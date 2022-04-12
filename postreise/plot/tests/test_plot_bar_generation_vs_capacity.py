from unittest.mock import patch

import pandas as pd
import pytest
from powersimdata.tests.mock_scenario import MockScenario

from postreise.plot.plot_bar_generation_vs_capacity import (
    _get_bar_display_val,
    make_gen_cap_custom_data,
    plot_bar_generation_vs_capacity,
)

mock_plant = {
    "plant_id": ["A", "B", "C", "D", "E", "F", "G", "H"],
    "zone_id": [301, 302, 303, 304, 305, 306, 307, 308],
    "Pmax": [100, 75, 150, 30, 50, 300, 200, 80],
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

mock_solar = pd.DataFrame(
    {
        "A": [95, 95, 96, 94],
        "C": [140, 135, 136, 144],
        "F": [299, 298, 299, 298],
        "G": [195, 195, 193, 199],
    },
    index=pd.date_range(start="2016-01-01", periods=4, freq="H"),
)

mock_wind = pd.DataFrame(
    {
        "B": [70, 71, 70, 72],
        "D": [29, 29, 29, 29],
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

mock_demand = pd.DataFrame(
    {
        301: [1100, 1102, 1103, 1104],
        302: [2344, 2343, 2342, 2341],
        303: [3875, 3876, 3877, 3878],
        304: [4924, 4923, 4922, 4921],
        305: [400, 300, 200, 100],
        306: [5004, 5003, 5002, 5001],
        307: [2504, 2503, 2502, 2501],
        308: [3604, 3603, 3602, 1],
    },
    index=pd.date_range(start="2016-01-01", periods=4, freq="H"),
)

grid_attrs = {"plant": mock_plant}
scenario = MockScenario(
    grid_attrs, pg=mock_pg, solar=mock_solar, wind=mock_wind, demand=mock_demand
)
scenario.info["name"] = "Best Scenario"
scenario.info["interconnect"] = "Texas"
scenario.info["start_date"] = pd.Timestamp(2016, 1, 1)
scenario.info["end_date"] = pd.Timestamp(2016, 1, 1, 3)
scenario.state.grid.interconnect = ["Texas"]
scenario.state.grid.id2zone = {
    k: v for k, v in zip(mock_plant["zone_id"], mock_plant["zone_name"])
}
scenario.state.grid.zone2id = {v: k for k, v in scenario.state.grid.id2zone.items()}


@patch("postreise.plot.plot_bar_generation_vs_capacity.Scenario", return_value=scenario)
def test_plot_bar_generation_stack(monkeypatch):
    plot_bar_generation_vs_capacity(
        areas=["Coast", "Texas"],
        area_types=["loadzone", "interconnect"],
        scenario_ids=[22, 44],
        time_zone="US/Central",
        plot_show=False,
    )
    plot_bar_generation_vs_capacity(
        areas="Far West",
        area_types="loadzone",
        scenario_ids=[22, 44],
        horizontal=True,
        plot_show=False,
    )


def test_plot_bar_generation_stack_argument_type():
    with pytest.raises(TypeError) as excinfo:
        plot_bar_generation_vs_capacity(
            areas=["South", "Far West"],
            area_types=["loadzone", "loadzone"],
            scenario_ids=[22, 44],
            resource_labels=["solar", "wind"],
            plot_show=False,
        )
    assert "resource_labels must be a dict" in str(excinfo.value)


def test_plot_bar_generation_stack_argument_value():
    with pytest.raises(ValueError) as excinfo:
        plot_bar_generation_vs_capacity(
            areas=["South", "East"],
            area_types=["loadzone"],
            scenario_ids=[22, 44],
            plot_show=False,
        )
    assert "area_types must have same size as areas" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        plot_bar_generation_vs_capacity(
            areas="South Central",
            area_types="loadzone",
            scenario_ids=[1000, 2000],
            scenario_names=["CaseA", "CaseB", "CaseC"],
            plot_show=False,
        )
    assert "scenario_names must have same size as scenario_ids" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        plot_bar_generation_vs_capacity(
            areas="South Central",
            area_types="loadzone",
            scenario_ids=1000,
            plot_show=False,
        )
    assert "two scenario and/or custom data must be provided" in str(excinfo.value)


def test_get_bar_display_val_greater_than_ten():
    val = _get_bar_display_val(10.456)
    assert val == 10


def test_get_bar_display_val_less_than_ten():
    val = _get_bar_display_val(3.456)
    assert val == 3.5


def test_get_bar_display_val_zero():
    val = _get_bar_display_val(0)
    assert val == 0


def test_make_gen_cap_custom_data_given_no_data():
    label = "my data"
    gen_cap_data = make_gen_cap_custom_data("Western", label)
    expected_gen_cap_data = {
        "name": label,
        "gen": {
            "label": "Generation",
            "unit": "TWh",
            "data": {"Western": {}},
        },
        "cap": {"label": "Capacity", "unit": "GW", "data": {"Western": {}}},
    }

    assert gen_cap_data == expected_gen_cap_data


def test_make_gen_cap_custom_data_given_cap_data():
    label = "my data"
    mock_data = pd.DataFrame(
        {
            "Western": [10, 10, 10, 10],
        },
        index=["wind", "solar", "hydro", "coal"],
    )
    gen_cap_data = make_gen_cap_custom_data("Western", label, cap_data=mock_data)
    expected_gen_cap_data = {
        "name": label,
        "gen": {
            "label": "Generation",
            "unit": "TWh",
            "data": {"Western": {}},
        },
        "cap": {"label": "Capacity", "unit": "GW", "data": mock_data.to_dict()},
    }

    assert gen_cap_data == expected_gen_cap_data


def test_make_gen_cap_custom_data_given_gen_and_cap_data():
    label = "my data"
    mock_gen_data = pd.DataFrame(
        {
            "Western": [100, 100, 100, 100],
        },
        index=["wind", "solar", "hydro", "coal"],
    )
    mock_cap_data = pd.DataFrame(
        {
            "Western": [10, 10, 10, 10],
        },
        index=["wind", "solar", "hydro", "coal"],
    )
    gen_cap_data = make_gen_cap_custom_data(
        "Western", label, mock_gen_data, mock_cap_data
    )
    expected_gen_cap_data = {
        "name": label,
        "gen": {"label": "Generation", "unit": "TWh", "data": mock_gen_data.to_dict()},
        "cap": {"label": "Capacity", "unit": "GW", "data": mock_cap_data.to_dict()},
    }

    assert gen_cap_data == expected_gen_cap_data
