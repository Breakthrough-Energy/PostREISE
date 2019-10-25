import unittest

import numpy as np
from numpy.testing import assert_array_almost_equal
import pandas as pd

from tests.mocks import MockScenario
from postreise.analyze.carbon import generate_carbon_stats
from postreise.analyze.carbon import summarize_carbon_by_bus

# plant_id is the index
mock_plant = {
    'plant_id': [101, 102, 103, 104, 105],
    'bus_id': [1001, 1002, 1003, 1004, 1005],
    'type': ['solar', 'wind', 'ng', 'coal', 'dfo'],
    'zone_id': [1, 2, 3, 1, 3],
    'GenMWMax': [200, 150, 100, 300, 120],
    'GenFuelCost': [0, 0, 3.3, 4.4, 5.5],
    'Pmin': [20, 30, 25, 100, 20],
    'Pmax': [40, 80, 50, 150, 80],
    }

# branch_id is the index
mock_branch = {
    'branch_id': [11, 12, 13, 14, 15],
    'from_zone_id': [1, 2, 3, 1, 3],
    'to_zone_id': [1, 3, 2, 2, 3],
    'rateA': [10, 20, 30, 40, 50],
    'x': [0.1, 0.2, 0.3, 0.4, 0.5],
    }

# dcline_id is the index
mock_dcline = {
    'dcline_id': [101, 102, 103, 104, 105],
    'status': [1, 1, 1, 1, 1],
    'Pmax': [100, 200, 300, 400, 500],
    }

# plant_id is the index
mock_gencost = {
    'plant_id': [101, 102, 103, 104, 105],
    'type': [2] * 5,
    'startup': [0] * 5,
    'shutdown': [0] * 5,
    'n': [3] * 5,
    'c2': [1, 2, 3, 4, 5],
    'c1': [10, 20, 30, 40, 50],
    'c0': [100, 200, 300, 400, 500],
    'interconnect': ['Western'] * 5,
    }


class TestCarbonCalculation(unittest.TestCase):

    def setUp(self):
        def _test_carbon_structure(carbon):
            pg = self.pg
            plant = self.grid.plant

            # check data frame structure
            err_msg = 'generate_carbon_stats should return a data frame'
            self.assertTrue(isinstance(carbon, pd.DataFrame), err_msg)
            err_msg = 'carbon and pg should have same index'
            for a, b in zip(pg.index.to_numpy(), carbon.index.to_numpy()):
                self.assertEqual(a, b, err_msg)
            err_msg = 'carbon and pg should have same columns'
            for a, b in zip(pg.columns.to_numpy(), carbon.columns.to_numpy()):
                self.assertEqual(a, b, err_msg)

            # sanity check values
            carbon_from_wind = plant[plant.type == 'wind'].index.values
            err_msg = 'Wind farm does not emit carbon'
            self.assertEqual(carbon[carbon_from_wind[0]].sum(), 0, err_msg)
            carbon_from_solar = plant[plant.type == 'solar'].index.values
            err_msg = 'Solar plant does not emit carbon'
            self.assertEqual(carbon[carbon_from_solar[0]].sum(), 0, err_msg)
            negative_carbon_count = np.sum((carbon < 0).to_numpy().ravel())
            err_msg = 'No plant should emit negative carbon'
            self.assertEqual(negative_carbon_count, 0, err_msg)

        self._test_carbon_structure = _test_carbon_structure
        self.period_num = 4
        self.mock_pg = pd.DataFrame({
            plant_id: [(i+1)*p for p in range(self.period_num)]
            for i, plant_id in enumerate(mock_plant['plant_id'])})
        self.scenario = MockScenario(
            grid_attrs={'plant': mock_plant, 'gencost': mock_gencost},
            pg=self.mock_pg)
        self.pg = self.scenario.get_pg()
        self.grid = self.scenario.get_grid()

    def test_carbon_calc_always_on(self):

        carbon = generate_carbon_stats(self.scenario, method='always-on')
        self._test_carbon_structure(carbon)

        # check specific values
        expected_values = np.array([
            [0, 0, 4.82, 8.683333, 6.77],
            [0, 0, 6.6998, 13.546000, 11.8475],
            [0, 0, 9.4472, 21.1873333, 20.3100],
            [0, 0, 13.0622, 31.6073333, 32.1575],
            ])
        assert_array_almost_equal(expected_values, carbon.to_numpy(),
                                  err_msg='Values do not match expected')

    def test_carbon_calc_decommit(self):

        carbon = generate_carbon_stats(self.scenario, method='decommit')
        self._test_carbon_structure(carbon)

        # check specific values
        expected_values = np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 6.6998, 13.546000, 11.8475],
            [0, 0, 9.4472, 21.1873333, 20.3100],
            [0, 0, 13.0622, 31.6073333, 32.1575],
            ])
        assert_array_almost_equal(expected_values, carbon.to_numpy(),
                                  err_msg='Values do not match expected')

    def test_carbon_calc_simple(self):

        carbon = generate_carbon_stats(self.scenario, method='simple')
        self._test_carbon_structure(carbon)

        # check specific values
        expected_values = np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 1.407, 4.004, 4.2],
            [0, 0, 2.814, 8.008, 8.4],
            [0, 0, 4.221, 12.012, 12.6],
            ])
        assert_array_almost_equal(expected_values, carbon.to_numpy(),
                                  err_msg='Values do not match expected')


class TestCarbonSummarization(unittest.TestCase):

    def setUp(self):
        self.period_num = 3
        self.fossil_fuels = {'coal', 'dfo', 'ng'}
        self.pg = pd.DataFrame({
            plant_id: [(i+1)*p for p in range(self.period_num)]
            for i, plant_id in enumerate(mock_plant['plant_id'])})
        self.plant = pd.DataFrame(mock_plant)
        self.plant.set_index('plant_id', inplace=True)

    def test_carbon_summarization(self):
        # setup
        pg = self.pg
        plant = self.plant
        input_carbon_values = [
            [0, 0, 6.6998, 13.546000, 11.8475],
            [0, 0, 9.4472, 21.1873333, 20.3100],
            [0, 0, 13.0622, 31.6073333, 32.1575],
            ]
        input_carbon = pd.DataFrame(
            input_carbon_values, index=pg.index, columns=pg.columns)
        expected_sum = {
            'coal': {1004: 66.3406666},
            'ng': {1003: 29.2092},
            'dfo': {1005: 64.315},
            }

        # calculation
        summation = summarize_carbon_by_bus(input_carbon, plant)

        # checks
        err_msg = 'summarize_carbon_by_bus didn\'t return a dict'
        self.assertTrue(isinstance(summation, dict), err_msg)
        err_msg = 'summarize_carbon_by_bus didn\'t return the right dict keys'
        self.assertEqual(set(summation.keys()), self.fossil_fuels, err_msg)
        for k in expected_sum.keys():
            err_msg = 'summation not correct for fuel ' + k
            self.assertEqual(
                expected_sum[k].keys(), summation[k].keys(), err_msg)
            for bus in expected_sum[k]:
                err_msg = 'summation not correct for bus ' + str(bus)
                self.assertAlmostEqual(
                    expected_sum[k][bus], summation[k][bus], msg=err_msg)


if __name__ == '__main__':
    unittest.main()
