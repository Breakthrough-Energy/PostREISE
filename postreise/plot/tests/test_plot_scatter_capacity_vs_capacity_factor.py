import pandas as pd
import pytest
from powersimdata.tests.mock_scenario import MockScenario

from postreise.plot.plot_scatter_capacity_vs_capacity_factor import (
    plot_scatter_capacity_vs_capacity_factor,
)

mock_plant = {
    "plant_id": ["A", "B", "C", "D", "E", "F", "G", "H"],
    "zone_id": [301, 302, 303, 304, 305, 306, 307, 308],
    "Pmax": [100, 75, 150, 30, 50, 300, 200, 80],
    "Pmin": [0, 0, 0, 0, 0, 100, 10, 0],
    "type": ["solar", "wind", "hydro", "hydro", "wind", "coal", "ng", "wind"],
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
scenario = MockScenario(grid_attrs, pg=mock_pg)
scenario.info["interconnect"] = "Texas"
scenario.info["start_date"] = pd.Timestamp(2016, 1, 1)
scenario.info["end_date"] = pd.Timestamp(2016, 1, 1, 3)
scenario.state.grid.id2zone = {
    k: v for k, v in zip(mock_plant["zone_id"], mock_plant["zone_name"])
}
scenario.state.grid.zone2id = {v: k for k, v in scenario.state.grid.id2zone.items()}


def test_plot_scatter_capacity_vs_capacity_factor():
    plot_scatter_capacity_vs_capacity_factor(scenario, "Texas", "wind", plot_show=False)
    plot_scatter_capacity_vs_capacity_factor(
        scenario,
        "Far West",
        "solar",
        percentage=True,
        title="capacity vs capacity factor for solar in Far West",
        plot_show=False,
    )


def _assert_error(err_msg, *args, **kwargs):
    with pytest.raises(TypeError) as excinfo:
        plot_scatter_capacity_vs_capacity_factor(*args, **kwargs)
    assert err_msg in str(excinfo.value)


def test_plot_scatter_capacity_vs_capacity_factor_argument_type():
    _assert_error(
        "area must be a str", scenario, ["Far West"], "solar", plot_show=False
    )
    _assert_error(
        "resources must be a list or str", scenario, "North", 1, plot_show=False
    )
    _assert_error(
        "resources must be a list of str",
        scenario,
        "Texas",
        ["wind", 2],
        plot_show=False,
    )
    _assert_error(
        "markersize must be either an int or float",
        scenario,
        "East",
        ["wind", "solar"],
        markersize="15",
        plot_show=False,
    )
    _assert_error(
        "fontsize must be either an int or float",
        scenario,
        "South Central",
        ["wind", "solar"],
        fontsize="10",
        plot_show=False,
    )
    _assert_error(
        "title must be a str", scenario, "Coast", "solar", title=12345, plot_show=False
    )
