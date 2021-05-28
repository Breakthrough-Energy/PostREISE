from bokeh.io import show
from powersimdata import Scenario

from postreise.plot.plot_interconnection_map import map_interconnections

scenario = Scenario(3287)
grid = scenario.get_grid()

transmission_map = map_interconnections(grid)
show(transmission_map)
