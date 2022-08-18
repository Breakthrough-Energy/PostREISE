from unittest.mock import patch

import pandas as pd
import pytest
from powersimdata.tests.mock_scenario import MockScenario

from postreise.plot.plot_bar_generation_stack import plot_bar_generation_stack

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
        301: [11, 12, 13, 14],
        302: [2, 3, 8, 10],
        303: [38, 39, 40, 40],
        304: [20, 19, 18, 17],
        305: [4, 3, 2, 1],
        306: [200, 250, 225, 275],
        307: [100, 125, 150, 175],
        308: [36, 36, 37, 38],
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


@patch("postreise.plot.plot_bar_generation_stack.Scenario", return_value=scenario)
def test_plot_bar_generation_stack(monkeypatch):
    plot_bar_generation_stack(
        "Texas", 1000, "wind", area_types="interconnect", plot_show=False
    )
    plot_bar_generation_stack(
        "Texas",
        1000,
        "wind",
        area_types="interconnect",
        scenario_names="Worst Scenario",
        plot_show=False,
    )
    plot_bar_generation_stack(
        "Far West",
        200,
        "solar",
        area_types="loadzone",
        titles={"Far West": "Where?"},
        t2c={"solar": "#FFBB45"},
        t2hc={"solar_curtailment": "#996100"},
        t2l={"solar": "shiny"},
        curtailment_split=False,
        plot_show=False,
    )


def test_plot_bar_generation_stack_argument_type():
    with pytest.raises(TypeError) as excinfo:
        plot_bar_generation_stack(
            "Western",
            {823, 824},
            ["wind", "solar", "coal"],
        )
    assert "scenario_ids must be a int, str or list" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        plot_bar_generation_stack(
            "Western",
            [823, 824],
            {"wind", "solar", "coal"},
        )
    assert "resources must be a list or str" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        plot_bar_generation_stack(
            ["Western", "Eastern"],
            [823, 824],
            ["wind", "solar", "coal"],
            titles=["WECC", "EI"],
        )
    assert "titles must be a dictionary" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        plot_bar_generation_stack(
            ["Western", "Eastern"],
            [823, 824],
            ["wind", "solar", "coal"],
            save=True,
            filenames=["WECC", "EI"],
        )
    assert "filenames must be a dictionary" in str(excinfo.value)


def test_plot_bar_generation_stack_argument_value():
    with pytest.raises(ValueError) as excinfo:
        plot_bar_generation_stack(
            ["Western", "Eastern"],
            [823, 824],
            ["wind", "solar", "coal"],
            area_types="interconnect",
        )
    assert "area_types must have same size as areas" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        plot_bar_generation_stack(
            ["Western", "Eastern"],
            [823, 824],
            ["wind", "solar", "coal"],
            scenario_names="USA Basecase",
        )
    assert "scenario_names must have same size as scenario_ids" in str(excinfo.value)
