import unittest

import pandas as pd
from powersimdata.input.check import _check_epsilon
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state
from powersimdata.tests.mock_scenario import MockScenario

from postreise.analyze.generation.binding import (
    pmax_constraints,
    pmin_constraints,
    ramp_constraints,
)


class TestCheckScenario(unittest.TestCase):
    def test_good_scenario(self):
        mock_plant = {
            "plant_id": ["A", "B", "C", "D"],
            "ramp_30": [2.5, 5, 10, 25],
        }
        mock_scenario = MockScenario({"plant": mock_plant})
        _check_scenario_is_in_analyze_state(mock_scenario)

    def test_bad_scenario_type(self):
        with self.assertRaises(TypeError):
            _check_scenario_is_in_analyze_state("307")

    def test_bad_scenario_state(self):
        mock_plant = {
            "plant_id": ["A", "B", "C", "D"],
            "ramp_30": [2.5, 5, 10, 25],
        }
        mock_scenario = MockScenario({"plant": mock_plant})
        mock_scenario.state = "Create"
        with self.assertRaises(ValueError):
            _check_scenario_is_in_analyze_state(mock_scenario)


class TestCheckEpsilon(unittest.TestCase):
    def test_good_float_value(self):
        _check_epsilon(5e-4)

    def test_good_int_value(self):
        _check_epsilon(1)

    def test_zero(self):
        _check_epsilon(0)

    def test_bad_type(self):
        with self.assertRaises(TypeError):
            _check_epsilon("0.001")

    def test_bad_value(self):
        with self.assertRaises(ValueError):
            _check_epsilon(-0.001)


class TestRampConstraints(unittest.TestCase):
    def setUp(self):
        mock_plant = {
            "plant_id": ["A", "B", "C", "D"],
            "ramp_30": [2.5, 5, 10, 25],
        }
        grid_attrs = {"plant": mock_plant}
        mock_pg = pd.DataFrame(
            {
                "A": [100, 104, (99 + 1e-4), (104 + 1e-4 - 1e-7)],
                "B": [50, 45, 50, 45],
                "C": [20, 40, 60, 80],
                "D": [200, 150, 100, 50],
            }
        )
        self.mock_scenario = MockScenario(grid_attrs, pg=mock_pg)
        self.default_expected = pd.DataFrame(
            {
                "UTC": pd.date_range(start="2016-01-01", periods=4, freq="H"),
                "A": [False, False, True, True],
                "B": [False, False, False, False],
                "C": [False, True, True, True],
                "D": [False, True, True, True],
            }
        )
        self.default_expected.set_index("UTC", inplace=True)

    def get_default_expected(self):
        return self.default_expected.copy()

    def test_ramp_constraints_default(self):
        binding_ramps = ramp_constraints(self.mock_scenario)
        expected = self.get_default_expected()
        assert binding_ramps.equals(expected)

    def test_ramp_constraints_spec_epsilon1(self):
        # Same results as test_ramp_constraints_default
        binding_ramps = ramp_constraints(self.mock_scenario, epsilon=1e-3)
        expected = self.get_default_expected()
        assert binding_ramps.equals(expected)

    def test_ramp_constraints_spec_epsilon2(self):
        # One differece from test_ramp_constraints_default: ('A', 't3')
        binding_ramps = ramp_constraints(self.mock_scenario, epsilon=1e-6)
        expected = self.get_default_expected()
        expected.loc["2016-01-01 02:00:00", "A"] = False
        assert binding_ramps.equals(expected)

    def test_ramp_constraints_spec_epsilon3(self):
        # Two differeces from test_ramp_constraints_default: ('A', ['t3'/'t4'])
        binding_ramps = ramp_constraints(self.mock_scenario, epsilon=1e-9)
        expected = self.get_default_expected()
        expected.loc[:, "A"] = False
        assert binding_ramps.equals(expected)


