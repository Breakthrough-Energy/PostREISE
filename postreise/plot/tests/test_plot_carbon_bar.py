import pandas as pd
import pytest
from powersimdata.tests.mock_scenario import MockScenario

from postreise.plot.plot_carbon_bar import plot_carbon_bar

mock_plant_s1 = {
    "plant_id": ["A", "B", "C", "D", "E", "F", "G", "H"],
    "bus_id": [1, 2, 3, 4, 5, 6, 7, 9],
    "type": ["coal", "wind", "coal", "coal", "ng", "coal", "ng", "ng"],
}

mock_pg_s1 = pd.DataFrame(
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

s1 = MockScenario({"plant": mock_plant_s1}, pg=mock_pg_s1)
s1.info["name"] = "Carbon Scenario 1"


mock_plant_s2 = {
    "plant_id": ["a", "b", "c", "d", "e", "f", "g", "h"],
    "bus_id": [1, 2, 3, 4, 5, 6, 7, 9],
    "type": ["ng", "ng", "ng", "coal", "coal", "hydro", "ng", "solar"],
}

mock_pg_s2 = pd.DataFrame(
    {
        "a": [180, 175, 172, 181],
        "b": [122, 122, 125, 120],
        "c": [330, 330, 330, 330],
        "d": [225, 226, 227, 228],
        "e": [110, 111, 119, 112],
        "f": [90, 95, 95, 94],
        "g": [90, 90, 91, 90],
        "h": [61, 63, 65, 67],
    },
    index=pd.date_range(start="2016-01-01", periods=4, freq="H"),
)

s2 = MockScenario({"plant": mock_plant_s2}, pg=mock_pg_s2)
s2.info["name"] = "Carbon Scenario 2"


def test_plot_carbon_bar():
    plot_carbon_bar(
        s1,
        s2,
        labels_size=10,
        plot_show=False,
    )
    plot_carbon_bar(
        s1,
        s2,
        labels=[s1.info["name"], s2.info["name"]],
        plot_show=False,
    )


def test_plot_carbon_bar_argument_type():
    with pytest.raises(TypeError) as excinfo:
        plot_carbon_bar(
            s1,
            labels={"first": s1.info["name"]},
        )
    assert "labels must be a list/tuple/set" in str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        plot_carbon_bar(s1, labels_size=12.5)
    assert "labels_size must be an int" in str(excinfo.value)


def test_plot_carbon_bar_argument_value():
    with pytest.raises(ValueError) as excinfo:
        plot_carbon_bar(1, "2", s1)
    assert "all inputs must be Scenario objects" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        plot_carbon_bar(s2, labels=["scenario 1", "scenario 2"])
    assert "labels must have same length as number of scenarios" in str(excinfo.value)
