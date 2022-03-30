from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from powersimdata.tests.mock_scenario import MockScenario

from postreise.plot.plot_bar_shortfall import plot_bar_shortfall

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

target = pd.DataFrame(
    {
        "ce_target_fraction": [0.2437],
        "allowed_resources": ["solar, wind"],
        "external_ce_addl_historical_amount": [0.00],
        "solar_percentage": [np.nan],
        "area_type": [np.nan],
    },
    index=["Texas"],
)
target.index.name = "region_name"


@patch("postreise.plot.plot_bar_shortfall.Scenario", return_value=scenario)
def test_plot_bar_shortfall(monkeypatch):
    plot_bar_shortfall("Texas", 500, target, plot_show=False)
    plot_bar_shortfall(
        "Texas",
        500,
        target,
        baseline_scenario=1,
        baseline_scenario_name="Baseline",
        plot_show=False,
    )


def test_plot_bar_shortfall_argument_type():
    with pytest.raises(TypeError) as excinfo:
        plot_bar_shortfall(
            areas="all",
            scenario_ids=[823, 824],
            target_df="not a dataframe",
        )
    assert "target_df must be a pandas.DataFrame" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        plot_bar_shortfall(
            areas="all",
            scenario_ids=[823, 824],
            target_df=pd.DataFrame(),
            strategy="collaborative",
        )
    assert "strategy must be a dict" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        plot_bar_shortfall(
            areas="all",
            scenario_ids=[823, 824],
            target_df=pd.DataFrame(),
            strategy={823: "collaborative"},
            scenario_names=["USA 2016", "USA 2020"],
            baseline_scenario=["1", "2", "3"],
        )
    assert "baseline_scenario must be a str or int" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        plot_bar_shortfall(
            areas="all",
            scenario_ids=[823, 824],
            target_df=pd.DataFrame(),
            strategy={823: "collaborative"},
            scenario_names=["USA 2016", "USA 2020"],
            baseline_scenario=823,
            baseline_scenario_name=888,
        )
    assert "baseline_scenario_name must be a str" in str(excinfo.value)


def test_plot_bar_shortfall_argument_value():
    with pytest.raises(ValueError) as excinfo:
        plot_bar_shortfall(
            areas="all",
            scenario_ids=[823, 824],
            target_df=pd.DataFrame(),
            strategy={823: "collaborative"},
            scenario_names=["USA 2016"],
        )
    assert "scenario_names must have same size as scenario_ids" in str(excinfo.value)
