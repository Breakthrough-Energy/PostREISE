import pandas as pd
from numpy.testing import assert_array_equal
from powersimdata.tests.mock_scenario import MockScenario

from postreise.analyze.demand import (
    get_demand_time_series,
    get_net_demand_time_series,
)

mock_plant = {
    "plant_id": ["1001", "1002", "1003"],
    "zone_name": ["B", "B", "C"],
    "type": ["solar", "wind", "hydro"],
}

mock_pg = pd.DataFrame(
    {
        "1001": [0, 1, 3, 2],
        "1002": [4, 3, 1, 2],
        "1003": [3, 3, 3, 3],
    }
)

grid_attrs = {"plant": mock_plant}

mock_demand = pd.DataFrame(
    {
        101: [1, 2, 3, 4],
        102: [4, 3, 2, 1],
        103: [2, 2, 2, 2],
    }
)

scenario = MockScenario(grid_attrs, pg=mock_pg, demand=mock_demand)
scenario.state.grid.zone2id = {
    "A": 101,
    "B": 102,
    "C": 103,
}


def test_get_demand_time_series():
    demand = get_demand_time_series(scenario, "A")
    expected_results = [1, 2, 3, 4]
    assert_array_equal(demand.to_numpy(), expected_results)


def test_get_net_demand_time_series():
    net_demand = get_net_demand_time_series(scenario, "all")
    expected_results = [3, 3, 3, 3]
    assert_array_equal(net_demand.to_numpy(), expected_results)
