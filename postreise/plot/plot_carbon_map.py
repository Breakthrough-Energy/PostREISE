import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state
from powersimdata.network.constants.carrier.resource import USAResource, EUResource

from postreise.analyze.generation.emissions import (
    generate_emissions_stats,
    summarize_emissions_by_bus,
)
from postreise.plot.canvas import create_map_canvas
from postreise.plot.colors import be_green, be_red, be_purple
from postreise.plot.plot_borders import add_borders
from postreise.plot.projection_helpers import project_bus


def combine_bus_info_and_emission(scenario):
    """Build data frame needed for plotting carbon emitted by thermal generators.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- bus data frame with emission.
    """
    grid = scenario.get_grid()
    carbon_by_bus = summarize_emissions_by_bus(generate_emissions_stats(scenario), grid)

    selected = grid.bus.loc[pd.DataFrame.from_dict(carbon_by_bus).index]
    bus_w_emission = selected.merge(
        pd.DataFrame.from_dict(carbon_by_bus), right_index=True, left_index=True
    )

    return bus_w_emission


def aggregate_bus_emission_generator(bus, coordinate_rounding, resource_types):
    """Aggregate emission for buses based on similar lat/lon coordinates

    :param pandas.DataFrame bus: bus data frame containing carbon resource types,
        'lat', 'lon', 'type', and 'color' columns.
    :param int coordinate_rounding: number of digits to round lat/lon for aggregation.
    :param set resource_types: set of carbon resource types.
    :return: (*pandas.DataFrame*) -- aggregated data frame.
    """
    bus_w_xy = project_bus(bus)
    bus_w_xy["lat"] = bus_w_xy["lat"].round(coordinate_rounding)
    bus_w_xy["lon"] = bus_w_xy["lon"].round(coordinate_rounding)

    resource_agg = {rtype: "sum" for rtype in resource_types}
    aggregated = bus_w_xy.groupby(["lat", "lon", "color", "type"]).agg(
        {"x": "mean", "y": "mean", **resource_agg}
    )
    aggregated = aggregated.reset_index()
    return aggregated


def aggregate_bus_emission_difference(bus, coordinate_rounding, grid):
    """Aggregate emission for buses based on similar lat/lon coordinates

    :param pandas.DataFrame bus: bus data frame containing carbon resource types,
        'lat', 'lon', 'type', and 'color' columns.
    :param int coordinate_rounding: number of digits to round lat/lon for aggregation.
    :return: (*pandas.DataFrame*) -- aggregated data frame.
    """
    bus_w_xy = project_bus(bus)
    bus_w_xy["lat"] = bus_w_xy["lat"].round(coordinate_rounding)
    bus_w_xy["lon"] = bus_w_xy["lon"].round(coordinate_rounding)

    aggregated = bus_w_xy.groupby(["lat", "lon"]).agg(
        {"amount": "sum", "x": "mean", "y": "mean"}
    )
    aggregated = aggregated.reset_index()
    return aggregated


def prepare_bus_data_generator(grid, bus_emission, coordinate_rounding):
    """Prepare data with amount of emissions.

    :param powersimdata.input.grid.Grid grid: grid object.
    :param pandas.DataFrame bus_emission: bus data frame with emission as returned by
        :func:`combine_bus_info_and_emission`.
    :param int coordinate_rounding: number of digits to round lat/lon for aggregation.
    :return: (*pandas.DataFrame*) -- data for plotting.
    """
    bus_emission["color"] = ""
    bus_emission["type"] = ""

    coal_resource_types = grid.model_immutables.plants["group_all_resources"]["coal"]
    ng_resource_types = grid.model_immutables.plants["group_all_resources"]["ng"]
    resource_types = coal_resource_types.union(ng_resource_types)

    for rtype in resource_types:
        # TODO: update usa_tamu ModelImmutables colors to use hex values so this doesn't break
        if grid.grid_model == "usa_tamu":
            colors = {"coal": "black", "ng": be_purple}
            color = colors[rtype]
        elif grid.grid_model == "europe_tub":
            color = grid.model_immutables.plants["type2color"][rtype]
        else:
            raise ValueError("grid model is not supported")

        bus_emission.loc[(bus_emission[rtype] > 0), "color"] = color
        label = grid.model_immutables.plants["type2label"][rtype]
        bus_emission.loc[(bus_emission[rtype] > 0), "type"] = label

    grouped_bus_emission = aggregate_bus_emission_generator(
        bus_emission, coordinate_rounding, resource_types
    )
    grouped_bus_emission["amount"] = 0
    for rtype in resource_types:
        grouped_bus_emission["amount"] = (
            grouped_bus_emission["amount"] + grouped_bus_emission[rtype]
        )

    return grouped_bus_emission.query("amount != 0").sort_values(by=["color"])


