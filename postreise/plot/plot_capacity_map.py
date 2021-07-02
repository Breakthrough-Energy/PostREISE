# This plotting module has a corresponding demo notebook in
#   PostREISE/postreise/plot/demo: capacity_map_demo.py
import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool
from matplotlib import colors as mcolors
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state

from postreise.plot.canvas import create_map_canvas
from postreise.plot.check import _check_func_kwargs
from postreise.plot.plot_states import add_state_borders
from postreise.plot.projection_helpers import project_bus


def map_plant_capacity(
    scenario,
    resources,
    figsize=(1400, 800),
    x_range=None,
    y_range=None,
    disaggregation=None,
    state_borders_kwargs=None,
    min_capacity=1,
    size_factor=1,
    alpha=0.5,
    legend_font_size=12,
    legend_location="bottom_right",
):
    """Make map of plant capacities, optionally disaggregated by new/existing. Area
    is proportional to capacity.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param iterable resources: which types of resources to plot.
    :param tuple figsize: size of the bokeh figure (in pixels).
    :param tuple x_range: x range to zoom plot to (EPSG:3857).
    :param tuple y_range: y range to zoom plot to (EPSG:3857).
    :param str disaggregation: method used to disaggregate plants:
        if "new_vs_existing_plants": separates plants into added vs. existing.
        if None, no disaggregation.
    :param dict state_borders_kwargs: keyword arguments to pass to
        :func:`postreise.plot.plot_states.add_state_borders`.
    :param float/int min_capacity: minimum bus capacity (MW) for markers to be plotted.
    :param float/int size_factor: scale size of glyphs.
    :param float/int alpha: opacity of circles (between 0 and 1).
    :param int/float legend_font_size: font size for legend.
    :param str legend_location: location for legend.
    :return: (*bokeh.plotting.figure.Figure*) -- map with color-coded upgrades.
    """
    _check_scenario_is_in_analyze_state(scenario)

    # create canvas
    canvas = create_map_canvas(figsize=figsize, x_range=x_range, y_range=y_range)

    # add state borders
    default_state_borders_kwargs = {
        "line_color": "gray",
        "line_width": 2,
        "fill_alpha": 0,
        "background_map": True,
    }
    all_state_borders_kwargs = (
        {**default_state_borders_kwargs, **state_borders_kwargs}
        if state_borders_kwargs is not None
        else default_state_borders_kwargs
    )
    _check_func_kwargs(
        add_state_borders, set(all_state_borders_kwargs), "state_borders_kwargs"
    )
    canvas = add_state_borders(canvas, **all_state_borders_kwargs)

    # add plant capacity
    add_plant_capacity(
        canvas,
        scenario,
        resources,
        disaggregation,
        min_capacity,
        size_factor,
        alpha,
    )

    canvas.legend.label_text_font_size = f"{legend_font_size}pt"
    canvas.legend.location = legend_location

    return canvas


def add_plant_capacity(
    canvas,
    scenario,
    resources,
    disaggregation=None,
    min_capacity=1,
    size_factor=1,
    alpha=0.5,
):
    """Adds renewables capacity to a plot.

    :param bokeh.plotting.figure.Figure canvas: canvas to plot capacities onto.
    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param iterable resources: which types of resources to plot.
    :param tuple figsize: size of the bokeh figure (in pixels).
    :param tuple x_range: x range to zoom plot to (EPSG:3857).
    :param tuple y_range: y range to zoom plot to (EPSG:3857).
    :param str disaggregation: method used to disaggregate plants:
        if "new_vs_existing_plants": separates plants into added vs. existing.
        if None, no disaggregation.
    :param float/int min_capacity: minimum bus capacity (MW) for markers to be plotted.
    :param float/int size_factor: scale size of glyphs.
    :param float/int alpha: opacity of circles (between 0 and 1).
    :raises ValueError: if ``disaggregation`` is not 'new_vs_existing_plants' or None.
    :return: (*bokeh.plotting.figure.Figure*) -- map with color-coded upgrades.
    """
    ct = scenario.get_ct()
    grid = scenario.get_grid()
    grid.plant["lat"] = grid.plant["lat"].round(3)
    grid.plant["lon"] = grid.plant["lon"].round(3)
    grid.plant = project_bus(grid.plant.query("type in @resources"))
    type_colors = grid.model_immutables.plants["type2color"]

    xy_capacity = {}
    if disaggregation is None:
        grouped_capacities = grid.plant.groupby(["x", "y", "type"]).sum().Pmax
        grouped_capacities = grouped_capacities.reset_index()
        xy_capacity["all"] = grouped_capacities.query("Pmax > 0")
    elif disaggregation == "new_vs_existing_plants":
        if "new_plant" in ct.keys():
            num_new_plants = len(ct["new_plant"])
            scaled_plants = grid.plant.iloc[:-num_new_plants]
            new_plants = grid.plant.iloc[-num_new_plants:]
            grouped_new_capacities = new_plants.groupby(["x", "y", "type"]).sum().Pmax
            grouped_new_capacities = grouped_new_capacities.reset_index()
            xy_capacity["new"] = grouped_new_capacities.query("Pmax > 0")
        else:
            scaled_plants = grid.plant
            new_plants = pd.DataFrame(columns=grid.plant.columns)
            xy_capacity["new"] = pd.DataFrame(columns=["x", "y", "type", "Pmax"])
        grouped_capacities = scaled_plants.groupby(["x", "y", "type"]).sum().Pmax
        grouped_capacities = grouped_capacities.reset_index()
        xy_capacity["existing"] = grouped_capacities.query("Pmax > 0")
    else:
        raise ValueError(f"Unknown disaggregation method: {disaggregation}")

    # capacity circles
    renderers = []
    for tranche, plants in xy_capacity.items():
        for resource in sorted(resources):
            if disaggregation is None:
                legend_label = f"{resource} capacity"
            elif disaggregation == "new_vs_existing_plants":
                legend_label = f"{resource} capacity of {tranche} plants"
            if resource not in plants.type.unique():
                print(f"no {resource} plants for grouping: {tranche}")
                continue
            matching_plants = plants.query("type == @resource")
            data = {
                "x": matching_plants["x"],
                "y": matching_plants["y"],
                "capacity": matching_plants["Pmax"],
                "radius": matching_plants["Pmax"] ** 0.5 * size_factor,
            }
            circle = canvas.circle(
                "x",
                "y",
                color=mcolors.to_hex(type_colors[resource]),
                alpha=0.8,
                size="radius",
                source=ColumnDataSource(data),
                legend_label=legend_label,
            )
            renderers.append(circle)

    hover = HoverTool(
        tooltips=[
            ("Capacity (MW)", "@capacity"),
        ],
        renderers=renderers,
    )

    canvas.add_tools(hover)

    return canvas
