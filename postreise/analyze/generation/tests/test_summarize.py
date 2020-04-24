import unittest

import pandas as pd

from powersimdata.tests.mock_scenario import MockScenario
from postreise.analyze.tests.test_helpers import check_dataframe_matches
from postreise.analyze.generation.summarize import sum_generation_by_type_zone

# plant_id is the index
mock_plant = {
    'plant_id': ['A', 'B', 'C', 'D'],
    'zone_id': [1, 1, 2, 2],
    'type': ['solar', 'wind', 'hydro', 'hydro']
    }

mock_pg = pd.DataFrame({
    'A': [1, 2, 3, 4],
    'B': [1, 2, 4, 8],
    'C': [1, 1, 2, 3],
    'D': [1, 3, 5, 7],
    })

grid_attrs = {'plant': mock_plant}


class TestSumGenerationByTypeZone(unittest.TestCase):

    def setUp(self):
        self.scenario = MockScenario(grid_attrs, pg=mock_pg)

    def test_sum_generation(self):
        expected_return = pd.DataFrame({
            'type': ['hydro', 'solar', 'wind'],
            1: [0, 10, 15],
            2: [23, 0, 0]})
        expected_return.set_index('type', inplace=True)
        summed_generation = sum_generation_by_type_zone(self.scenario)
        check_dataframe_matches(summed_generation, expected_return)

    def test_with_string(self):
        with self.assertRaises(TypeError):
            sum_generation_by_type_zone('scenario_number')

    def test_with_scenario_not_analyze(self):
        test_scenario = MockScenario(grid_attrs, pg=mock_pg)
        test_scenario.state = 'Create'
        with self.assertRaises(ValueError):
            sum_generation_by_type_zone(test_scenario)
