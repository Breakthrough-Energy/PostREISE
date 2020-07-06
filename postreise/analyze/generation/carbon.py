import numpy as np
from numpy.polynomial.polynomial import polyval
import pandas as pd

from powersimdata.scenario.scenario import Scenario
from powersimdata.scenario.analyze import Analyze

# For simple methods:
# MWh to metric tons of CO2
# Source: IPCC Special Report on Renewable Energy Sources and Climate Change
# Mitigation (2011), Annex II: Methodology, Table A.II.4, 50th percentile
# http://www.ipcc-wg3.de/report/IPCC_SRREN_Annex_II.pdf
carbon_per_mwh = {
    "coal": 1001,
    "dfo": 840,
    "ng": 469,
}

# For curve methods:
# MMBTu of fuel per hour to metric tons of CO2 per hour
# Source: https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references
# = (Heat rate MMBTu/h) * (kg C/mmbtu) * (mass ratio CO2/C) / (kg to tonnes)
carbon_per_mmbtu = {
    "coal": 26.05,
    "dfo": 20.31,
    "ng": 14.46,
}


def generate_carbon_stats(scenario, method="simple"):
    """Generates carbon statistics from the input generation data. Method
    descriptions: 'simple' uses a fixed ratio of CO2 to MWh, 'always-on' uses
    generator heat-rate curves including non-zero intercepts, 'decommit' uses
    generator heat-rate curves but de-commits generators if they are off
    (detected by pg < 1 MW).

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str method: selected method to handle no-load fuel consumption.
    :return: (*pandas.DataFrame*) -- carbon data frame.
    """

    allowed_methods = ("simple", "always-on", "decommit")
    if not isinstance(method, str):
        raise TypeError("method must be a str")
    if method not in allowed_methods:
        raise ValueError("Unknown method for generate_carbon_stats()")

    if not isinstance(scenario, Scenario):
        raise TypeError("scenario must be a Scenario object")
    if not isinstance(scenario.state, Analyze):
        raise ValueError("scenario.state must be Analyze")

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
    fossil_fuels = {"coal", "dfo", "ng"}
    plant_buses = plant["bus_id"].unique()
    bus_totals_by_type = {f: {b: 0 for b in plant_buses} for f in fossil_fuels}
    # sum by fuel by bus
    for p in plant_totals.index:
        plant_type = plant.loc[p, "type"]
        if plant_type not in fossil_fuels:
            continue
        plant_bus = plant.loc[p, "bus_id"]
        bus_totals_by_type[plant_type][plant_bus] += plant_totals.loc[p]
    # filter out buses whose carbon is zero
    bus_totals_by_type = {
        f: {b: v for b, v in bus_totals_by_type[f].items() if v > 0}
        for f in fossil_fuels
    }

    return bus_totals_by_type


def calc_costs(pg, gencost, decommit=False):
    """Calculates individual generator costs at given powers. If decommit is
    True, costs will be zero below the decommit threshold (1 MW).

    :param pandas.DataFrame pg: Generation solution data frame.
    :param pandas.DataFrame gencost: cost curve polynomials.
    :param boolean decommit: Whether to decommit generator at very low power.
    :return: (*pandas.DataFrame*) -- data frame of costs.
    """

    decommit_threshold = 1

    _check_gencost(gencost)
    _check_time_series(pg, "pg")

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


def _check_gencost(gencost):
    """Checks that gencost is specified properly.

    :param pandas.DataFrame gencost: cost curve polynomials.
    """

    # check for nonempty dataframe
    if not isinstance(gencost, pd.DataFrame):
        raise TypeError("gencost must be a pandas.DataFrame")
    if not gencost.shape[0] > 0:
        raise ValueError("gencost must have at least one row")

    # check for proper columns
    required_columns = ("type", "n")
    for r in required_columns:
        if r not in gencost.columns:
            raise ValueError("gencost must have column " + r)

    # check that gencosts are all specified as type 2 (polynomial)
    cost_type = gencost["type"]
    if not cost_type.where(cost_type == 2).equals(cost_type):
        raise ValueError("each gencost must be type 2 (polynomial)")

    # check that all gencosts are specified as same order polynomial
    if not (gencost["n"].nunique() == 1):
        raise ValueError("all polynomials must be of same order")

    # check that this order is an integer > 0
    n = gencost["n"].iloc[0]
    if not isinstance(n, (int, np.integer)):
        print(type(n))
        raise TypeError("polynomial degree must be specified as an int")
    if n < 1:
        raise ValueError("polynomial must be at least of order 1 (constant)")

    # check that the right columns are here for this dataframe
    coef_columns = ["c" + str(i) for i in range(n)]
    for c in coef_columns:
        if c not in gencost.columns:
            err_msg = "gencost of order {0} must have column {1}".format(n, c)
            raise ValueError(err_msg)


def _check_time_series(df, label, tolerance=1e-3):
    """Checks that a time series dataframe is specified properly.

    :param pandas.DataFrame df: dataframe to check.
    :param str label: Name of dataframe (used for error messages).
    :param float tolerance: tolerance value for checking non-negativity.
    :raises TypeError: if df is not a dataframe or label is not a str.
    :raises ValueError: if df does not have at least one row and one column, or
        if it contains values that are more negative than the tolerance allows.
    """
    if not isinstance(label, str):
        raise TypeError("label must be a str")

    # check for nonempty dataframe
    if not isinstance(df, pd.DataFrame):
        raise TypeError(label + " must be a pandas.DataFrame")
    if not df.shape[0] > 0:
        raise ValueError(label + " must have at least one row")
    if not df.shape[1] > 0:
        raise ValueError(label + " must have at least one column")
    # check to ensure that all values are non-negative
    if any((df < -1 * tolerance).to_numpy().ravel()):
        raise ValueError(label + " must be non-negative")
