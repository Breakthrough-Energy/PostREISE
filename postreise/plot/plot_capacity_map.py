# This plotting module has a corresponding demo notebook in
#   PostREISE/postreise/plot/demo: capacity_map_demo.py

import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from matplotlib import colors as mcolors
from powersimdata import Scenario

from postreise.plot.plot_states import plot_states
from postreise.plot.projection_helpers import project_bus


def map_plant_capacity(
    scenario,
    resources,
    figsize=(1400, 800),
    x_range=None,
    y_range=None,
    disaggregation=None,
    plot_states_kwargs=None,
    min_capacity=1,
    size_factor=1,
    alpha=0.5,
    legend_font_size=12,
    legend_location="bottom_right",
):
    """Makes map of plant capacities, optionally disaggregated by new/existing. Area
    is proportional to capacity.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param iterable resources: which types of resources to plot.
    :param tuple figsize: size of the bokeh figure (in pixels).
    :param tuple(float, float) x_range: x range to zoom plot to (EPSG:3857).
    :param tuple(float, float) y_range: y range to zoom plot to (EPSG:3857).
    :param str disaggregation: method used to disaggregate plants:
        if "new_vs_existing_plants": separates plants into added vs. existing.
        if None, no disaggregation.
    :param dict plot_states_kwargs: keyword arguments to pass to
        :func:`postreise.plot.plot_states.plot_states`.
    :param float/int min_capacity: minimum bus capacity (MW) for markers to be plotted.
    :param float/int size_factor: scale size of glyphs.
    :param float/int alpha: opacity of circles (between 0 and 1).
    :param int/float legend_font_size: font size for legend.
    :param str legend_location: location for legend.
    :raises TypeError: if scenario is not a Scenario object.
    :return: (*bokeh.plotting.figure.Figure*) -- Bokeh map plot of color-coded upgrades.
    """

    if not isinstance(scenario, Scenario):
        raise TypeError(f"scenario must be a {Scenario} object")

    p = figure(
        tools="pan,wheel_zoom,reset,save",
        x_axis_location=None,
        y_axis_location=None,
        plot_width=figsize[0],
        plot_height=figsize[1],
        output_backend="webgl",
        sizing_mode="scale_both",
        match_aspect=True,
        x_range=x_range,
        y_range=y_range,
    )

    # state borders
    default_plot_states_kwargs = {
        "line_color": "gray",
        "line_width": 2,
        "fill_alpha": 0,
        "background_map": True,
    }
    if plot_states_kwargs is not None:
        all_plot_states_kwargs = {**default_plot_states_kwargs, **plot_states_kwargs}
    else:
        all_plot_states_kwargs = default_plot_states_kwargs
    plot_states(bokeh_figure=p, **all_plot_states_kwargs)

    add_plant_capacity(
        p,
        scenario,
        resources,
        disaggregation,
        min_capacity,
        size_factor,
        alpha,
    )

    p.legend.label_text_font_size = f"{legend_font_size}pt"
    p.legend.location = legend_location

    return p


def add_plant_capacity(
    bokeh_figure,
    scenario,
    resources,
    disaggregation=None,
    min_capacity=1,
    size_factor=1,
    alpha=0.5,
):
    """Adds renewables capacity to a plot.

    :param bokeh.plotting.figure.Figure bokeh_figure: figure to plot capacities onto.
    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param iterable resources: which types of resources to plot.
    :param tuple figsize: size of the bokeh figure (in pixels).
    :param tuple(float, float) x_range: x range to zoom plot to (EPSG:3857).
    :param tuple(float, float) y_range: y range to zoom plot to (EPSG:3857).
    :param str disaggregation: method used to disaggregate plants:
        if "new_vs_existing_plants": separates plants into added vs. existing.
        if None, no disaggregation.
    :param dict plot_states_kwargs: keyword arguments to pass to
        :func:`postreise.plot.plot_states.plot_states`.
    :param float/int min_capacity: minimum bus capacity (MW) for markers to be plotted.
    :param float/int size_factor: scale size of glyphs.
    :param float/int alpha: opacity of circles (between 0 and 1).
    :raises ValueError: if ``disaggregation`` is not 'new_vs_existing_plants' or None.
    :return: (*bokeh.plotting.figure.Figure*) -- Bokeh map plot of color-coded upgrades.
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
            circle = bokeh_figure.circle(
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
            ("Capacity (MW)", "@capacitymw"),
        ],
        renderers=renderers,
    )

    bokeh_figure.add_tools(hover)

    return bokeh_figure
