import numpy as np
import pandas as pd
from numpy.polynomial.polynomial import polyval
from powersimdata.input.check import _check_gencost, _check_time_series
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state


def calculate_costs(
    scenario=None, pg=None, gencost=None, decommit=False, decommit_threshold=1
):
    """Calculate individual generator costs at given powers. If decommit is
    True, costs will be zero below the decommit threshold (1 MW).
    Either ``scenario`` XOR (``pg`` AND ``gencost``) must be specified.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario to analyze.
    :param pandas.DataFrame pg: Generation solution data frame.
    :param pandas.DataFrame gencost: cost curve polynomials.
    :param bool decommit: Whether to decommit generator at low power.
    :param int/float decommit_threshold: The power (MW) below which generators are
        assumed to be 'decommitted', and costs are zero (if ``decommit`` is True).
    :raises ValueError: if not (``scenario`` XOR (``pg`` AND ``gencost``)) is specified,
        or if ``pg`` is passed and has negative values.
    :return: (*pandas.DataFrame*) -- data frame of costs.
        Index is hours, columns are plant IDs, values are $/hour.
    """

    # Check that we've appropriately specified `scenario` XOR (`pg` AND `gencost`)
    if not ((scenario is not None) ^ (pg is not None and gencost is not None)):
        raise ValueError("Either scenario XOR (pg AND gencost) must be specified")
    if scenario is not None:
        _check_scenario_is_in_analyze_state(scenario)
        pg = scenario.state.get_pg()
        gencost = scenario.state.get_grid().gencost["before"]
    else:
        _check_gencost(gencost)
        _check_time_series(pg, "PG")
        if (pg < -1e-3).any(axis=None):
            raise ValueError("PG must be non-negative")
    # get ordered polynomial coefficients in columns, discarding non-coefficient data
    num_coefficients = gencost["n"].iloc[0]
    coefficient_columns = [f"c{i}" for i in range(num_coefficients)]
    coefficients = gencost[coefficient_columns].to_numpy().T

    # elementwise, evaluate polynomial where x = value
    costs = polyval(pg.to_numpy(), coefficients, tensor=False)

    if decommit:
        # mask values where pg is 0 to 0 cost (assume uncommitted, no cost)
        costs = np.where(pg.to_numpy() < decommit_threshold, 0, costs)

    # Finally, convert to dataframe with shape that matches `pg`
    costs = pd.DataFrame(costs, columns=pg.columns, index=pg.index)
    return costs
