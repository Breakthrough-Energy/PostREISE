import numpy as np
import pandas as pd
from powersimdata.input.check import _check_grid_type, _check_time_series
from powersimdata.network.model import ModelImmutables
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state

from postreise.analyze.generation.costs import calculate_costs


def generate_emissions_stats(scenario, pollutant="carbon", method="simple"):
    """Calculate hourly emissions for each generator.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str pollutant: pollutant to analyze.
    :param str method: selected method to handle no-load fuel consumption.
    :return: (*pandas.DataFrame*) -- emissions data frame. index: timestamps, column:
        plant id, values: emission in tons.

    .. note:: method descriptions:

        - 'simple' uses a fixed ratio of CO2 to MWh
        - 'always-on' uses generator heat-rate curves including non-zero intercepts
        - 'decommit' uses generator heat-rate curves but de-commits generators if they
          are off (detected by pg < 1 MW).
    """
    _check_scenario_is_in_analyze_state(scenario)
    mi = ModelImmutables(scenario.info["grid_model"])
    allowed_methods = {
        "carbon": {"simple", "always-on", "decommit"},
        "nox": {"simple"},
        "so2": {"simple"},
    }
    emissions_per_mwh = {
        "carbon": mi.plants["carbon_per_mwh"],
        "nox": mi.plants["nox_per_mwh"],
        "so2": mi.plants["so2_per_mwh"],
    }

    if pollutant not in allowed_methods.keys():
        raise ValueError("Unknown pollutant for generate_emissions_stats()")
    if not isinstance(method, str):
        raise TypeError("method must be a str")
    if method not in allowed_methods[pollutant]:
        err_msg = f"method for {pollutant} must be one of: {allowed_methods[pollutant]}"
        raise ValueError(err_msg)

    pg = scenario.state.get_pg()
    grid = scenario.state.get_grid()
    emissions = pd.DataFrame(np.zeros_like(pg), index=pg.index, columns=pg.columns)

    if method == "simple":
        for fuel, val in emissions_per_mwh[pollutant].items():
            indices = (grid.plant["type"] == fuel).to_numpy()
            emissions.loc[:, indices] = pg.loc[:, indices] * val / 1000
    elif method in ("decommit", "always-on"):
        decommit = True if method == "decommit" else False

        costs = calculate_costs(
            pg=pg, gencost=grid.gencost["before"], decommit=decommit
        )
        heat = np.zeros_like(costs)

        for fuel, val in mi.plants["carbon_per_mmbtu"].items():
            indices = (grid.plant["type"] == fuel).to_numpy()
            heat[:, indices] = (
                costs.iloc[:, indices] / grid.plant["GenFuelCost"].values[indices]
            )
            emissions.loc[:, indices] = heat[:, indices] * val * 44 / 12 / 1000
    else:
        raise Exception("I should not be able to get here")

    return emissions


def summarize_emissions_by_bus(emissions, grid):
    """Calculate total emissions by generator type and bus.

    :param pandas.DataFrame emissions: hourly emissions by generator as returned by
        :func:`generate_emissions_stats`.
    :param powersimdata.input.grid.Grid grid: grid object.
    :return: (*dict*) -- annual emissions by fuel and bus.
    """

    _check_time_series(emissions, "emissions")
    if (emissions < -1e-3).any(axis=None):
        raise ValueError("emissions must be non-negative")

    _check_grid_type(grid)
    plant = grid.plant

    # sum by generator
    plant_totals = emissions.sum()
    # set up output data structure
    plant_buses = plant["bus_id"].unique()
    bus_totals_by_type = {
        f: {b: 0 for b in plant_buses}
        for f in grid.model_immutables.plants["carbon_resources"]
    }
    # sum by fuel by bus
    for p in plant_totals.index:
        plant_type = plant.loc[p, "type"]
        if plant_type not in grid.model_immutables.plants["carbon_resources"]:
            continue
        plant_bus = plant.loc[p, "bus_id"]
        bus_totals_by_type[plant_type][plant_bus] += plant_totals.loc[p]
    # filter out buses whose emissions are zero
    bus_totals_by_type = {
        r: {b: v for b, v in bus_totals_by_type[r].items() if v > 0}
        for r in grid.model_immutables.plants["carbon_resources"]
    }

    return bus_totals_by_type