def prepare_bus_data_difference(
    bus_emission, coordinate_rounding, color_up, color_down, grid=None
):
    """Prepare data with amount of emissions and type for hover tips

    :param pandas.DataFrame bus_emission: bus data frame with emission as returned by
        :func:`combine_bus_info_and_emission`.
    :param int coordinate_rounding: number of digits to round lat/lon for aggregation.
    :param str color_up: color assigned to 'increase' in emissions.
    :param str color_down: color assigned to 'decrase' in emissions.
    # ADD GRID
    :return: (*pandas.DataFrame*) -- data for plotting.
    """
    grouped_bus_emission = aggregate_bus_emission_difference(
        bus_emission, coordinate_rounding, grid=None
    )
    grouped_bus_emission["color"] = ""
    grouped_bus_emission["type"] = ""
    grouped_bus_emission.loc[(grouped_bus_emission["amount"] > 0), "color"] = color_up
    grouped_bus_emission.loc[(grouped_bus_emission["amount"] < 0), "color"] = color_down
    grouped_bus_emission.loc[(grouped_bus_emission["amount"] > 0), "type"] = "increase"
    grouped_bus_emission.loc[(grouped_bus_emission["amount"] < 0), "type"] = "decrease"

    grouped_bus_emission["amount"] = grouped_bus_emission["amount"].abs()
    return grouped_bus_emission.query("amount != 0").sort_values(by=["color"])


def add_emission(canvas, emission, scale_factor):
    """Add emission.

    :param pandas.DataFrame emission: emission data for plotting.
    :param float scale_factor: scaling factor for size of emissions circles glyphs.
    :return: (*bokeh.plotting.figure*) -- carbon emission map.
    """

    # emissions as circles
    source = {
        "x": emission["x"],
        "y": emission["y"],
        "size": np.log2(emission["amount"]) * scale_factor,
        "tons": emission["amount"],
        "color": emission["color"],
        "type": emission["type"],
    }
    circle = canvas.circle(
        "x",
        "y",
        color="color",
        alpha=0.25,
        size="size",
        source=ColumnDataSource(source),
        legend_group="type",
    )
    hover = HoverTool(
        tooltips=[
            ("Type", "@type"),
            ("Tons CO\u2082", "@tons"),
        ],
        renderers=[circle],
    )
    canvas.add_tools(hover)

    canvas.legend.location = "bottom_right"
    canvas.legend.label_text_font_size = "12pt"

    return canvas


def map_carbon_emission_generator(
    scenario,
    coordinate_rounding=1,
    figsize=(1400, 800),
    scale_factor=1,
    borders_kwargs=None,
):
    """Make map of carbon emissions at bus level. Color of markers indicates generator
    type and size reflects emissions level.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param int coordinate_rounding: number of digits to round lat/lon for aggregation.
    :param tuple figsize: size of the bokeh figure (in pixels).
    :param int/float scale_factor: scaling factor for size of emissions circles glyphs.
    :param dict borders_kwargs: keyword arguments to be passed to
        :func:`postreise.plot.plot_borders.add_borders`.
    :return: (*bokeh.plotting.figure*) -- carbon emission map.
    :raises TypeError:
        if ``coordinate_rounding`` is not ``int``.
        if ``scale_factor`` is not ``int`` or ``float``.
    :raises ValueError:
        if ``coordinate_rounding`` is negative.
        if ``scale_factor`` is negative.
    """
    _check_scenario_is_in_analyze_state(scenario)
    if not isinstance(coordinate_rounding, int):
        raise TypeError("coordinate_rounding must be an int")
    if coordinate_rounding < 0:
        raise ValueError("coordinate_rounding must be positive")
    if not isinstance(scale_factor, (int, float)):
        raise TypeError("scale_factor must be a int/float")
    if scale_factor < 0:
        raise ValueError("scale_factor must be positive")

    # create canvas
    canvas = create_map_canvas(figsize=figsize)

    # add state borders
    default_borders_kwargs = {"fill_alpha": 0.0, "background_map": False}
    all_borders_kwargs = (
        {**default_borders_kwargs, **borders_kwargs}
        if borders_kwargs is not None
        else default_borders_kwargs
    )
    grid = scenario.state.get_grid()
    canvas = add_borders(grid.grid_model, canvas, all_borders_kwargs)

    # add emission
    bus_emission = combine_bus_info_and_emission(scenario)
    emission = prepare_bus_data_generator(grid, bus_emission, coordinate_rounding)
    canvas = add_emission(canvas, emission, scale_factor)
    return canvas


