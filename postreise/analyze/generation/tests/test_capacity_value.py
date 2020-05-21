import pandas as pd
import pytest
from pytest import approx

from powersimdata.tests.mock_scenario import MockScenario
from postreise.analyze.generation.capacity_value import calculate_capacity_value


mock_plant = {
    'plant_id': [101, 102, 103],
    'type': ['solar', 'wind', 'wind'],
    }
    
mock_demand = pd.DataFrame({'zone 1': [
    133335, 133630, 131964, 133614, 134298, 136032, 136260, 133757, 129943,
    133440, 135238, 135242, 133018, 132799, 133861, 133275, 130403]})

mock_pg = pd.DataFrame({
    101: [6459, 4084, 1015, 8004, 7373, 6161, 3999, 909, 40, 7332, 6112, 3725,
          795, 7188, 6082, 3786, 838],
    102: [2205, 2757, 3190, 603, 1402, 1838, 1948, 2478, 3186, 1559, 1752,
          2033, 2400, 1352, 2160, 2472, 3217],
    103: [2206, 2758, 3191, 603, 1402, 1838, 1949, 2478, 3187, 1560, 1752,
          2034, 2401, 1352, 2160, 2472, 3217],
    })

scenario = MockScenario(
    grid_attrs={'plant': mock_plant}, demand=mock_demand, pg=mock_pg)


def test_calculation_wind_str():
    assert calculate_capacity_value(scenario, 'wind', 10) == approx(3496.1)


def test_calculation_wind_set():
    assert calculate_capacity_value(scenario, {'wind'}, 10) == approx(3496.1)


def test_calculation_wind_tuple():
    assert calculate_capacity_value(scenario, ('wind',), 10) == approx(3496.1)


def test_calculation_wind_list():
    assert calculate_capacity_value(scenario, ['wind'], 10) == approx(3496.1)


def test_calculation_wind_5_hour():
    assert calculate_capacity_value(scenario, 'wind', hours=5) == approx(3343)


def test_calculation_solar():
    assert calculate_capacity_value(scenario, {'solar'}, 10) == approx(3720)


def test_calculation_wind_solar():
    capacity_value = calculate_capacity_value(scenario, ['wind', 'solar'], 10)
    assert capacity_value == approx(8478.9)


def test_calculation_solar_wind():
    capacity_value = calculate_capacity_value(scenario, ['solar', 'wind'], 10)
    assert capacity_value == approx(8478.9)


def test_failure_scenario_type():
    with pytest.raises(TypeError):
        calculate_capacity_value('scenario', ['solar', 'wind'], hours=10)


def test_failure_resources_type():
    with pytest.raises(TypeError):
        calculate_capacity_value(scenario, {'solar': 'wind'}, hours=10)


def test_failure_hours_type():
    with pytest.raises(TypeError):
        calculate_capacity_value(scenario, ['solar', 'wind'], hours=10.0)


def test_failure_no_resources_present():
    with pytest.raises(ValueError):
        calculate_capacity_value(scenario, ['geothermal'], hours=10)


def test_failure_one_resource_not_present():
    with pytest.raises(ValueError):
        calculate_capacity_value(scenario, ['solar', 'wind', 'geothermal'], 10)


def test_failure_no_resources():
    with pytest.raises(ValueError):
        calculate_capacity_value(scenario, [], 10)


def test_failure_zero_hours():
    with pytest.raises(ValueError):
        calculate_capacity_value(scenario, ['solar'], hours=0)


def test_failure_too_many_hours():
    with pytest.raises(ValueError):
        calculate_capacity_value(scenario, ['solar'], hours=100)
