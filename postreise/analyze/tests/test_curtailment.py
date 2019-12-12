import unittest

import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal
import pandas as pd

from postreise.tests.mock_scenario import MockScenario
from postreise.analyze.curtailment import \
    calculate_curtailment_time_series, calculate_curtailment_percentage, \
    summarize_curtailment_by_bus, summarize_curtailment_by_location


# plant_id is the index
mock_plant = {
    'plant_id': ['A', 'B', 'C', 'D'],
    'bus_id': [1, 1, 2, 3],
    'lat': [47.6, 47.6, 37.8, 37.8],
    'lon': [122.3, 122.3, 122.4, 122.4],
    'type': ['solar', 'solar', 'wind', 'wind']
    }

mock_pg = pd.DataFrame({
    'A': [1, 2, 3, 3],
    'B': [1, 2, 3.5, 6],
    'C': [1, 1, 2, 2.5],
    'D': [1, 3, 4, 5.5],
    })

mock_solar = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': [1, 2, 4, 8],
    })

mock_wind = pd.DataFrame({
    'C': [1, 1, 2, 3],
    'D': [1, 3, 5, 7],
    })

mock_curtailment_data = pd.DataFrame({
    'A': [0, 0, 0, 1],
    'B': [0, 0, 0.5, 2],
    'C': [0, 0, 0, 0.5],
    'D': [0, 0, 1, 1.5],
    })

mock_curtailment = {
    'solar': mock_curtailment_data[['A', 'B']],
    'wind': mock_curtailment_data[['C', 'D']],
    }

grid_attrs = {'plant': mock_plant}
scenario = MockScenario(
    grid_attrs, pg=mock_pg, solar=mock_solar, wind=mock_wind)

class TestCalculateCurtailmentTimeSeries(unittest.TestCase):

    def _check_curtailment_vs_expected(self, curtailment, expected):
        self.assertIsInstance(curtailment, dict)
        self.assertEqual(curtailment.keys(), expected.keys())
        for key in curtailment.keys():
            self.assertIsInstance(curtailment[key], pd.DataFrame)
        assert_array_equal(curtailment[key].index.to_numpy(),
                           expected[key].index.to_numpy())
        assert_array_equal(curtailment[key].columns.to_numpy(),
                           expected[key].columns.to_numpy())
        assert_array_equal(curtailment[key].to_numpy(),
                           expected[key].to_numpy())

    def test_calculate_curtailment_time_series_solar(self):
        expected_return = {'solar': mock_curtailment['solar']}
        curtailment = calculate_curtailment_time_series(
            scenario, resources=('solar',))
        self._check_curtailment_vs_expected(curtailment, expected_return)

    def test_calculate_curtailment_time_series_wind(self):
        expected_return = {'wind': mock_curtailment['wind']}
        curtailment = calculate_curtailment_time_series(
            scenario, resources=('wind',))
        self._check_curtailment_vs_expected(curtailment, expected_return)

    def test_calculate_curtailment_time_series_default(self):
        expected_return = mock_curtailment
        curtailment = calculate_curtailment_time_series(scenario)
        self._check_curtailment_vs_expected(curtailment, expected_return)

    def test_calculate_curtailment_time_series_solar_wind(self):
        expected_return = mock_curtailment
        curtailment = calculate_curtailment_time_series(
            scenario, resources=('solar', 'wind',))
        self._check_curtailment_vs_expected(curtailment, expected_return)


class TestCheckResourceInScenario(unittest.TestCase):

    def test_error_geothermal_curtailment(self):
        with self.assertRaises(ValueError):
            curtailment = calculate_curtailment_time_series(
                scenario, resources=('geothermal',))

    def test_error_no_solar(self):
        no_solar_mock_plant = {
            'plant_id': ['C', 'D'],
            'type': ['wind', 'wind']
            }
        no_solar_grid_attrs = {'plant': no_solar_mock_plant}
        no_solar_scenario = MockScenario(no_solar_grid_attrs)
        with self.assertRaises(ValueError):
            curtailment = calculate_curtailment_time_series(
                no_solar_scenario, resources=('solar',))


class TestCalculateCurtailmentPercentage(unittest.TestCase):

    def test_calculate_curtailment_percentage_solar(self):
        expected_return = 3.5 / 25
        total_curtailment = calculate_curtailment_percentage(
            scenario, resources=('solar',))
        self.assertAlmostEqual(total_curtailment, expected_return)

    def test_calculate_curtailment_percentage_wind(self):
        expected_return = 3 / 23
        total_curtailment = calculate_curtailment_percentage(
            scenario, resources=('wind',))
        self.assertAlmostEqual(total_curtailment, expected_return)

    def test_calculate_curtailment_percentage_default(self):
        expected_return = 6.5 / 48
        total_curtailment = calculate_curtailment_percentage(scenario)
        self.assertAlmostEqual(total_curtailment, expected_return)

    def test_calculate_curtailment_percentage_solar_wind(self):
        expected_return = 6.5 / 48
        total_curtailment = calculate_curtailment_percentage(
            scenario, resources=('solar', 'wind'))
        self.assertAlmostEqual(total_curtailment, expected_return)


class TestSummarizeCurtailmentByBus(unittest.TestCase):

    def test_summarize_curtailment_by_bus(self):
        grid = scenario.state.get_grid()
        expected_return = {
            'solar': {1: 3.5},
            'wind': {2: 0.5, 3: 2.5},
            }
        bus_curtailment = summarize_curtailment_by_bus(mock_curtailment, grid)
        self.assertEqual(bus_curtailment, expected_return)

class TestSummarizeCurtailmentByLocation(unittest.TestCase):

    def test_summarize_curtailment_by_location(self):
        grid = scenario.state.get_grid()
        expected_return = {
            'solar': {(47.6, 122.3): 3.5},
            'wind': {(37.8, 122.4): 3},
            }
        location_curtailment = summarize_curtailment_by_location(
            mock_curtailment, grid)
        self.assertEqual(location_curtailment, expected_return)