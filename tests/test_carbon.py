import unittest

import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal
import pandas as pd

# context.py ensures that we always import from the current postreise folder.
from context import postreise
from mock_carbon import MockGrid, MockScenario
from postreise.analyze.carbon import generate_carbon_stats

class TestMocks(unittest.TestCase):

    # check that gridmock is working correctly
    def test_mock_grid(self):
        grid = MockGrid(['plant'])
        self.assertTrue(isinstance(grid, object),
                        'GridMock should return an object')
        self.assertTrue(hasattr(grid, 'plant'),
                        'Plant property should be in the GridMock')
        self.assertFalse(hasattr(grid, 'branch'),
                         'Branch property should not be in the GridMock')

    def test_mockpg_created_properly(self):
        period_num = 4
        grid = MockGrid(['plant'])
        scenario = MockScenario(['plant', 'gencost'], period_num)
        pg = scenario.get_pg()
        err_msg = 'MockPG should have dimension (periodNum * len(plant))'
        self.assertEqual(pg.shape, (period_num, grid.plant.shape[0]), err_msg)

class TestCarbonCalculation(unittest.TestCase):

    def test_carbon_calculation(self):
        period_num = 3
        scenario = MockScenario(['plant', 'gencost'], period_num)
        grid = scenario.get_grid()
        pg = scenario.get_pg()

        carbon = generate_carbon_stats(scenario)

        # check data frame structure
        err_msg = 'generate_carbon_stats should return a data frame'
        self.assertTrue(isinstance(carbon, pd.DataFrame), err_msg)
        err_msg = 'carbon and pg should have same index'
        for a, b in (zip(pg.index.to_numpy(), carbon.index.to_numpy())):
            self.assertEqual(a, b, err_msg)
        err_msg = 'carbon and pg should have same columns'
        for a, b in (zip(pg.columns.to_numpy(), carbon.columns.to_numpy())):
            self.assertEqual(a, b, err_msg)

        # sanity check values
        carbon_from_wind = grid.plant[grid.plant.type == 'wind'].index.values
        err_msg = 'Wind farm does not emit carbon'
        self.assertEqual(carbon[carbon_from_wind[0]].sum(), 0, err_msg)
        carbon_from_solar = grid.plant[grid.plant.type == 'solar'].index.values
        err_msg = 'Solar plant does not emit carbon'
        self.assertEqual(carbon[carbon_from_solar[0]].sum(), 0, err_msg)
        negative_carbon_count = np.sum((carbon < 0).to_numpy().ravel())
        err_msg = 'No plant should emit negative carbon'
        self.assertEqual(negative_carbon_count, 0, err_msg)

        #check specific values
        expected_values = [
            [0, 0, 6.6998, 13.546000, 11.8475],
            [0, 0, 9.4472, 21.1873333, 20.3100],
            [0, 0, 13.0622, 31.6073333, 32.1575]
            ]
        err_msg = 'Values do not match expected'
        for i, t in enumerate(pg.index):
            for j, p in enumerate(pg.columns):
                self.assertAlmostEqual(
                    carbon.iloc[i,j], expected_values[i][j], msg=err_msg)

if __name__ == '__main__':
    unittest.main()
