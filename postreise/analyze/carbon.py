import numpy as np
from numpy.polynomial.polynomial import polyval
import pandas as pd

def generate_carbon_stats(pg, grid, name=None):
    """Generates carbon statistics from the input generation data.
    
    :param pandas.DataFrame pg: Generation solution data frame.
    :param PowerSimData.Grid grid: Grid object containing gen costs & types.
    :param string name: filename of output. If None, no file is written.
    :return: (*pandas.DataFrame*) -- data frame with ?
    """
    
    costs = calc_costs(pg, grid.gencost)
    heat = np.zeros_like(costs)
    carbon = pd.DataFrame(np.zeros_like(pg), index=pg.index, columns=pg.columns)

    # MMBTu of fuel to metric tons of CO2
    # Source: https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references
    # = (Heat rate) * (kg C/mmbtu) * (mass ratio CO2/C) / (kg to metric tons)
    carbon_intensities = {
        'coal': 26.05,
        'dfo': 20.31,
        'ng': 14.46,
        }
    for fuel, val in carbon_intensities.items():
        indices = (grid.plant['type'] == fuel)
        heat[:, indices] = (
            costs[:, indices] / grid.plant['GenFuelCost'].values[indices])
        carbon.loc[:, indices] = heat[:, indices] * val * 44/12 / 1000
    
    return carbon
    
def calc_costs(pg, gencost):
    """Calculates individual generator costs at given powers.
    
    :param pandas.DataFrame pg: Generation solution data frame.
    :param pandas.DataFrame gencost: cost curve polynomials.
    :return: (*pandas.DataFrame*) -- data frame of costs
    """
    
    if not isinstance(gencost, pd.DataFrame):
        raise TypeError('gencost must be a pandas.DataFrame (for now)')
        
    # check that gencosts are all specified as type 2 (polynomial)
    cost_type = gencost['type']
    if not cost_type.where(cost_type == 2).equals(cost_type):
        raise ValueError('Not all polynomials!')
    # get ordered polynomial coefficients in columns, discarding non-coeff data
    coefs = gencost.values.T[-2:3:-1,:]
    # elementwise, evaluate polynomial where x = value
    costs = polyval(pg.values, coefs, tensor=False)
    
    return costs