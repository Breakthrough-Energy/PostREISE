import unittest

import pandas as pd

from postreise.tests.mock_scenario import MockScenario
from postreise.tests.mock_grid import MockGrid

# plant_id is the index
mock_plant = {
    'plant_id': [101, 102, 103, 104, 105],
    'bus_id': [1001, 1002, 1003, 1004, 1005],
    'type': ['solar', 'wind', 'ng', 'coal', 'dfo'],
    'zone_id': [1, 2, 3, 1, 3],
    'Pmax': [200, 150, 100, 300, 120],
    'GenFuelCost': [0, 0, 3.3, 4.4, 5.5],
    'Pmin': [20, 30, 25, 100, 20],
    'Pmax': [40, 80, 50, 150, 80],
    }


class TestMocks(unittest.TestCase):

    def setUp(self):
        self.period_num = 4
        self.mock_pg = pd.DataFrame({
            plant_id: [(i+1)*p for p in range(self.period_num)]
            for i, plant_id in enumerate(mock_plant['plant_id'])})
        self.mock_pg.set_index(pd.date_range(
            start='2016-01-01', periods=self.period_num, freq='H'),
            inplace=True)
        self.mock_pg.index.name = 'UTC'
    
    # check that MockGrid is working correctly
    def test_mock_grid_successes(self):
        grid = MockGrid(grid_attrs={'plant': mock_plant})
        self.assertTrue(isinstance(grid, object),
                        'MockGrid should return an object')
        self.assertTrue(hasattr(grid, 'plant'),
                        'Plant property should be in the MockGrid')
        self.assertEqual(len(grid.branch), 0, 
                         'Branch dataframe should be empty in the MockGrid')
    
    def test_mock_grid_failures(self):
        with self.assertRaises(TypeError):
            grid = MockGrid(grid_attrs='foo')
        with self.assertRaises(TypeError):
            grid = MockGrid(grid_attrs={1: 'foo'})
        with self.assertRaises(ValueError):
            grid = MockGrid(grid_attrs={'foo': 'bar'})

    def test_mockpg_stored_properly(self):
        scenario = MockScenario(
            grid_attrs={'plant': mock_plant},
            pg=self.mock_pg)
        pg = scenario.state.get_pg()
        err_msg = 'pg should have dimension (periodNum * len(plant))'
        self.assertEqual(pg.shape, self.mock_pg.shape, err_msg)


if __name__ == '__main__':
    unittest.main()
