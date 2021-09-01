import pandas as pd
import pytest
from powersimdata.input.tests.test_helpers import check_dataframe_matches
from powersimdata.tests.mock_scenario import MockScenario
from pytest import approx

from postreise.analyze.generation.capacity import (
    calculate_net_load_peak,
    calculate_NLDC,
    get_capacity_by_resources,
    get_capacity_factor_time_series,
    get_storage_capacity,
    sum_capacity_by_type_zone,
)

mock_plant = {
    "plant_id": [101, 102, 103],
    "type": ["solar", "wind", "wind"],
    "Pmax": [9000, 5000, 4000],
    "zone_name": ["Washington", "Washington", "Oregon"],
    "zone_id": [201, 201, 202],
}

mock_bus = {
    "bus_id": [1, 2, 3, 4],
    "zone_id": [201, 201, 202, 202],
}

mock_storage = {
    "bus_id": [1, 2, 3],
    "Pmax": [10, 10, 10],
}

mock_demand = pd.DataFrame(
    {
        "201": [
            133335,
            133630,
            131964,
            133614,
            134298,
            136032,
            136260,
            133757,
            129943,
            133440,
            135238,
            135242,
            133018,
            132799,
            133861,
            133275,
            130403,
        ]
    }
)

mock_pg = pd.DataFrame(
    {
        101: [
            6459,
            4084,
            1015,
            8004,
            7373,
            6161,
            3999,
            909,
            40,
            7332,
            6112,
            3725,
            795,
            7188,
            6082,
            3786,
            838,
        ],
        102: [
            2205,
            2757,
            3190,
            603,
            1402,
            1838,
            1948,
            2478,
            3186,
            1559,
            1752,
            2033,
            2400,
            1352,
            2160,
            2472,
            3217,
        ],
        103: [
            2206,
            2758,
            3191,
            603,
            1402,
            1838,
            1949,
            2478,
            3187,
            1560,
            1752,
            2034,
            2401,
            1352,
            2160,
            2472,
            3217,
        ],
    }
)

scenario = MockScenario(
    grid_attrs={"plant": mock_plant, "bus": mock_bus, "storage_gen": mock_storage},
    demand=mock_demand,
    pg=mock_pg,
)
scenario.info["start_date"] = "2016-01-01 00:00:00"
scenario.info["end_date"] = "2016-01-01 10:00:00"
scenario.state.grid.zone2id = {
    "Washington": 201,
    "Oregon": 202,
}


def test_NLDC_calculation_wind_str():  # noqa: N802
    assert calculate_NLDC(scenario, "wind", 10) == approx(3496.1)


def test_NLDC_calculation_wind_set():  # noqa: N802
    assert calculate_NLDC(scenario, {"wind"}, 10) == approx(3496.1)


def test_NLDC_calculation_wind_tuple():  # noqa: N802
    assert calculate_NLDC(scenario, ("wind",), 10) == approx(3496.1)


def test_NLDC_calculation_wind_list():  # noqa: N802
    assert calculate_NLDC(scenario, ["wind"], 10) == approx(3496.1)


def test_NLDC_calculation_wind_5_hour():  # noqa: N802
    assert calculate_NLDC(scenario, {"wind"}, hours=5) == approx(3343)


def test_NLDC_calculation_solar():  # noqa: N802
    assert calculate_NLDC(scenario, {"solar"}, 10) == approx(3720)


def test_NLDC_calculation_wind_solar():  # noqa: N802
    assert calculate_NLDC(scenario, ["wind", "solar"], 10) == approx(8478.9)


def test_NLDC_calculation_solar_wind():  # noqa: N802
    assert calculate_NLDC(scenario, ["solar", "wind"], 10) == approx(8478.9)


def test_calculate_net_load_peak_solar():
    assert calculate_net_load_peak(scenario, {"solar"}, 10) == approx(2535.2)


def test_calculate_net_load_peak_solar_5():
    assert calculate_net_load_peak(scenario, {"solar"}, 5) == approx(2088.6)


def test_calculate_net_load_peak_wind():
    assert calculate_net_load_peak(scenario, {"wind"}, 10) == approx(3370.8)


def test_calculate_net_load_peak_wind_5():
    assert calculate_net_load_peak(scenario, {"wind"}, 5) == approx(3017.4)


def test_calculate_net_load_peak_solar_wind():
    capacity_value = calculate_net_load_peak(scenario, {"solar", "wind"}, 10)
    assert capacity_value == approx(8211.5)


def test_calculate_net_load_peak_solar_wind_5():
    capacity_value = calculate_net_load_peak(scenario, {"solar", "wind"}, 5)
    assert capacity_value == approx(7397.2)


def test_failure_scenario_type():
    with pytest.raises(TypeError):
        calculate_net_load_peak("scenario", ["solar", "wind"], hours=10)


def test_failure_resources_type_dict():
    with pytest.raises(TypeError):
        calculate_net_load_peak(scenario, {"solar": "wind"}, hours=10)


def test_failure_hours_type():
    with pytest.raises(TypeError):
        calculate_net_load_peak(scenario, ["solar", "wind"], hours=10.0)


def test_failure_no_resources_present():
    with pytest.raises(ValueError):
        calculate_net_load_peak(scenario, ["geothermal"], hours=10)


def test_failure_one_resource_not_present():
    with pytest.raises(ValueError):
        calculate_net_load_peak(scenario, ["wind", "geothermal"], 10)


def test_failure_no_resources():
    with pytest.raises(ValueError):
        calculate_net_load_peak(scenario, [], 10)


def test_failure_zero_hours():
    with pytest.raises(ValueError):
        calculate_net_load_peak(scenario, ["solar"], hours=0)


def test_failure_too_many_hours():
    with pytest.raises(ValueError):
        calculate_net_load_peak(scenario, ["solar"], hours=100)


def test_get_capacity_by_resources():
    arg = [(scenario, "Oregon", "wind"), (scenario, "all", "wind")]
    expected = [4000, 9000]
    for a, e in zip(arg, expected):
        assert get_capacity_by_resources(*a).values == e


def test_get_storage_capacity():
    arg = [(scenario, "Washington"), (scenario, "all")]
    expected = [20, 30]
    for a, e in zip(arg, expected):
        assert get_storage_capacity(*a) == e


def test_sum_capacity_by_type_zone():
    expected_df = pd.DataFrame(
        {201: [9000, 5000], 202: [0, 4000]},
        index=["solar", "wind"],
    )
    check_dataframe_matches(expected_df, sum_capacity_by_type_zone(scenario))


def test_get_capacity_factor_time_series():
    expected_df = pd.DataFrame({101: mock_pg[101] / 9000})
    check_dataframe_matches(
        expected_df, get_capacity_factor_time_series(scenario, "Washington", "solar")
    )
