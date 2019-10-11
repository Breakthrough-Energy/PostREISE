import unittest
import pandas as pd

from postreise.analyze.test.carbon_mock import MockGrid, MockScenario
from postreise.analyze.carbon import generate_carbon_stats


class TestScalarMethods(unittest.TestCase):

    # check that gridmock is working correctly
    def test_mock_grid(self):
        grid = MockGrid(['plant'])
        self.assertTrue(isinstance(grid, object),
                        'GridMock should return an object')
        self.assertTrue(hasattr(grid, 'plant'),
                        'Plant property should be in the GridMock')
        self.assertFalse(hasattr(grid, 'branch'),
                         'Branch property should not be in the GridMock')

    def test_carbon_calculation(self):
        period_num = 3
        scenario = MockScenario(['plant', 'gencost'], period_num)
        grid = scenario.get_grid()

        carbon = generate_carbon_stats(scenario)

        self.assertTrue(isinstance(carbon, pd.DataFrame),
                        'generate_carbon_stats should return a data frame')
        carbon_from_wind = grid.plant[grid.plant.type == 'wind'].index.values
        self.assertEqual(carbon[carbon_from_wind[0]].sum(),0,
                         'Wind farm does not emit carbon')
        carbon_from_solar = grid.plant[grid.plant.type == 'solar'].index.values
        self.assertEqual(carbon[carbon_from_solar[0]].sum(), 0,
                         'Solar plant does not emit carbon')


if __name__ == '__main__':
    unittest.main()
