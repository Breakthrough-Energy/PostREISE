from bokeh.io import show
from powersimdata import Scenario

from postreise.plot.plot_carbon_map import map_carbon_emission_generator

scenario = Scenario(3287)

emission_map = map_carbon_emission_generator(
    scenario, coordinate_rounding=0, scale_factor=0.75
)
show(emission_map)
