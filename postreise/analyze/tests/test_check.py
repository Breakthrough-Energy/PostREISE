import datetime
import numpy as np
import pandas as pd
import pytest

from powersimdata.tests.mock_scenario import MockScenario
from postreise.analyze.check import (
    _check_data_frame,
    _check_grid,
    _check_scenario_is_in_analyze_state,
    _check_areas_and_format,
    _check_resources_and_format,
    _check_resources_are_renewable_and_format,
    _check_resources_are_in_grid,
    _check_plants_are_in_grid,
    _check_number_hours_to_analyze,
    _check_date,
    _check_date_range,
    _check_epsilon,
    _check_gencost,
    _check_time_series,
    _check_curtailment,
)


mock_plant = {
    "plant_id": range(15),
    "type": [
        "solar",
        "nuclear",
        "wind",
        "wind_offshore",
        "coal",
        "ng",
        "coal",
        "coal",
        "geothermal",
        "wind",
        "solar",
        "hydro",
        "coal",
        "ng",
        "solar",
    ],
}

mock_gencost = {
    "plant_id": range(15),
    "type": [2] * 15,
    "startup": [0] * 15,
    "shutdown": [0] * 15,
    "n": [3] * 15,
    "c2": [
        0,
        0.00021,
        0,
        0,
        0.00125,
        0.0015,
        0.00085,
        0.0009,
        0,
        0,
        0,
        0,
        0.0013,
        0.0011,
        0,
    ],
    "c1": [0, 20, 0, 0, 25, 32, 18, 29, 0, 0, 0, 0, 35, 27, 0],
    "c0": [0, 888, 0, 0, 750, 633, 599, 933, 0, 0, 0, 0, 1247, 1111, 0],
    "interconnect": ["Western"] * 15,
}

scenario = MockScenario({"plant": mock_plant, "gencost_after": mock_gencost})
scenario.info["start_date"] = "2016-01-01 00:00:00"
scenario.info["end_date"] = "2016-01-10 23:00:00"

grid = scenario.state.get_grid()


def test_check_data_frame_argument_type():
    arg = (
        (1, "int"),
        ("homer", "str"),
        ({"homer", "marge", "bart", "lida"}, "set"),
        (pd.DataFrame({"California": [1, 2, 3], "Texas": [4, 5, 6]}), 123456),
    )
    for a in arg:
        with pytest.raises(TypeError):
            _check_data_frame(a[0], a[1])


def test_check_data_frame_argument_value():
    arg = (
        (pd.DataFrame({"California": [], "Texas": []}), "row"),
        (pd.DataFrame({}), "col"),
    )
    for a in arg:
        with pytest.raises(ValueError):
            _check_data_frame(a[0], a[1])


def test_check_data_frame():
    _check_data_frame(
        pd.DataFrame({"California": [1, 2, 3], "Texas": [4, 5, 6]}), "pandas.DataFrame"
    )


def test_check_grid_argument_type():
    arg = (1, pd.DataFrame({"California": [1, 2, 3], "Texas": [4, 5, 6]}))
    for a in arg:
        with pytest.raises(TypeError):
            _check_grid(a)


def test_check_grid():
    _check_grid(grid)


def test_check_scenario_is_in_analyze_state_argument_type():
    arg = (1, grid)
    for a in arg:
        with pytest.raises(TypeError):
            _check_scenario_is_in_analyze_state(a)


def test_check_scenario_is_in_analyze_state_argument_value():
    input = MockScenario()
    input.state = "Create"
    with pytest.raises(ValueError):
        _check_scenario_is_in_analyze_state(input)


def test_check_scenario_is_in_analyze():
    _check_scenario_is_in_analyze_state(scenario)


def test_check_areas_and_format_argument_type():
    arg = (
        1,
        {"California": [1, 2, 3], "Texas": [4, 5, 6]},
        [1, 2, 3, 4],
        (1, 2, 3, 4),
        ("a", "b", "c", 4),
    )
    for a in arg:
        with pytest.raises(TypeError):
            _check_areas_and_format()


def test_check_areas_and_format_argument_value():
    arg = ([], {"Texas", "Louisane", "Florida", "Canada"}, {"France"})
    for a in arg:
        with pytest.raises(ValueError):
            _check_areas_and_format(a)


def test_check_areas_and_format():
    _check_areas_and_format(["Western", "NY", "El Paso", "Arizona"])
    areas = _check_areas_and_format(["California", "CA", "NY", "TX", "MT", "WA"])
    assert areas == {"Washington", "Texas", "Montana", "California", "New York"}


def test_check_resources_and_format_argument_type():
    arg = (
        1,
        {"coal": [1, 2, 3], "htdro": [4, 5, 6]},
        [1, 2, 3, 4],
        (1, 2, 3, 4),
        {1, 2, 3, 4},
        ("a", "b", "c", 4),
    )
    for a in arg:
        with pytest.raises(TypeError):
            _check_resources_and_format(a)


def test_check_resources_and_format_argument_value():
    arg = ((), {"solar", "nuclear", "ng", "battery"}, {"geo-thermal"})
    for a in arg:
        with pytest.raises(ValueError):
            _check_resources_and_format(a)


def test_check_resources_and_format():
    _check_resources_and_format(["dfo", "wind", "solar", "ng"])
    _check_resources_and_format("wind_offshore")
    _check_resources_and_format({"nuclear"})


def test_check_resources_are_renewable_and_format_argument_value():
    with pytest.raises(ValueError):
        _check_resources_are_renewable_and_format({"solar", "nuclear"})


def test_check_resources_are_renewable_and_format():
    _check_resources_are_renewable_and_format(["wind_offshore", "wind"])
    _check_resources_are_renewable_and_format("solar")
    _check_resources_are_renewable_and_format({"wind"})


