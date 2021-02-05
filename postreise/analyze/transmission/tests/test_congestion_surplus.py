import numpy as np
import pandas as pd
from powersimdata.input.input_data import InputData
from powersimdata.tests.mock_scenario import MockScenario

from postreise.analyze.transmission import congestion

mock_plant = {
    "plant_id": ["A", "B", "C", "D"],
    "bus_id": [1, 1, 2, 3],
}
mock_bus = {
    "bus_id": [1, 2, 3, 4],
    "Pd": [5, 6, 30, 1],
    "zone_id": [1, 1, 1, 2],
}
grid_attrs = {"plant": mock_plant, "bus": mock_bus}


def _check_return(expected_return, surplus):
    assert isinstance(surplus, pd.Series)
    msg = "Time series indices don't match"
    np.testing.assert_array_equal(
        surplus.index.to_numpy(), expected_return.index.to_numpy(), msg
    )
    msg = "Values don't match expected"
    np.testing.assert_array_equal(surplus.to_numpy(), expected_return.to_numpy(), msg)


def test_calculate_congestion_surplus_single_time(monkeypatch):
    """Congested case from Kirschen & Strbac Section 5.3.2.4"""

    def mock_get_data(*args, **kwargs):
        return demand

    # Override default InputData.get_data method to avoid profile csv lookup
    monkeypatch.setattr(InputData, "get_data", mock_get_data)

    demand = pd.DataFrame({"UTC": ["t1"], 1: [410], 2: [0]})
    lmp = pd.DataFrame({"UTC": ["t1"], 1: [7.5], 2: [11.25], 3: [10], 4: [0]})
    pg = pd.DataFrame({"UTC": ["t1"], "A": [50], "B": [285], "C": [0], "D": [75]})
    for df in (demand, lmp, pg):
        df.set_index("UTC", inplace=True)
    mock_scenario = MockScenario(grid_attrs, demand=demand, lmp=lmp, pg=pg)

    expected_return = pd.Series(
        data=[787.5],
        index=pd.date_range(start="2016-01-01", periods=1, freq="H"),
    )
    expected_return.rename_axis("UTC")

    surplus = congestion.calculate_congestion_surplus(mock_scenario)
    _check_return(expected_return, surplus)


def test_calculate_congestion_surplus_three_times(monkeypatch):
    """First: congested. Second: uncongested. Third: uncongested, fuzzy."""

    def mock_get_data(*args, **kwargs):
        return demand

    # Override default InputData.get_data method to avoid profile csv lookup
    monkeypatch.setattr(InputData, "get_data", mock_get_data)

    time_indices = ["t1", "t2", "t3"]
    demand = pd.DataFrame({"UTC": time_indices, 1: [410] * 3, 2: [0] * 3})
    lmp = pd.DataFrame(
        {
            "UTC": time_indices,
            1: [7.5, 7.5, 7.5],
            2: [11.25, 7.5, 7.5],
            3: [10, 7.5, 7.49],
            4: [0, 0, 0],
        }
    )
    pg = pd.DataFrame(
        {
            "UTC": time_indices,
            "A": [50, 125, 125],
            "B": [285] * 3,
            "C": [0] * 3,
            "D": [75, 0, 0],
        }
    )
    for df in (demand, lmp, pg):
        df.set_index("UTC", inplace=True)
    mock_scenario = MockScenario(grid_attrs, demand=demand, lmp=lmp, pg=pg)

    expected_return = pd.Series(
        data=[787.5, 0, 0],
        index=pd.date_range(start="2016-01-01", periods=3, freq="H"),
    )
    expected_return.rename_axis("UTC")

    surplus = congestion.calculate_congestion_surplus(mock_scenario)
    _check_return(expected_return, surplus)
