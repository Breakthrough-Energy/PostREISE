import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_array_almost_equal
from powersimdata.tests.mock_grid import MockGrid
from powersimdata.tests.mock_scenario import MockScenario

from postreise.analyze.generation.emissions import (
    generate_emissions_stats,
    summarize_emissions_by_bus,
)


@pytest.fixture
def mock_plant():
    # plant_id is the index
    return {
        "plant_id": [101, 102, 103, 104, 105],
        "bus_id": [1001, 1002, 1003, 1004, 1005],
        "type": ["solar", "wind", "ng", "coal", "dfo"],
        "GenFuelCost": [0, 0, 3.3, 4.4, 5.5],
    }


@pytest.fixture
def mock_gencost():
    # plant_id is the index
    return {
        "plant_id": [101, 102, 103, 104, 105],
        "type": [2] * 5,
        "startup": [0] * 5,
        "shutdown": [0] * 5,
        "n": [3] * 5,
        "c2": [1, 2, 3, 4, 5],
        "c1": [10, 20, 30, 40, 50],
        "c0": [100, 200, 300, 400, 500],
        "interconnect": ["Western"] * 5,
    }


@pytest.fixture
def mock_pg(mock_plant):
    return pd.DataFrame(
        {
            plant_id: [(i + 1) * p for p in range(4)]
            for i, plant_id in enumerate(mock_plant["plant_id"])
        },
        index=pd.date_range("2019-01-01", periods=4, freq="H"),
    )


@pytest.fixture
def scenario(mock_plant, mock_gencost, mock_pg):
    return MockScenario(
        grid_attrs={"plant": mock_plant, "gencost_before": mock_gencost},
        pg=mock_pg,
    )


def _test_emissions_structure(emissions, mock_plant, pg):
    plant = pd.DataFrame(mock_plant)
    plant.set_index("plant_id", inplace=True)

    # check data frame structure
    err_msg = "generate_emissions_stats should return a data frame"
    assert isinstance(emissions, pd.DataFrame), err_msg
    for a, b in zip(pg.index.to_numpy(), emissions.index.to_numpy()):
        assert a == b, "emissions and pg should have same index"
    for a, b in zip(pg.columns.to_numpy(), emissions.columns.to_numpy()):
        assert a == b, "emissions and pg should have same columns"

    # sanity check values
    emissions_from_wind = plant[plant.type == "wind"].index.values
    err_msg = "Wind farm does not emit emissions"
    assert emissions[emissions_from_wind[0]].sum() == 0, err_msg
    emissions_from_solar = plant[plant.type == "solar"].index.values
    err_msg = "Solar plant does not emit emissions"
    assert emissions[emissions_from_solar[0]].sum() == 0, err_msg
    negative_emissions_count = np.sum((emissions < 0).to_numpy().ravel())
    assert negative_emissions_count == 0, "No plant should emit negative emissions"


class TestCarbonCalculation:
    def test_carbon_calc_always_on(self, scenario, mock_plant):

        carbon = generate_emissions_stats(scenario, method="always-on")
        _test_emissions_structure(carbon, mock_plant, scenario.state.get_pg())

        # check specific values
        expected_values = np.array(
            [
                [0, 0, 4.82, 8.683333, 6.77],
                [0, 0, 6.6998, 13.546000, 11.8475],
                [0, 0, 9.4472, 21.1873333, 20.3100],
                [0, 0, 13.0622, 31.6073333, 32.1575],
            ]
        )
        assert_array_almost_equal(
            expected_values, carbon.to_numpy(), err_msg="Values do not match expected"
        )

    def test_carbon_calc_decommit(self, scenario, mock_plant):

        carbon = generate_emissions_stats(scenario, method="decommit")
        _test_emissions_structure(carbon, mock_plant, scenario.state.get_pg())

        # check specific values
        expected_values = np.array(
            [
                [0, 0, 0, 0, 0],
                [0, 0, 6.6998, 13.546000, 11.8475],
                [0, 0, 9.4472, 21.1873333, 20.3100],
                [0, 0, 13.0622, 31.6073333, 32.1575],
            ]
        )
        assert_array_almost_equal(
            expected_values, carbon.to_numpy(), err_msg="Values do not match expected"
        )

    def test_carbon_calc_simple(self, scenario, mock_plant):

        carbon = generate_emissions_stats(scenario, method="simple")
        _test_emissions_structure(carbon, mock_plant, scenario.state.get_pg())

        # check specific values
        expected_values = np.array(
            [
                [0, 0, 0, 0, 0],
                [0, 0, 1.407, 4.004, 4.2],
                [0, 0, 2.814, 8.008, 8.4],
                [0, 0, 4.221, 12.012, 12.6],
            ]
        )
        assert_array_almost_equal(
            expected_values, carbon.to_numpy(), err_msg="Values do not match expected"
        )


