import pandas as pd
import pytest
from powersimdata.tests.mock_scenario import MockScenario

from postreise.plot.plot_scatter_capacity_vs_cost_curve_slope import (
    plot_scatter_capacity_vs_cost_curve_slope,
)

mock_plant = {
    "plant_id": ["A", "B", "C", "D", "E", "F", "G", "H"],
    "zone_id": [301, 302, 303, 304, 305, 306, 307, 308],
    "Pmax": [0, 107.339504, 111.162538, 50, 246.45462, 526.536296, 135.964283, 80],
    "Pmin": [0, 34.086297, 0, 0, 0, 87.3496, 0, 0],
    "type": ["solar", "coal", "ng", "hydro", "ng", "coal", "ng", "wind"],
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

mock_gencost = pd.DataFrame(
    {
        "plant_id": ["A", "B", "C", "D", "E", "F", "G", "H"],
        "type": [2] * 8,
        "startup": [0] * 8,
        "shutdown": [0] * 8,
        "n": [3] * 8,
        "p1": [0, 34.086297, 0, 0, 0, 87.3496, 0, 0],
        "f1": [0, 1389.874177, 954.059069, 0, 1740.404763, 4176.870758, 1518.336994, 0],
        "p2": [0, 107.339504, 111.162538, 50, 246.45462, 526.536296, 135.964283, 80],
        "f2": [0, 3037.013714, 3571.755645, 0, 8498.008304, 17948.417749, 5511.044, 0],
        "interconnect": ["Texas"] * 8,
    }
)


grid_attrs = {"plant": mock_plant, "gencost_after": mock_gencost}
scenario = MockScenario(grid_attrs)
scenario.info["interconnect"] = "Texas"
scenario.state.grid.id2zone = {
    k: v for k, v in zip(mock_plant["zone_id"], mock_plant["zone_name"])
}
scenario.state.grid.zone2id = {v: k for k, v in scenario.state.grid.id2zone.items()}


def test_plot_scatter_capacity_vs_cost_curve_slope():
    plot_scatter_capacity_vs_cost_curve_slope(
        scenario, "Texas", "coal", plot_show=False
    )
    plot_scatter_capacity_vs_cost_curve_slope(
        scenario,
        "Far West",
        "ng",
        title="capacity vs cost curve slope for solar in Far West",
        plot_show=False,
    )
    _, data_avg = plot_scatter_capacity_vs_cost_curve_slope(
        scenario, "Texas", "solar", plot_show=False
    )
    assert data_avg == 0


def _assert_error(err_msg, *args, **kwargs):
    with pytest.raises(TypeError) as excinfo:
        plot_scatter_capacity_vs_cost_curve_slope(*args, **kwargs)
    assert err_msg in str(excinfo.value)


def test_plot_scatter_capacity_vs_cost_curve_slope_argument_type():
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
