import unittest

import pandas as pd
from numpy.testing import assert_array_equal
from powersimdata.input.tests.test_helpers import check_dataframe_matches
from powersimdata.tests.mock_scenario import MockScenario

from postreise.analyze.generation.curtailment import (
    calculate_curtailment_percentage_by_resources,
    calculate_curtailment_time_series_by_resources,
    get_curtailment_time_series,
    summarize_curtailment_by_bus,
    summarize_curtailment_by_location,
)

# plant_id is the index
mock_plant = {
    "plant_id": ["A", "B", "C", "D"],
    "bus_id": [1, 2, 3, 4],
    "lat": [47.6, 47.6, 37.8, 37.8],
    "lon": [-122.3, -122.3, -122.4, -122.4],
    "type": ["solar", "solar", "wind", "wind_offshore"],
    "zone_name": ["Washington", "Washington", "Bay Area", "Bay Area"],
}

mock_pg = pd.DataFrame(
    {
        "A": [1, 2, 3, 3],
        "B": [1, 2, 3.5, 6],
        "C": [1, 1, 2, 2.5],
        "D": [1, 3, 4, 5.5],
    }
)

mock_solar = pd.DataFrame(
    {
        "A": [1, 2, 3, 4],
        "B": [1, 2, 4, 8],
    }
)

mock_wind = pd.DataFrame(
    {
        "C": [1, 1, 2, 3],
        "D": [1, 3, 5, 7],
    }
)

mock_curtailment_data = pd.DataFrame(
    {
        "A": [0, 0, 0, 1],
        "B": [0, 0, 0.5, 2],
        "C": [0, 0, 0, 0.5],
        "D": [0, 0, 1, 1.5],
    }
)
mock_curtailment_data["UTC"] = pd.date_range(start="2016-01-01", periods=4, freq="H")
mock_curtailment_data.set_index("UTC", inplace=True)

mock_curtailment = {
    "solar": mock_curtailment_data[["A", "B"]],
    "wind": mock_curtailment_data[["C"]],
    "wind_offshore": mock_curtailment_data[["D"]],
}

grid_attrs = {"plant": mock_plant}
scenario = MockScenario(grid_attrs, pg=mock_pg, solar=mock_solar, wind=mock_wind)


class TestCalculateCurtailmentTimeSeries(unittest.TestCase):
    def _check_curtailment_vs_expected(self, curtailment, expected):
        self.assertIsInstance(curtailment, dict)
        self.assertEqual(curtailment.keys(), expected.keys())
        for key in curtailment.keys():
            self.assertIsInstance(curtailment[key], pd.DataFrame)
            assert_array_equal(
                curtailment[key].index.to_numpy(), expected[key].index.to_numpy()
            )
            assert_array_equal(
                curtailment[key].columns.to_numpy(), expected[key].columns.to_numpy()
            )
            assert_array_equal(curtailment[key].to_numpy(), expected[key].to_numpy())

    def test_calculate_curtailment_time_series_solar(self):
        expected_return = {"solar": mock_curtailment["solar"]}
        curtailment = calculate_curtailment_time_series_by_resources(
            scenario, resources=("solar",)
        )
        self._check_curtailment_vs_expected(curtailment, expected_return)

    def test_calculate_curtailment_time_series_wind_argument_type(self):
        expected_return = {"wind": mock_curtailment["wind"]}
        arg = (
            (scenario, "wind"),
            (scenario, ("wind")),
            (scenario, ["wind"]),
            (scenario, {"wind"}),
        )
        for a in arg:
            curtailment = calculate_curtailment_time_series_by_resources(a[0], a[1])
            self._check_curtailment_vs_expected(curtailment, expected_return)

    def test_calculate_curtailment_time_series_default(self):
        expected_return = mock_curtailment
        curtailment = calculate_curtailment_time_series_by_resources(scenario)
        self._check_curtailment_vs_expected(curtailment, expected_return)

    def test_calculate_curtailment_time_series_solar_wind_tuple(self):
        expected_return = {r: mock_curtailment[r] for r in ("solar", "wind")}
        curtailment = calculate_curtailment_time_series_by_resources(
            scenario, resources=("solar", "wind")
        )
        self._check_curtailment_vs_expected(curtailment, expected_return)

    def test_calculate_curtailment_time_series_solar_wind_set(self):
        expected_return = {r: mock_curtailment[r] for r in ("solar", "wind")}
        curtailment = calculate_curtailment_time_series_by_resources(
            scenario, resources={"solar", "wind"}
        )
        self._check_curtailment_vs_expected(curtailment, expected_return)

    def test_calculate_curtailment_time_series_wind_solar_list(self):
        expected_return = {r: mock_curtailment[r] for r in ("solar", "wind")}
        curtailment = calculate_curtailment_time_series_by_resources(
            scenario, resources=["wind", "solar"]
        )
        self._check_curtailment_vs_expected(curtailment, expected_return)