def test_check_resources_are_in_grid_argument_value():
    arg = (({"solar", "dfo"}, grid), ({"uranium"}, grid))
    for a in arg:
        with pytest.raises(ValueError):
            _check_resources_are_in_grid(a[0], a[1])


def test_check_resources_are_in_grid():
    _check_resources_are_in_grid({"solar", "coal", "hydro"}, grid)
    _check_resources_are_in_grid(["solar", "ng", "hydro", "nuclear"], grid)


def test_check_plants_are_in_grid_argument_type():
    arg = (
        (str(grid.plant.index[1]), grid),
        (grid.plant.index[:3], grid),
        (grid.plant.index[0], grid.plant),
    )
    for a in arg:
        with pytest.raises(TypeError):
            _check_plants_are_in_grid(a[0], a[1])


def test_check_plants_are_in_grid_argument_value():
    with pytest.raises(ValueError):
        _check_plants_are_in_grid([p + 100 for p in grid.plant.index[-5:]], grid)


def test_check_plants_are_in_grid():
    _check_plants_are_in_grid([p for p in grid.plant.index[:5]], grid)
    _check_plants_are_in_grid([str(p) for p in grid.plant.index[:5]], grid)
    _check_plants_are_in_grid(set([p for p in grid.plant.index[:5]]), grid)
    _check_plants_are_in_grid(tuple([p for p in grid.plant.index[:5]]), grid)


def test_check_number_hours_to_analyze_argument_type():
    arg = ((scenario, "100"), (scenario, [100]), (scenario, {100, 50}))
    for a in arg:
        with pytest.raises(TypeError):
            _check_number_hours_to_analyze(a[0], a[1])


def test_check_number_hours_to_analyze_argument_value():
    arg = ((scenario, -10), (scenario, 15 * 24))
    for a in arg:
        with pytest.raises(ValueError):
            _check_number_hours_to_analyze(a[0], a[1])


def test_check_number_hours_to_analyze():
    _check_number_hours_to_analyze(scenario, 24)


def test_check_date_argument_type():
    with pytest.raises(TypeError):
        _check_date("2016-02-01 00:00:00")


def test_check_date():
    _check_date(datetime.datetime(2020, 9, 9))
    _check_date(np.datetime64("1981-06-21"))
    _check_date(pd.Timestamp(2016, 2, 1))


def test_check_date_range_argument_value():
    arg = (
        (scenario, pd.Timestamp(2016, 1, 5), pd.Timestamp(2016, 1, 2)),
        (scenario, pd.Timestamp(2016, 1, 2), pd.Timestamp(2016, 1, 2)),
        (scenario, pd.Timestamp(2015, 12, 1), pd.Timestamp(2016, 1, 8)),
        (scenario, pd.Timestamp(2016, 1, 2), pd.Timestamp(2016, 2, 15)),
    )
    for a in arg:
        with pytest.raises(ValueError):
            _check_date_range(a[0], a[1], a[2])


def test_check_date_range():
    _check_date_range(scenario, pd.Timestamp(2016, 1, 2), pd.Timestamp(2016, 1, 7))


def test_check_epsilon_argument_type():
    arg = ("1e-3", [0.0001])
    for a in arg:
        with pytest.raises(TypeError):
            _check_epsilon()


def test_check_epsilon_argument_value():
    with pytest.raises(ValueError):
        _check_epsilon(-0.00001)


def test_check_epsilon():
    _check_epsilon(1e-2)
    _check_epsilon(0.001)


def test_check_gencost_argument_type():
    gencost_n = grid.gencost["after"].copy()
    gencost_n.loc[0, "n"] = 3.0
    arg = (1, gencost_n)
    for a in arg:
        with pytest.raises(TypeError):
            _check_gencost(a)


def test_check_gencost_argument_value():
    gencost = grid.gencost["after"]
    gencost_n = grid.gencost["after"].copy()
    gencost_n.loc[0, "n"] = 10
    gencost_type = grid.gencost["after"].copy()
    gencost_type.loc[3, "type"] = 3
    arg = (
        gencost.drop(columns=["type"]),
        gencost.drop(columns=["n"]),
        gencost_type,
        gencost_n,
    )
    for a in arg:
        with pytest.raises(ValueError):
            _check_gencost(a)


def test_check_gencost():
    gencost = grid.gencost["after"]
    _check_gencost(gencost)


def test_check_time_series_argument_value():
    ts = pd.DataFrame(
        {"demand": [200, -100, 10, 75, 150]},
        index=pd.date_range("2018-01-01", periods=5, freq="H"),
    )
    with pytest.raises(ValueError):
        _check_time_series(ts, "demand")


def test_check_time_series():
    ts = pd.DataFrame(
        {"demand": [200, 100, 10, 75, 150]},
        index=pd.date_range("2018-01-01", periods=5, freq="H"),
    )
    _check_time_series(ts, "demand")


def test_check_curtailment_argument_type():
    curtailment = {
        "solar": pd.DataFrame(
            {1: 100, 2: 20, 3: 0},
            index=pd.date_range("2018-01-01", periods=3, freq="H"),
        ),
        "wind": [50, 5, 13],
    }
    arg = (1, ["solar", "wind"], curtailment)
    for a in arg:
        with pytest.raises(TypeError):
            _check_curtailment()


def check_curtailment():
    curtaiment = {
        "solar": pd.DataFrame(
            {1: 100, 2: 20, 3: 0},
            index=pd.date_range("2018-01-01", periods=3, freq="H"),
        ),
        "wind": pd.DataFrame(
            {1: 50, 2: 5, 3: 13},
            index=pd.date_range("2018-01-01", periods=3, freq="H"),
        ),
    }
    _check_curtailment(curtailment)
