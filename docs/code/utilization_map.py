from bokeh.io import show
from powersimdata import Scenario

from postreise.plot.plot_utilization_map import map_utilization

scenario = Scenario("3287")
util_map = map_utilization(scenario, plot_states_kwargs={"background_map": False})
show(util_map)