class TestCheckResourceInScenario(unittest.TestCase):
    def test_error_geothermal_curtailment(self):
        with self.assertRaises(ValueError):
            calculate_curtailment_time_series_by_resources(
                scenario, resources=("geothermal",)
            )

    def test_error_no_solar(self):
        no_solar_mock_plant = {"plant_id": ["C", "D"], "type": ["wind", "wind"]}
        no_solar_grid_attrs = {"plant": no_solar_mock_plant}
        no_solar_scenario = MockScenario(no_solar_grid_attrs)
        with self.assertRaises(ValueError):
            calculate_curtailment_time_series_by_resources(
                no_solar_scenario, resources=("solar",)
            )


class TestCalculateCurtailmentPercentage(unittest.TestCase):
    def test_calculate_curtailment_percentage_solar(self):
        expected_return = 3.5 / 25
        total_curtailment = calculate_curtailment_percentage_by_resources(
            scenario, resources=("solar",)
        )
        self.assertAlmostEqual(total_curtailment, expected_return)

    def test_calculate_curtailment_percentage_wind(self):
        expected_return = 0.5 / 7
        total_curtailment = calculate_curtailment_percentage_by_resources(
            scenario, resources=("wind",)
        )
        self.assertAlmostEqual(total_curtailment, expected_return)

    def test_calculate_curtailment_percentage_wind_offshore(self):
        expected_return = 2.5 / 16
        total_curtailment = calculate_curtailment_percentage_by_resources(
            scenario, resources=("wind_offshore",)
        )
        self.assertAlmostEqual(total_curtailment, expected_return)

    def test_calculate_curtailment_percentage_default(self):
        expected_return = 6.5 / 48
        total_curtailment = calculate_curtailment_percentage_by_resources(scenario)
        self.assertAlmostEqual(total_curtailment, expected_return)

    def test_calculate_curtailment_percentage_solar_wind(self):
        expected_return = 4 / 32
        total_curtailment = calculate_curtailment_percentage_by_resources(
            scenario, resources=("solar", "wind")
        )
        self.assertAlmostEqual(total_curtailment, expected_return)


class TestSummarizeCurtailmentByBus(unittest.TestCase):
    def test_summarize_curtailment_by_bus(self):
        expected_return = {
            "solar": {1: 1, 2: 2.5},
            "wind": {3: 0.5},
            "wind_offshore": {4: 2.5},
        }
        bus_curtailment = summarize_curtailment_by_bus(scenario)
        self.assertEqual(bus_curtailment, expected_return)


class TestSummarizeCurtailmentByLocation(unittest.TestCase):
    def test_summarize_curtailment_by_location(self):
        expected_return = {
            "solar": {(47.6, -122.3): 3.5},
            "wind": {(37.8, -122.4): 0.5},
            "wind_offshore": {(37.8, -122.4): 2.5},
        }
        location_curtailment = summarize_curtailment_by_location(scenario)
        self.assertEqual(location_curtailment, expected_return)


class TestGetCurtailmentTimeSeries(unittest.TestCase):
    def test_get_curtailment_time_series(self):
        arg = [(scenario, "Washington"), (scenario, "Bay Area"), (scenario, "all")]
        expected_return = [
            pd.DataFrame(
                {
                    "solar_curtailment": mock_curtailment["solar"].sum(axis=1).values,
                },
                index=mock_solar.index,
            ),
            pd.DataFrame(
                {
                    "wind_curtailment": mock_curtailment["wind"].sum(axis=1).values,
                    "wind_offshore_curtailment": mock_curtailment["wind_offshore"]
                    .sum(axis=1)
                    .values,
                },
                index=mock_wind.index,
            ),
            pd.DataFrame(
                {
                    "solar_curtailment": mock_curtailment["solar"].sum(axis=1).values,
                    "wind_curtailment": mock_curtailment["wind"].sum(axis=1).values,
                    "wind_offshore_curtailment": mock_curtailment["wind_offshore"]
                    .sum(axis=1)
                    .values,
                },
                index=mock_pg.index,
            ),
        ]
        for a, e in zip(arg, expected_return):
            check_dataframe_matches(get_curtailment_time_series(*a), e)
