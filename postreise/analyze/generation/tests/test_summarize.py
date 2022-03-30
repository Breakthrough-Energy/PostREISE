import pathlib
import unittest

import pandas as pd
import pytest
from numpy.testing import assert_array_almost_equal
from powersimdata.input.tests.test_helpers import check_dataframe_matches
from powersimdata.tests.mock_scenario import MockScenario

from postreise.analyze.generation.summarize import (
    get_generation_time_series_by_resources,
    get_storage_time_series,
    sum_generation_by_state,
    sum_generation_by_type_zone,
    summarize_hist_gen,
)

# plant_id is the index
mock_plant = {
    "plant_id": ["A", "B", "C", "D"],
    "zone_id": [201, 202, 203, 204],
    "type": ["solar", "wind", "hydro", "hydro"],
    "zone_name": ["Washington", "Oregon", "Northern California", "Bay Area"],
}

# bus_id is the index
mock_bus = {
    "bus_id": [1, 2, 3, 4],
    "zone_id": [201, 202, 203, 204],
}

mock_storage = {
    "bus_id": [1, 2, 3],
    "Pmax": [10, 10, 10],
}

mock_pg = pd.DataFrame(
    {
        "A": [1, 2, 3, 4],
        "B": [1, 2, 4, 8],
        "C": [1, 1, 2, 3],
        "D": [1, 3, 5, 7],
    },
    index=pd.date_range(start="2016-01-01", periods=4, freq="H"),
)

mock_storage_pg = pd.DataFrame(
    {
        0: [1, 1, 1],
        1: [0, 1, 2],
        2: [2, 2, 2],
    }
)

grid_attrs = {"plant": mock_plant, "bus": mock_bus, "storage_gen": mock_storage}
scenario = MockScenario(grid_attrs, pg=mock_pg, storage_pg=mock_storage_pg)
scenario.state.grid.id2zone = {
    k: v for k, v in zip(mock_plant["zone_id"], mock_plant["zone_name"])
}
scenario.state.grid.zone2id = {v: k for k, v in scenario.state.grid.id2zone.items()}


class TestSumGenerationByTypeZone(unittest.TestCase):
    def setUp(self):
        self.scenario = MockScenario(grid_attrs, pg=mock_pg)

    def test_sum_generation(self):
        expected_return = pd.DataFrame(
            {
                "type": ["hydro", "solar", "wind"],
                201: [0, 10, 0],
                202: [0, 0, 15],
                203: [7, 0, 0],
                204: [16, 0, 0],
            }
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

    def test_with_time_change(self):
        summed_generation = sum_generation_by_type_zone(
            self.scenario,
            time_zone="ETC/GMT+6",
        )
        expected_return = pd.DataFrame(
            {
                "type": ["hydro", "solar", "wind"],
                201: [0, 10, 0],
                202: [0, 0, 15],
                203: [7, 0, 0],
                204: [16, 0, 0],
            }
        )
        expected_return.set_index("type", inplace=True)
        check_dataframe_matches(summed_generation, expected_return)

    def test_with_time_slice(self):
        summed_generation = sum_generation_by_type_zone(
            self.scenario,
            time_range=[pd.Timestamp(2016, 1, 1, 1), pd.Timestamp(2016, 1, 1, 2)],
        )
        expected_return = pd.DataFrame(
            {
                "type": ["hydro", "solar", "wind"],
                201: [0, 5, 0],
                202: [0, 0, 6],
                203: [3, 0, 0],
                204: [8, 0, 0],
            }
        )
        expected_return.set_index("type", inplace=True)
        check_dataframe_matches(summed_generation, expected_return)

    def test_with_time_change_and_time_slice(self):
        summed_generation = sum_generation_by_type_zone(
            self.scenario,
            time_zone="ETC/GMT+1",
            time_range=[
                pd.Timestamp("2016-01-01-00", tz="ETC/GMT+1"),
                pd.Timestamp("2016-01-01-02", tz="ETC/GMT+1"),
            ],
        )
        expected_return = pd.DataFrame(
            {
                "type": ["hydro", "solar", "wind"],
                201: [0, 9, 0],
                202: [0, 0, 14],
                203: [6, 0, 0],
                204: [15, 0, 0],
            }
        )
        expected_return.set_index("type", inplace=True)
        check_dataframe_matches(summed_generation, expected_return)


@pytest.fixture
def sim_gen_result():
    return sum_generation_by_state(scenario)


@pytest.fixture
def hist_gen_raw():
    # raw_hist_gen_csv = "usa_hist_gen.csv"
    # path_to_csv = pathlib.Path(__file__).parent.joinpath(raw_hist_gen_csv)

    path_to_csv = pathlib.Path(__file__).parent.joinpath(
        "..", "..", "..", "data", "2016_Historical_USA_TAMU_Generation_GWh.csv"
    )

    hist_gen_raw = pd.read_csv(path_to_csv, index_col=0).T
    return hist_gen_raw


def test_sum_generation_by_state_shape(sim_gen_result):
    assert (5, 3) == sim_gen_result.shape
    assert "all" in sim_gen_result.index
    assert "Western" in sim_gen_result.index


def test_sum_generation_by_state_values_scaled(sim_gen_result):
    expected_return = pd.DataFrame(
        {
            "hydro": [0.023, 0, 0, 0.023, 0.023],
            "solar": [0, 0, 0.01, 0.01, 0.01],
            "wind": [0, 0.015, 0, 0.015, 0.015],
        },
        index=["California", "Oregon", "Washington", "Western", "all"],
    )
    check_dataframe_matches(sim_gen_result, expected_return)


def test_summarize_hist_gen_include_areas(hist_gen_raw):
    all_resources = ["wind", "hydro", "coal"]
    actual_hist_gen = summarize_hist_gen(hist_gen_raw, all_resources)
    for area in (
        "Western interconnection",
        "Eastern interconnection",
        "Texas interconnection",
        "Montana",
        "New Mexico",
        "All",
    ):
        assert area in actual_hist_gen.index


def test_summarize_hist_gen_shape(hist_gen_raw):
    all_resources = ["wind", "hydro", "coal"]
    actual_hist_gen = summarize_hist_gen(hist_gen_raw, all_resources)
    # 48 contiguous, 3 interconnections and total
    assert (52, 3) == actual_hist_gen.shape


def test_get_generation_time_series_by_resources():
    arg = [(scenario, "Washington", "solar"), (scenario, "Oregon", "wind")]
    expected = [
        pd.DataFrame({"solar": mock_pg["A"]}),
        pd.DataFrame({"wind": mock_pg[["B"]].sum(axis=1)}),
    ]
    for a, e in zip(arg, expected):
        check_dataframe_matches(get_generation_time_series_by_resources(*a), e)


def test_get_storage_time_series():
    arg = [(scenario, "Washington"), (scenario, "all")]
    expected = [mock_storage_pg[0], mock_storage_pg.sum(axis=1)]
    for a, e in zip(arg, expected):
        assert_array_almost_equal(get_storage_time_series(*a), e)
