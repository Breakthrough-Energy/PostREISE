import pandas as pd
import pytest
from powersimdata.tests.mock_scenario import MockScenario

from postreise.plot.plot_bar_renewable_max_profile_actual import (
    plot_bar_renewable_max_profile_actual,
)

mock_plant = {
    "plant_id": ["A", "B", "C", "D", "E", "F", "G", "H"],
    "zone_id": [301, 302, 303, 304, 305, 306, 307, 308],
    "Pmax": [100, 75, 150, 30, 50, 300, 200, 80],
    "Pmin": [0, 0, 0, 0, 0, 100, 10, 0],
    "type": ["solar", "wind", "solar", "hydro", "wind", "solar", "ng", "wind"],
    "zone_name": [
        "Far West",
        "North",
        "West",
        "South",
        "North Central",
        "South Central",
        "Coast",
        "East",
    ],
}

mock_solar = pd.DataFrame(
    {
        "A": [95, 95, 96, 94],
        "C": [140, 135, 136, 144],
        "F": [299, 298, 299, 298],
    },
    index=pd.date_range(start="2016-01-01", periods=4, freq="H"),
)

mock_wind = pd.DataFrame(
    {
        "B": [70, 71, 70, 72],
        "E": [40, 39, 38, 41],
        "H": [71, 74, 68, 69],
    },
    index=pd.date_range(start="2016-01-01", periods=4, freq="H"),
)

mock_pg = pd.DataFrame(
    {
        "A": [80, 75, 72, 81],
        "B": [22, 22, 25, 20],
        "C": [130, 130, 130, 130],
        "D": [25, 26, 27, 28],
        "E": [10, 11, 9, 12],
        "F": [290, 295, 295, 294],
        "G": [190, 190, 191, 190],
        "H": [61, 63, 65, 67],
    },
    index=pd.date_range(start="2016-01-01", periods=4, freq="H"),
)

grid_attrs = {"plant": mock_plant}
scenario = MockScenario(grid_attrs, pg=mock_pg, solar=mock_solar, wind=mock_wind)
scenario.info["interconnect"] = "Texas"
scenario.info["start_date"] = pd.Timestamp(2016, 1, 1)
scenario.info["end_date"] = pd.Timestamp(2016, 1, 1, 3)
scenario.state.grid.id2zone = {
    k: v for k, v in zip(mock_plant["zone_id"], mock_plant["zone_name"])
}
scenario.state.grid.zone2id = {v: k for k, v in scenario.state.grid.id2zone.items()}


def test_plot_bar_renewable_max_profile_actual():
    plot_bar_renewable_max_profile_actual(scenario, "Texas", "wind", plot_show=False)
    plot_bar_renewable_max_profile_actual(
        scenario,
        "Texas",
        "solar",
        show_as_state=False,
        percentage=True,
        plot_show=False,
    )


def test_plot_bar_renewable_max_profile_actual_argument_type():
    with pytest.raises(TypeError) as excinfo:
        plot_bar_renewable_max_profile_actual(
            scenario, ["Texas"], "wind", plot_show=False
        )
    assert "interconnect must be a str" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        plot_bar_renewable_max_profile_actual(
            scenario, "Texas", ["coal"], plot_show=False
        )
    assert "gen_type must be a str" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        plot_bar_renewable_max_profile_actual(
            scenario, "Texas", "wind", fontsize="15", plot_show=False
        )
    assert "fontsize must be either a int or a float" in str(excinfo.value)


def test_plot_bar_renewable_max_profile_actual_argument_value():
    with pytest.raises(ValueError) as excinfo:
        plot_bar_renewable_max_profile_actual(
            scenario, "Europe", "wind", plot_show=False
        )
    assert (
        "interconnect must be one of ['Eastern', 'Eastern_Western', 'Texas', 'Texas_Eastern', 'Texas_Western', 'USA', 'Western']"
        in str(excinfo.value)
    )
    with pytest.raises(ValueError) as excinfo:
        plot_bar_renewable_max_profile_actual(
            scenario, "Western", "wind", plot_show=False
        )
    assert "interconnect is incompatible with scenario's interconnect" in str(
        excinfo.value
    )
