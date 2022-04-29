import pandas as pd
import pytest
from powersimdata.tests.mock_scenario import MockScenario

from postreise.plot.plot_sim_vs_hist import plot_generation_sim_vs_hist

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
scenario.state.grid.model = "usa_tamu"

hist_gen = pd.DataFrame(
    {
        "solar": 100 * 4,
        "wind": 205 * 4,
        "hydro": 180 * 4,
        "coal": 300 * 4,
        "ng": 200 * 4,
    },
    index=["Texas"],
)


def test_plot_generation_sim_vs_hist_argument_type():
    with pytest.raises(TypeError, match="hist_gen must be a pandas.DataFrame"):
        plot_generation_sim_vs_hist(scenario, 3, "Texas")
    with pytest.raises(TypeError, match="state must be a str"):
        plot_generation_sim_vs_hist(scenario, pd.DataFrame(), ["Texas"])


def test_plot_generation_sim_vs_hist_argument_value():
    with pytest.raises(ValueError, match="Invalid state"):
        plot_generation_sim_vs_hist(scenario, hist_gen, "Washington")


def test_plot_generation_sim_vs_hist():
    plot_generation_sim_vs_hist(
        scenario, hist_gen, "Texas", show_max=False, plot_show=False
    )
    plot_generation_sim_vs_hist(scenario, hist_gen, "Texas", plot_show=False)
