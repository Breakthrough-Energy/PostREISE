from bokeh.io import show
from powersimdata import Scenario

from postreise.plot.plot_capacity_map import map_plant_capacity

resources = {"solar", "wind", "nuclear"}
plot_kwargs = {
    "x_range": (-1.4e7, -1.12e7),
    "y_range": (3.6e6, 6.4e6),
    "figsize": (800, 800),
}

scenario = Scenario(3697)
show(map_plant_capacity(scenario, resources, **plot_kwargs))
show(
    map_plant_capacity(
        scenario, resources, disaggregation="new_vs_existing_plants", **plot_kwargs
    )
)