def map_carbon_emission_difference(
    scenario_1,
    scenario_2,
    coordinate_rounding=1,
    figsize=(1400, 800),
    color_increase=be_red,
    color_decrease=be_green,
    scale_factor=1,
    borders_kwargs=None,
):
    """Make map of difference in emissions between two scenarios at bus level. Color of
    markers indicates increase/decrease in emissions (``scenario_2`` w.r,t.
    ``scenario_1``) and size reflects relative difference in emissions.

    :param powersimdata.scenario.scenario.Scenario scenario_1: scenario instance.
    :param powersimdata.scenario.scenario.Scenario scenario_2: scenario instance.
    :param int coordinate_rounding: number of digits to round lat/lon for aggregation.
    :param tuple figsize: size of the bokeh figure (in pixels).
    :param str color_increase: color assigned to increase in emissions.
    :param str color_decrease: color associated to decrease in emissions.
    :param float scale_factor: scaling factor for size of emissions circles glyphs.
    :param dict borders_kwargs: keyword arguments to be passed to
        :func:`postreise.plot.plot_borders.add_borders`.
    :return: (*bokeh.plotting.figure*) -- carbon emission map.
    :raises TypeError:
        if ``coordinate_rounding`` is not ``int``.
        if ``color_increase`` and ``color_decrease`` are not ``str``.
        if ``scale_factor`` is not ``int`` or ``float``.
    :raises ValueError:
        if ``coordinate_rounding`` is negative.
        if ``scale_factor`` is negative.
    """
    _check_scenario_is_in_analyze_state(scenario_1)
    _check_scenario_is_in_analyze_state(scenario_2)
    if not isinstance(coordinate_rounding, int):
        raise TypeError("coordinate_rounding must be an int")
    if coordinate_rounding < 0:
        raise ValueError("coordinate_rounding must be positive")
    if not isinstance(color_increase, str):
        raise TypeError("color_increase must be a str")
    if not isinstance(color_decrease, str):
        raise TypeError("color_decrease must be a str")
    if not isinstance(scale_factor, (int, float)):
        raise TypeError("scale_factor must be a int/float")
    if scale_factor < 0:
        raise ValueError("scale_factor must be positive")

    # create canvas
    canvas = create_map_canvas(figsize=figsize)

    # add state borders
    default_borders_kwargs = {"fill_alpha": 0.0, "background_map": False}
    all_borders_kwargs = (
        {**default_borders_kwargs, **borders_kwargs}
        if borders_kwargs is not None
        else default_borders_kwargs
    )
    grid = scenario_1.state.get_grid()
    canvas = add_borders(grid.grid_model, canvas, all_borders_kwargs)

    # add emission
    bus_emission_1 = combine_bus_info_and_emission(scenario_1)
    bus_emission_2 = combine_bus_info_and_emission(scenario_2)
    emission = bus_emission_1.merge(
        bus_emission_2,
        right_index=True,
        left_index=True,
        suffixes=("_1", "_2"),
        how="outer",
    )
    emission.fillna(0, inplace=True)

    coal_resource_types = grid.model_immutables.plants["group_all_resources"]["coal"]
    ng_resource_types = grid.model_immutables.plants["group_all_resources"]["ng"]
    resource_types = coal_resource_types.union(ng_resource_types)

    emission["amount"] = 0
    for rtype in resource_types:
        emission["amount"] + emission[f"{rtype}_2"] - emission[f"{rtype}_1"]

    emission["lon"] = emission["lon_1"].fillna(emission["lon_2"])
    emission["lat"] = emission["lat_1"].fillna(emission["lat_2"])
    emission = prepare_bus_data_difference(
        emission, coordinate_rounding, color_increase, color_decrease, grid
    )
    canvas = add_emission(canvas, emission, scale_factor)

    return canvas