class TestNOxCalculation:
    def test_calculate_nox_simple(self, scenario):
        expected_values = np.array(
            [
                [0, 0, 0, 0, 0],
                [0, 0, 0.000537, 0.002632, 0.007685],
                [0, 0, 0.001074, 0.005264, 0.015370],
                [0, 0, 0.001611, 0.007896, 0.023055],
            ]
        )
        nox = generate_emissions_stats(scenario, pollutant="nox", method="simple")
        assert_array_almost_equal(
            expected_values, nox.to_numpy(), err_msg="Values do not match expected"
        )

    def test_calculate_nox_disallowed_method(self, scenario):
        with pytest.raises(ValueError):
            generate_emissions_stats(scenario, pollutant="nox", method="decommit")


class TestSO2Calculation:
    def test_calculate_so2_simple(self, scenario):
        expected_values = np.array(
            [
                [0, 0, 0, 0, 0],
                [0, 0, 3.0000e-05, 3.8600e-03, 1.0945e-02],
                [0, 0, 6.0000e-05, 7.7200e-03, 2.1890e-02],
                [0, 0, 9.0000e-05, 1.1580e-02, 3.2835e-02],
            ]
        )
        nox = generate_emissions_stats(scenario, pollutant="so2", method="simple")
        assert_array_almost_equal(
            expected_values, nox.to_numpy(), err_msg="Values do not match expected"
        )

    def test_calculate_so2_disallowed_method(self, scenario):
        with pytest.raises(ValueError):
            generate_emissions_stats(scenario, pollutant="so2", method="always-on")


class TestEmissionsSummarization:
    def test_emissions_summarization(self, mock_pg, mock_plant):
        # setup
        pg = pd.DataFrame(mock_pg).iloc[:3, :]
        plant = pd.DataFrame(mock_plant)
        plant.set_index("plant_id", inplace=True)
        input_carbon_values = [
            [0, 0, 6.6998, 13.546000, 11.8475],
            [0, 0, 9.4472, 21.1873333, 20.3100],
            [0, 0, 13.0622, 31.6073333, 32.1575],
        ]
        input_carbon = pd.DataFrame(
            input_carbon_values, index=pg.index, columns=pg.columns
        )
        expected_sum = {
            "coal": {1004: 66.3406666},
            "ng": {1003: 29.2092},
            "dfo": {1005: 64.315},
        }

        # calculation
        summation = summarize_emissions_by_bus(
            input_carbon, MockGrid(grid_attrs={"plant": mock_plant})
        )

        # checks
        err_msg = "summarize_emissions_by_bus didn't return a dict"
        assert isinstance(summation, dict), err_msg
        err_msg = "summarize_emissions_by_bus didn't return the right dict keys"
        assert set(summation.keys()) == expected_sum.keys(), err_msg
        for k in expected_sum.keys():
            err_msg = "summation not correct for fuel " + k
            assert expected_sum[k].keys() == summation[k].keys(), err_msg
            for bus in expected_sum[k]:
                err_msg = "summation not correct for bus " + str(bus)
                assert expected_sum[k][bus] == pytest.approx(summation[k][bus]), err_msg
