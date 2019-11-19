import unittest

import numpy as np
import pandas as pd

from postreise.analyze.congestion import \
    calculate_congestion_surplus, map_demand_to_buses, map_pg_to_buses
from postreise.tests.mock_grid import MockGrid
from postreise.tests.mock_scenario import MockScenario

mock_plant = {
    'plant_id': ['A', 'B', 'C', 'D'],
    'bus_id': [1, 1, 2, 3],
    }
mock_bus = {
    'bus_id': [1, 2, 3],
    'Pd': [5, 6, 30],
    'zone_id': [1, 1, 1],
    }
grid_attrs = {'plant': mock_plant, 'bus': mock_bus}


class TestCalculateCongestionSurplus(unittest.TestCase):

    def _check_return(self, expected_return, surplus):
        self.assertIsInstance(surplus, pd.Series)
        msg = "Time series indices don't match"
        np.testing.assert_array_equal(
            surplus.index.to_numpy(), expected_return.index.to_numpy(), msg)
        msg = "Values don't match expected"
        np.testing.assert_array_equal(
            surplus.to_numpy(), expected_return.to_numpy(), msg)

    def test_calculate_congestion_surplus_single_time(self):
        demand = pd.DataFrame({'UTC': ['t1'], 1: [410]})
        lmp = pd.DataFrame({'UTC': ['t1'], 1: [7.5], 2: [11.25], 3: [10]})
        pg = pd.DataFrame(
            {'UTC': ['t1'], 'A': [50], 'B': [285], 'C': [0], 'D': [75]})
        for df in (demand, lmp, pg):
            df.set_index('UTC', inplace=True)
        mock_scenario = MockScenario(grid_attrs, demand=demand, lmp=lmp, pg=pg)

        expected_return = pd.Series(data=[787.5], index=['t1'])
        expected_return.rename_axis('UTC')

        surplus = calculate_congestion_surplus(mock_scenario)
        self._check_return(expected_return, surplus)

    def test_calculate_congestion_surplus_two_times(self):
        demand = pd.DataFrame({'UTC': ['t1', 't2'], 1: [410]*2})
        lmp = pd.DataFrame({
            'UTC': ['t1', 't2'],
            1: [7.5, 7.5], 2: [7.5, 11.25], 3: [7.5, 10]})
        pg = pd.DataFrame({
            'UTC': ['t1', 't2'],
            'A': [125, 50], 'B': [285, 285], 'C': [0, 0], 'D': [0, 75]})
        for df in (demand, lmp, pg):
            df.set_index('UTC', inplace=True)
        mock_scenario = MockScenario(grid_attrs, demand=demand, lmp=lmp, pg=pg)

        expected_return = pd.Series(data=[0, 787.5], index=['t1', 't2'])
        expected_return.rename_axis('UTC')

        surplus = calculate_congestion_surplus(mock_scenario)
        self._check_return(expected_return, surplus)


class TestMappingHelpers(unittest.TestCase):
    
    def _check_expected(self, test_return, expected_return, name):
        self.assertIsInstance(test_return, pd.DataFrame)
        msg = 'Index mismatch for ' + name
        np.testing.assert_array_equal(
            test_return.index, expected_return.index, msg)
        msg = 'Column mismatch for ' + name
        np.testing.assert_array_equal(
            test_return.columns, expected_return.columns, msg)
        msg = 'Values mismatch for ' + name
        np.testing.assert_array_almost_equal(
            test_return.to_numpy(), expected_return.to_numpy(), err_msg=msg)

    def test_map_demand_to_buses(self):
        grid = MockGrid(grid_attrs)
        demand = pd.DataFrame({'UTC': ['t1', 't2'], 1: [410]*2})
        demand.set_index('UTC', inplace=True)
        expected_return = pd.DataFrame({
            'UTC': ['t1', 't2'],
            1: [50]*2, 2: [60]*2, 3: [300]*2})
        expected_return.set_index('UTC', inplace=True)

        bus_demand = map_demand_to_buses(grid, demand)
        self._check_expected(bus_demand, expected_return, name='bus_demand')

    def test_map_pg_to_buses(self):
        grid = MockGrid(grid_attrs)
        pg = pd.DataFrame({
            'UTC': ['t1', 't2'],
            'A': [125, 50], 'B': [285, 285], 'C': [0, 0], 'D': [0, 75]})
        pg.set_index('UTC', inplace=True)
        expected_return = pd.DataFrame({
            'UTC': ['t1', 't2'],
            1: [410, 335], 2: [0, 0], 3: [0, 75]})
        expected_return.set_index('UTC', inplace=True)

        bus_pg = map_pg_to_buses(grid, pg)
        self._check_expected(bus_pg, expected_return, name='bus_pg')
