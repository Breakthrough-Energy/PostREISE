import pandas as pd
from numpy.testing import assert_array_equal
from powersimdata.tests.mock_scenario import MockScenario

from postreise.analyze.demand import get_demand_time_series, get_net_demand_time_series

mock_plant = {
    "plant_id": ["1001", "1002", "1003"],
    "zone_name": ["Oregon", "Oregon", "Southern California"],
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
        201: [1, 2, 3, 4],
        202: [4, 3, 2, 1],
        203: [2, 2, 2, 2],
    }
)

scenario = MockScenario(grid_attrs, pg=mock_pg, demand=mock_demand)
scenario.state.grid.zone2id = {
    "Washington": 201,
    "Oregon": 202,
    "Northern California": 203,
}


def test_get_demand_time_series():
    demand = get_demand_time_series(scenario, "Washington")
    expected_results = [1, 2, 3, 4]
    assert_array_equal(demand.to_numpy(), expected_results)


def test_get_net_demand_time_series():
    net_demand = get_net_demand_time_series(scenario, "all")
    expected_results = [3, 3, 3, 3]
    assert_array_equal(net_demand.to_numpy(), expected_results)
