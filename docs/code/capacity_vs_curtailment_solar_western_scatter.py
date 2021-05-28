from powersimdata import Scenario
from powersimdata.utility.helpers import PrintManager

from postreise.plot.plot_scatter_capacity_vs_curtailment import (
    plot_scatter_capacity_vs_curtailment,
)

with PrintManager():
    scenario = Scenario(3287)
    plot_scatter_capacity_vs_curtailment(scenario, "Western", "solar", percentage=True)
