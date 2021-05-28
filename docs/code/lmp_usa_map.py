from bokeh.io import show
from powersimdata import Scenario

from postreise.plot.plot_lmp_map import map_lmp

scenario = Scenario(3287)

lmp_map = map_lmp(scenario)
show(lmp_map)
