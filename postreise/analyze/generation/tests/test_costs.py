import pandas as pd
import pytest
from powersimdata.tests.mock_scenario import MockScenario

from postreise.analyze.generation.costs import calculate_costs


@pytest.fixture
def mock_gencost_data():
    # plant_id is the index
    return {
        "plant_id": [101, 102, 103, 104, 105],
        "type": [2] * 5,
        "startup": [0] * 5,
        "shutdown": [0] * 5,
        "n": [3] * 5,
        "c2": [1, 2, 3, 4, 5],
        "c1": [10, 20, 30, 40, 50],
        "c0": [100, 200, 300, 400, 500],
        "interconnect": ["Western"] * 5,
    }


@pytest.fixture
def mock_gencost(mock_gencost_data):
    # Reproducing manually what would be done inside MockGrid
    return pd.DataFrame(mock_gencost_data).set_index("plant_id")


@pytest.fixture
def mock_plant():
    # plant_id is the index
    return {
        "plant_id": [101, 102, 103, 104, 105],
        "bus_id": [1001, 1002, 1003, 1004, 1005],
        "type": ["solar", "wind", "ng", "coal", "dfo"],
        "GenFuelCost": [0, 0, 3.3, 4.4, 5.5],
    }


@pytest.fixture
def mock_pg(mock_plant):
    return pd.DataFrame(
        {
            plant_id: [(i + 1) * p for p in range(4)]
            for i, plant_id in enumerate(mock_plant["plant_id"])
        },
        index=pd.date_range("2019-01-01", periods=4, freq="H"),
    )


@pytest.fixture
def mock_scenario(mock_gencost_data, mock_pg):
    return MockScenario(grid_attrs={"gencost_before": mock_gencost_data}, pg=mock_pg)


def test_calculate_cost_equal_both_methods(mock_gencost, mock_pg, mock_scenario):
    scenario_calculated = calculate_costs(scenario=mock_scenario)
    gencost_pg_calculated = calculate_costs(gencost=mock_gencost, pg=mock_pg)
    assert scenario_calculated.equals(gencost_pg_calculated)


def test_pass_nothing():
    with pytest.raises(ValueError):
        calculate_costs()


def test_pass_just_pg(mock_pg):
    with pytest.raises(ValueError):
        calculate_costs(pg=mock_pg)


def test_pass_just_gencost(mock_gencost):
    with pytest.raises(ValueError):
        calculate_costs(gencost=mock_gencost)


def test_pass_too_many_things(mock_gencost, mock_pg, mock_scenario):
    with pytest.raises(ValueError):
        calculate_costs(gencost=mock_gencost, pg=mock_pg, scenario=mock_scenario)