class TestPminConstraints(unittest.TestCase):
    def setUp(self):
        mock_plant = {
            "plant_id": ["A", "B", "C", "D"],
            "Pmin": [0, 10, 20, 30],
        }
        grid_attrs = {"plant": mock_plant}
        mock_pg = pd.DataFrame(
            {
                "A": [0, 0],
                "B": [(10 + 1e-4), 15],
                "C": [25, (20 + 1e-7)],
                "D": [35, 40],
            }
        )
        self.mock_scenario = MockScenario(grid_attrs, pg=mock_pg)
        self.default_expected = pd.DataFrame(
            {
                "UTC": pd.date_range(start="2016-01-01", periods=2, freq="H"),
                "A": [True, True],
                "B": [True, False],
                "C": [False, True],
                "D": [False, False],
            }
        )
        self.default_expected.set_index("UTC", inplace=True)

    def get_default_expected(self):
        return self.default_expected.copy()

    def test_pmin_constraints_default(self):
        binding_pmins = pmin_constraints(self.mock_scenario)
        expected = self.get_default_expected()
        assert binding_pmins.equals(expected)

    def test_pmin_constraints_default_spec_epsilon1(self):
        binding_pmins = pmin_constraints(self.mock_scenario, epsilon=1e-3)
        expected = self.get_default_expected()
        assert binding_pmins.equals(expected)

    def test_pmin_constraints_default_spec_epsilon2(self):
        binding_pmins = pmin_constraints(self.mock_scenario, epsilon=1e-6)
        expected = self.get_default_expected()
        expected.loc["2016-01-01 00:00:00", "B"] = False
        assert binding_pmins.equals(expected)

    def test_pmin_constraints_default_spec_epsilon3(self):
        binding_pmins = pmin_constraints(self.mock_scenario, epsilon=1e-9)
        expected = self.get_default_expected()
        expected.loc["2016-01-01 00:00:00", "B"] = False
        expected.loc["2016-01-01 01:00:00", "C"] = False
        assert binding_pmins.equals(expected)


class TestPmaxConstraints(unittest.TestCase):
    def setUp(self):
        mock_plant = {
            "plant_id": ["A", "B", "C", "D"],
            "Pmax": [50, 75, 100, 200],
        }
        grid_attrs = {"plant": mock_plant}
        mock_pg = pd.DataFrame(
            {
                "A": [50, 50],
                "B": [(75 - 1e-4), 70],
                "C": [90, (100 - 1e-7)],
                "D": [150, 175],
            }
        )
        self.mock_scenario = MockScenario(grid_attrs, pg=mock_pg)
        self.default_expected = pd.DataFrame(
            {
                "UTC": pd.date_range(start="2016-01-01", periods=2, freq="H"),
                "A": [True, True],
                "B": [True, False],
                "C": [False, True],
                "D": [False, False],
            }
        )
        self.default_expected.set_index("UTC", inplace=True)

    def get_default_expected(self):
        return self.default_expected.copy()

    def test_pmax_constraints_default(self):
        binding_pmaxs = pmax_constraints(self.mock_scenario)
        expected = self.get_default_expected()
        assert binding_pmaxs.equals(expected)

    def test_pmax_constraints_default_sepc_epsilon1(self):
        binding_pmaxs = pmax_constraints(self.mock_scenario, epsilon=1e-3)
        expected = self.get_default_expected()
        assert binding_pmaxs.equals(expected)

    def test_pmax_constraints_default_sepc_epsilon2(self):
        binding_pmaxs = pmax_constraints(self.mock_scenario, epsilon=1e-6)
        expected = self.get_default_expected()
        expected.loc["2016-01-01 00:00:00", "B"] = False
        assert binding_pmaxs.equals(expected)

    def test_pmax_constraints_default_sepc_epsilon3(self):
        binding_pmaxs = pmax_constraints(self.mock_scenario, epsilon=1e-9)
        expected = self.get_default_expected()
        expected.loc["2016-01-01 00:00:00", "B"] = False
        expected.loc["2016-01-01 01:00:00", "C"] = False
        assert binding_pmaxs.equals(expected)
