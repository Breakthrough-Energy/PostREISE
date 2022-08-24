from unittest.mock import patch

import pandas as pd
import pytest
from powersimdata.tests.mock_scenario import MockScenario

from postreise.plot.plot_pie_generation_vs_capacity import (
    plot_pie_generation_vs_capacity,
)

mock_plant = {
    "plant_id": ["A", "B", "C", "D", "E", "F", "G", "H"],
    "zone_id": [301, 302, 303, 304, 305, 306, 307, 308],
    "Pmax": [1000, 750, 1500, 300, 500, 300, 200, 800],
    "Pmin": [0, 0, 0, 0, 0, 100, 10, 0],
    "type": ["solar", "wind", "solar", "wind", "wind", "solar", "solar", "wind"],
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
        "A": [800, 750, 720, 810],
        "B": [220, 220, 250, 200],
        "C": [1300, 1300, 1300, 1300],
        "D": [250, 260, 270, 280],
        "E": [100, 110, 90, 120],
        "F": [290, 295, 295, 294],
        "G": [190, 190, 191, 190],
        "H": [610, 630, 650, 670],
    },
    index=pd.date_range(start="2016-01-01", periods=4, freq="H"),
)

grid_attrs = {"plant": mock_plant}
scenario = MockScenario(grid_attrs, pg=mock_pg)
scenario.info["grid_model"] = "usa_tamu"
scenario.info["name"] = "Best Scenario"
scenario.info["interconnect"] = "Texas"
scenario.info["start_date"] = pd.Timestamp(2016, 1, 1)
scenario.info["end_date"] = pd.Timestamp(2016, 1, 1, 3)
scenario.state.grid.interconnect = ["Texas"]
scenario.state.grid.id2zone = {
    k: v for k, v in zip(mock_plant["zone_id"], mock_plant["zone_name"])
}
scenario.state.grid.zone2id = {v: k for k, v in scenario.state.grid.id2zone.items()}


@patch("postreise.plot.plot_pie_generation_vs_capacity.Scenario", return_value=scenario)
def test_plot_pie_generation_vs_capacity(monkeypatch):
    plot_pie_generation_vs_capacity(
        areas="Texas",
        area_types="interconnect",
        scenario_ids=[100, 200],
    )


def _assert_error(err_type, err_msg, *args, **kwargs):
    with pytest.raises(err_type) as excinfo:
        plot_pie_generation_vs_capacity(*args, **kwargs)
    assert err_msg in str(excinfo.value)


def test_plot_pie_generation_vs_capacity_argument_type():
    _assert_error(
        TypeError,
        "resource_labels must be a dict",
        areas=["all", "Western", "Texas", "Eastern"],
        area_types=[None, "interconnect", None, None],
        scenario_ids=[823, 824],
        scenario_names=["USA 2016", "USA 2020"],
        resource_labels=["My Natural Gas", "My Coal"],
        min_percentage=2.5,
    )
    _assert_error(
        TypeError,
        "resource_colors must be a dict",
        areas=["all", "Western", "Texas", "Eastern"],
        area_types=[None, "interconnect", None, None],
        scenario_ids=[823, 824],
        scenario_names=["USA 2016", "USA 2020"],
        resource_labels={"ng": "My Natural Gas", "coal": "My Coal"},
        resource_colors=["red", "blue", "yellow"],
        min_percentage=2.5,
    )


def test_plot_pie_generation_vs_capacity_argument_value():
    _assert_error(
        ValueError,
        "area_types and areas must have same length",
        areas=["all", "Western", "Texas", "Eastern"],
        area_types=["interconnect"],
        scenario_ids=[823, 824],
        scenario_names=["USA 2016", "USA 2020"],
        min_percentage=2.5,
    )
    _assert_error(
        ValueError,
        "scenario_names and scenario_ids must have same length",
        areas=["all", "Western", "Texas", "Eastern"],
        area_types=[None, "interconnect", None, None],
        scenario_ids=[823, 824],
        scenario_names=["USA 2016"],
        min_percentage=2.5,
    )
    _assert_error(
        ValueError,
        "scenario_ids and/or custom_data must have at least two elements",
        areas=["all", "Western", "Texas", "Eastern"],
        area_types=[None, "interconnect", None, None],
        scenario_ids=[823],
        scenario_names=["USA 2016"],
        min_percentage=2.5,
    )
