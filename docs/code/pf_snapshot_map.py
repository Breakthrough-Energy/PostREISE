import pandas as pd
from bokeh.io import show
from powersimdata import Scenario

from postreise.plot.plot_powerflow_snapshot import plot_powerflow_snapshot

scenario = Scenario(3287)
grid = scenario.get_grid()

pf_map = plot_powerflow_snapshot(
    scenario, pd.Timestamp(2016, 11, 2, 22), legend_font_size=20
)
show(pf_map)
