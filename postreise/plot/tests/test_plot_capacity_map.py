import pytest
from bokeh import plotting as plt
from powersimdata.tests.mock_scenario import MockScenario

from postreise.plot.plot_capacity_map import map_plant_capacity

mock_plant = {
    "plant_id": ["A", "B", "C", "D", "E", "F", "G", "H"],
    "bus_id": [1, 2, 3, 4, 5, 6, 7, 9],
    "lat": [29.7604, 30.2672, 26.183, 31.7619, 32.7555, 30.6280, 31.5493, 29.3013],
    "lon": [
        -95.3698,
        -97.7431,
        -98.123,
        -106.4850,
        -97.3308,
        -96.3344,
        -97.1467,
        94.7977,
    ],
    "Pmax": [1000, 750, 1500, 300, 500, 300, 200, 800],
    "type": ["coal", "coal", "coal", "coal", "wind", "coal", "coal", "solar"],
}

scenario = MockScenario({"plant": mock_plant})


def test_map_plant_capacity():
    canvas = map_plant_capacity(scenario, ["coal"])
    assert isinstance(canvas, plt.Figure)

    ct = {
        "new_plant": [
            {"type": "solar", "bus_id": 9, "Pmax": 800},
            {
                "type": "coal",
                "bus_id": 8,
                "Pmin": 25,
                "Pmax": 200,
                "c0": 1800,
                "c1": 30,
                "c2": 0.0025,
            },
        ]
    }
    scenario.state.ct = ct
    _ = map_plant_capacity(scenario, ["coal"], disaggregation="new_vs_existing_plants")

    scenario.state.ct = {}
    _ = map_plant_capacity(scenario, ["coal"], disaggregation="new_vs_existing_plants")

    _ = map_plant_capacity(scenario, ["hydro", "coal"])


def test_map_plant_capacity_argument_value():
    with pytest.raises(ValueError) as excinfo:
        map_plant_capacity(scenario, ["solar"], disaggregation="renewables")
    assert "Unknown disaggregation method: renewables" in str(excinfo.value)
