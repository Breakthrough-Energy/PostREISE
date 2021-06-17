from bokeh.io import show
from powersimdata import Scenario

from postreise.plot.plot_lmp_map import map_lmp

scenario = Scenario(3287)

lmp_map = map_lmp(scenario, lmp_min=10, lmp_max=35, num_ticks=6, scale_factor=1.5)
show(lmp_map)
