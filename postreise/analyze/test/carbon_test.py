import unittest
from postreise.analyze.CarbonMocks import *
from postreise.analyze.carbon import generate_carbon_stats


class TestScalarMethods(unittest.TestCase):

    # check that gridmock is working correctly
    def test_gridmock_creates_grid(self):
        grid = GridMock('plant')
        self.assertTrue(isinstance(grid, object), 'GridMock should return an object')
        self.assertTrue(hasattr(grid, 'plant'), 'Plant property should be in the GridMock')
        self.assertFalse(hasattr(grid, 'branch'), 'Branch property should not be in the GridMock')

    def test_carbon_calculation(self):
        periodNum = 3
        grid = GridMock(['plant','gencost'])
        pg = MockPG(periodNum)

        carbon = generate_carbon_stats(pg, grid)

        self.assertTrue(isinstance(carbon, pd.DataFrame), 'generate_carbon_stats should return a data frame')
        self.assertEqual(carbon.sum().sum(), 96.2799, 'Total emissio should be 96.2799')
        self.assertEqual(carbon[grid.plant[grid.plant.type == 'wind'].index.values[0]].sum(), 0, 'Wind farm does not emit carbon')
        self.assertEqual(carbon[grid.plant[grid.plant.type == 'solar'].index.values[0]].sum(), 0, 'Solar plant does not emit carbon')

if __name__ == '__main__':
    unittest.main()
