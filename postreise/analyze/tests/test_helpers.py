import unittest

from numpy.testing import assert_array_equal, assert_array_almost_equal
import pandas as pd

from powersimdata.tests.mock_grid import MockGrid
from postreise.analyze.helpers import (
    summarize_plant_to_bus,
    summarize_plant_to_location,
)

# plant_id is the index
mock_plant = {
    "plant_id": ["A", "B", "C", "D"],
    "bus_id": [1, 1, 2, 3],
    "lat": [47.6, 47.6, 37.8, 37.8],
    "lon": [122.3, 122.3, 122.4, 122.4],
}

# bus_id is the index
mock_bus = {
    "bus_id": [1, 2, 3, 4],
    "lat": [47.6, 37.8, 37.8, 40.7],
    "lon": [122.3, 122.4, 122.4, 74],
}

mock_pg = pd.DataFrame(
    {
        "A": [1, 2, 3, 4],
        "B": [1, 2, 4, 8],
        "C": [1, 1, 2, 3],
        "D": [1, 3, 5, 7],
    }
)

grid_attrs = {"plant": mock_plant, "bus": mock_bus}


def check_dataframe_matches(received_return, expected_return):
    assert isinstance(received_return, pd.DataFrame)
    assert_array_equal(
        received_return.index.to_numpy(), expected_return.index.to_numpy()
    )
    assert_array_equal(
        received_return.columns.to_numpy(), expected_return.columns.to_numpy()
    )
    assert_array_almost_equal(received_return.to_numpy(), expected_return.to_numpy())


class TestSummarizePlantToBus(unittest.TestCase):
    def setUp(self):
        self.grid = MockGrid(grid_attrs)

    def test_summarize_default(self):
        expected_return = pd.DataFrame(
            {
                1: [2, 4, 7, 12],
                2: [1, 1, 2, 3],
                3: [1, 3, 5, 7],
            }
        )
        bus_data = summarize_plant_to_bus(mock_pg, self.grid)
        check_dataframe_matches(bus_data, expected_return)

    def test_summarize_all_buses_false(self):
        expected_return = pd.DataFrame(
            {
                1: [2, 4, 7, 12],
                2: [1, 1, 2, 3],
                3: [1, 3, 5, 7],
            }
        )
        bus_data = summarize_plant_to_bus(mock_pg, self.grid, all_buses=False)
        check_dataframe_matches(bus_data, expected_return)

    def test_summarize_all_buses_true(self):
        expected_return = pd.DataFrame(
            {
                1: [2, 4, 7, 12],
                2: [1, 1, 2, 3],
                3: [1, 3, 5, 7],
                4: [0, 0, 0, 0],
            }
        )
        bus_data = summarize_plant_to_bus(mock_pg, self.grid, all_buses=True)
        check_dataframe_matches(bus_data, expected_return)


class TestSummarizePlantToLocation(unittest.TestCase):
    def setUp(self):
        self.grid = MockGrid(grid_attrs)

    def _check_dataframe_matches(self, loc_data, expected_return):
        self.assertIsInstance(loc_data, pd.DataFrame)
        assert_array_equal(loc_data.index.to_numpy(), expected_return.index.to_numpy())
        self.assertEqual(
            set(loc_data.columns.to_numpy()), set(expected_return.columns.to_numpy())
        )
        for c in loc_data.columns:
            assert_array_almost_equal(
                loc_data[c].to_numpy(), expected_return[c].to_numpy()
            )

    def test_summarize_location(self):
        expected_return = pd.DataFrame(
            {
                (47.6, 122.3): [2, 4, 7, 12],
                (37.8, 122.4): [2, 4, 7, 10],
            }
        )
        loc_data = summarize_plant_to_location(mock_pg, self.grid)
        self._check_dataframe_matches(loc_data, expected_return)
