import numpy as np
from numpy.polynomial.polynomial import polyval
import pandas as pd

from powersimdata.scenario.scenario import Scenario
from powersimdata.scenario.analyze import Analyze
from postreise.analyze.check import (
    _check_scenario_is_in_analyze_state,
    _check_gencost,
    _check_time_series,
)
from powersimdata.network.usa_tamu.constants.plants import (
    carbon_resources,
    carbon_per_mwh,
    carbon_per_mmbtu,
)


def generate_carbon_stats(scenario, method="simple"):
    """Generate carbon statistics from the input generation data. Method
    descriptions: 'simple' uses a fixed ratio of CO2 to MWh, 'always-on' uses
    generator heat-rate curves including non-zero intercepts, 'decommit' uses
    generator heat-rate curves but de-commits generators if they are off
    (detected by pg < 1 MW).

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str method: selected method to handle no-load fuel consumption.
    :return: (*pandas.DataFrame*) -- carbon data frame.
    """
    _check_scenario_is_in_analyze_state(scenario)

    allowed_methods = ("simple", "always-on", "decommit")
    if not isinstance(method, str):
        raise TypeError("method must be a str")
    if method not in allowed_methods:
        raise ValueError("Unknown method for generate_carbon_stats()")

    pg = scenario.state.get_pg()
    grid = scenario.state.get_grid()
    carbon = pd.DataFrame(np.zeros_like(pg), index=pg.index, columns=pg.columns)

    if method == "simple":
        for fuel, val in carbon_per_mwh.items():
            indices = (grid.plant["type"] == fuel).to_numpy()
            carbon.loc[:, indices] = pg.loc[:, indices] * val / 1000
    elif method in ("decommit", "always-on"):
        decommit = True if method == "decommit" else False

        costs = calc_costs(pg, grid.gencost["before"], decommit=decommit)
        heat = np.zeros_like(costs)

        for fuel, val in carbon_per_mmbtu.items():
            indices = (grid.plant["type"] == fuel).to_numpy()
            heat[:, indices] = (
                costs[:, indices] / grid.plant["GenFuelCost"].values[indices]
            )
            carbon.loc[:, indices] = heat[:, indices] * val * 44 / 12 / 1000
    else:
        raise Exception("I should not be able to get here")

    return carbon


def summarize_carbon_by_bus(carbon, plant):
    """Summarize time series carbon dataframe by type and bus.

    :param pandas.DataFrame carbon: Hourly carbon by generator.
    :param pandas.DataFrame plant: Generator specification table.
    :return: (*dict*) -- Annual carbon emissions by fuel and bus.
    """

    _check_time_series(carbon, "carbon")

    # sum by generator
    plant_totals = carbon.sum()
    # set up output data structure
    plant_buses = plant["bus_id"].unique()
    bus_totals_by_type = {f: {b: 0 for b in plant_buses} for f in carbon_resources}
    # sum by fuel by bus
    for p in plant_totals.index:
        plant_type = plant.loc[p, "type"]
        if plant_type not in carbon_resources:
            continue
        plant_bus = plant.loc[p, "bus_id"]
        bus_totals_by_type[plant_type][plant_bus] += plant_totals.loc[p]
    # filter out buses whose carbon is zero
    bus_totals_by_type = {
        r: {b: v for b, v in bus_totals_by_type[r].items() if v > 0}
        for r in carbon_resources
    }

    return bus_totals_by_type


def calc_costs(pg, gencost, decommit=False):
    """Calculate individual generator costs at given powers. If decommit is
    True, costs will be zero below the decommit threshold (1 MW).

    :param pandas.DataFrame pg: Generation solution data frame.
    :param pandas.DataFrame gencost: cost curve polynomials.
    :param boolean decommit: Whether to decommit generator at very low power.
    :return: (*pandas.DataFrame*) -- data frame of costs.
    """

    decommit_threshold = 1

    _check_gencost(gencost)
    _check_time_series(pg, "PG")

    # get ordered polynomial coefficients in columns, discarding non-coeff data
    # coefs = gencost.values.T[-2:3:-1,:]
    # coefs = gencost[['c0', 'c1', 'c2']].values.T
    num_coefs = gencost["n"].iloc[0]
    coef_columns = ["c" + str(i) for i in range(num_coefs)]
    coefs = gencost[coef_columns].to_numpy().T

    # elementwise, evaluate polynomial where x = value
    costs = polyval(pg.to_numpy(), coefs, tensor=False)

    if decommit:
        # mask values where pg is 0 to 0 cost (assume uncommitted, no cost)
        costs = np.where(pg.to_numpy() < decommit_threshold, 0, costs)

    return costs
