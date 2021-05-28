from bokeh.io import show
from powersimdata import Scenario

from postreise.plot.plot_carbon_map import map_carbon_emission_difference

scenarioA = Scenario(2497)
scenarioB = Scenario(3101)

emission_difference_map = map_carbon_emission_difference(
    scenarioA, scenarioB, coordinate_rounding=0
)
show(emission_difference_map)
