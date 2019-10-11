import numpy as np
from numpy.polynomial.polynomial import polyval
import pandas as pd

from powersimdata.input.grid import Grid

# MMBTu of fuel per hour to metric tons of CO2 per hour
# Source: https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references
# = (Heat rate MMBTu/h) * (kg C/mmbtu) * (mass ratio CO2/C) / (kg to tonnes)
carbon_intensities = {
    'coal': 26.05,
    'dfo': 20.31,
    'ng': 14.46,
    }

def generate_carbon_stats(scenario):
    """Generates carbon statistics from the input generation data.

    :param powersimdata.scenario.analyze.Analyze scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- carbon data frame.
    """

    pg = scenario.get_pg()
    grid = scenario.get_grid()

    costs = calc_costs(pg, grid.gencost)
    heat = np.zeros_like(costs)
    carbon = pd.DataFrame(np.zeros_like(pg), index=pg.index, columns=pg.columns)

    for fuel, val in carbon_intensities.items():
        indices = (grid.plant['type'] == fuel).to_numpy()
        heat[:, indices] = (
            costs[:, indices] / grid.plant['GenFuelCost'].values[indices])
        carbon.loc[:, indices] = heat[:, indices] * val * 44/12 / 1000

    return carbon

def calc_costs(pg, gencost):
    """Calculates individual generator costs at given powers.

    :param pandas.DataFrame pg: Generation solution data frame.
    :param pandas.DataFrame gencost: cost curve polynomials.
    :return: (*pandas.DataFrame*) -- data frame of costs.
    """

    _check_gencost(gencost)
    _check_pg(pg)

    # get ordered polynomial coefficients in columns, discarding non-coeff data
    #coefs = gencost.values.T[-2:3:-1,:]
    #coefs = gencost[['c0', 'c1', 'c2']].values.T
    num_coefs = gencost['n'].iloc[0]
    coef_columns = ['c' + str(i) for i in range(num_coefs)]
    coefs = gencost[coef_columns].to_numpy().T

    # elementwise, evaluate polynomial where x = value
    costs = polyval(pg.to_numpy(), coefs, tensor=False)

    return costs

def _check_gencost(gencost):
    """Checks that gencost is specified properly
    """

    # check for nonempty dataframe
    if not isinstance(gencost, pd.DataFrame):
        raise TypeError('gencost must be a pandas.DataFrame')
    if not gencost.shape[0] > 0:
        raise ValueError('gencost must have at least one row')

    # check for proper columns
    required_columns = ('type', 'n')
    for r in required_columns:
        if not r in gencost.columns:
            raise ValueError('gencost must have column ' + r)

    # check that gencosts are all specified as type 2 (polynomial)
    cost_type = gencost['type']
    if not cost_type.where(cost_type == 2).equals(cost_type):
        raise ValueError('each gencost must be type 2 (polynomial)')

    # check that all gencosts are specified as same order polynomial
    if not (gencost['n'].nunique() == 1):
        raise ValueError('all polynomials must be of same order')

    # check that this order is an integer > 0
    n = gencost['n'].iloc[0]
    if not isinstance(n, (int, np.integer)):
        print(type(n))
        raise TypeError('polynomial degree must be specified as an int')
    if n < 1:
        raise ValueError('polynomial must be at least of order 1 (constant)')

    # check that the right columns are here for this dataframe
    coef_columns = ['c' + str(i) for i in range(n)]
    for c in coef_columns:
        if not c in gencost.columns:
            err_msg = 'gencost of order {0} must have column {1}'.format(n, c)
            raise ValueError(err_msg)

def _check_pg(pg):
    """Checks that pg is specified properly
    """

    # check for nonempty dataframe
    if not isinstance(pg, pd.DataFrame):
        raise TypeError('pg must be a pandas.DataFrame')
    if not pg.shape[0] > 0:
        raise ValueError('pg must have at least one row')
    if not pg.shape[1] > 0:
        raise ValueError('pg must have at least one column')
    # check to ensure that all values are non-negative
    if np.sum((pg < 0).to_numpy().ravel()) > 0:
        raise ValueError('pg must be non-negative')