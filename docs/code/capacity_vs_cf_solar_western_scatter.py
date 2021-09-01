from powersimdata import Scenario
from powersimdata.utility.helpers import PrintManager

from postreise.plot.plot_scatter_capacity_vs_capacity_factor import (
    plot_scatter_capacity_vs_capacity_factor,
)

with PrintManager():
    scenario = Scenario(1171)
    plot_scatter_capacity_vs_capacity_factor(
        scenario, "Western", "solar", percentage=True
    )
