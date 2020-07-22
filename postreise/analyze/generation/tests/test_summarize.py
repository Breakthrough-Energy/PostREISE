import unittest
import pytest
import pandas as pd
import pathlib

from powersimdata.tests.mock_scenario import MockScenario
from powersimdata.tests.mock_scenario_info import MockScenarioInfo
from powersimdata.tests.mock_grid import MockGrid
from postreise.analyze.tests.test_helpers import check_dataframe_matches
from postreise.analyze.generation.summarize import (
    sum_generation_by_type_zone,
    sum_generation_by_state,
    summarize_hist_gen,
)

# plant_id is the index
mock_plant = {
    "plant_id": ["A", "B", "C", "D"],
    "zone_id": [1, 1, 2, 2],
    "type": ["solar", "wind", "hydro", "hydro"],
}

mock_pg = pd.DataFrame(
    {"A": [1, 2, 3, 4], "B": [1, 2, 4, 8], "C": [1, 1, 2, 3], "D": [1, 3, 5, 7],}
)

grid_attrs = {"plant": mock_plant}


class TestSumGenerationByTypeZone(unittest.TestCase):
    def setUp(self):
        self.scenario = MockScenario(grid_attrs, pg=mock_pg)

    def test_sum_generation(self):
        expected_return = pd.DataFrame(
            {"type": ["hydro", "solar", "wind"], 1: [0, 10, 15], 2: [23, 0, 0]}
        )
        expected_return.set_index("type", inplace=True)
        summed_generation = sum_generation_by_type_zone(self.scenario)
        check_dataframe_matches(summed_generation, expected_return)

    def test_with_string(self):
        with self.assertRaises(TypeError):
            sum_generation_by_type_zone("scenario_number")

    def test_with_scenario_not_analyze(self):
        test_scenario = MockScenario(grid_attrs, pg=mock_pg)
        test_scenario.state = "Create"
        with self.assertRaises(ValueError):
            sum_generation_by_type_zone(test_scenario)


@pytest.fixture
def sim_gen_result(monkeypatch):
    mock_resource = lambda x: ["ng", "hydro", "wind"]
    interconnect = ["Western"]
    s_info = MockScenarioInfo()
    s_info.grid.interconnect = interconnect
    monkeypatch.setattr(s_info, "get_available_resource", mock_resource)
    return sum_generation_by_state(s_info)


@pytest.fixture
def hist_gen_raw():
    raw_hist_gen_csv = "usa_hist_gen.csv"
    path_to_csv = pathlib.Path(__file__).parent.joinpath(raw_hist_gen_csv)
    hist_gen_raw = pd.read_csv(path_to_csv, index_col=0)
    return hist_gen_raw


def test_sum_generation_by_state_shape(sim_gen_result):
    assert (13, 3) == sim_gen_result.shape
    assert "all" in sim_gen_result.index
    assert "Western" in sim_gen_result.index


def test_sum_generation_by_state_values_scaled(sim_gen_result):
    assert all(sim_gen_result == 42 / 1000)


def test_summarize_hist_gen_include_areas(hist_gen_raw):
    all_resources = ["wind", "hydro", "coal"]
    actual_hist_gen = summarize_hist_gen(hist_gen_raw, all_resources)
    for area in ("Western", "Eastern", "Texas", "Montana", "all"):
        assert area in actual_hist_gen.index


def test_summarize_hist_gen_shape(hist_gen_raw):
    all_resources = ["wind", "hydro", "coal"]
    actual_hist_gen = summarize_hist_gen(hist_gen_raw, all_resources)
    assert (8, 3) == actual_hist_gen.shape
