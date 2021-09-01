from powersimdata import Scenario
from powersimdata.utility.helpers import PrintManager

from postreise.plot.plot_scatter_capacity_vs_cost_curve_slope import (
    plot_scatter_capacity_vs_cost_curve_slope,
)

with PrintManager():
    scenario = Scenario(3287)
    plot_scatter_capacity_vs_cost_curve_slope(scenario, "Eastern", "coal")
