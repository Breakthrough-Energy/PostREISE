# This plotting module has a corresponding demo notebook in
#   PostREISE/postreise/plot/demo: lmp_map_demo.ipynb

from bokeh.models import (
    BasicTicker,
    ColorBar,
    ColumnDataSource,
    HoverTool,
    LinearColorMapper,
)
from bokeh.palettes import Turbo256
from bokeh.plotting import figure
from matplotlib.colors import BoundaryNorm

from postreise.analyze.check import _check_scenario_is_in_analyze_state
from postreise.plot.plot_states import plot_states
from postreise.plot.projection_helpers import project_bus


def map_lmp(
    scenario,
    coordinate_rounding=1,
    lmp_min=20,
    lmp_max=45,
    num_ticks=6,
    figsize=(1400, 800),
    scale_factor=1,
    background_map=False,
):
    """Plot average LMP at bus level.

    :param powersimdata.scenario,scenario.Scenario scenario: scenario instance..
    :param int coordinate_rounding: number of digits to round lat/lon for aggregation.
    :param int lmp_min: minimum LMP to clamp plot range to.
    :param int lmp_max: maximum LMP to clamp plot range to.
    :param int num_ticks: number of ticks to display on the color bar.
    :param tuple figsize: size of the bokeh figure (in pixels).
    :param int/float scale_factor: scaling factor for size of circles centered on buses.
    :param bool background_map: whether to plot map tiles behind figure.
    :return: (*bokeh.plotting.figure*) -- LMP map.
    :raises TypeError:
        if ``coordinate_rounding`` is not ``int``.
        if ``lmp_min`` and ``lmp_max`` are not ``int``.
        if ``num_ticks`` is not ``int``.
        if ``figsize`` is not a tuple.
        if ``scale_factor`` is not ``int`` or ``float``.
        if ``background_map`` is not a ``bool``.
    :raises ValueError:
        if ``coordinate_rounding`` is not positive.
        if ``num_ticks`` is negative.
        if ``lmp_min`` or ``lmp_min`` is negative or ``lmp_min`` >= ``lmp_max``.
        if ``scale_factor`` is negative.
        if both elements of ``figsize`` are not positive.
    """
    _check_scenario_is_in_analyze_state(scenario)
    if not isinstance(coordinate_rounding, int):
        raise TypeError("coordinate_rounding must be an int")
    if coordinate_rounding < 0:
        raise ValueError("coordinate_rounding must be positive")
    if not isinstance(lmp_min, int):
        raise TypeError("lmp_min must be a int")
    if not isinstance(lmp_max, int):
        raise TypeError("lmp_max must be a int")
    if lmp_min >= lmp_max:
        raise ValueError("Must have lmp_min < lmp_max")
    if not isinstance(figsize, tuple):
        raise TypeError("figsize must be a tuple")
    if not (len(figsize) == 2 and all(e > 0 for e in figsize)):
        raise ValueError("both elemets of figsize must be positive")
    if not isinstance(scale_factor, (int, float)):
        raise TypeError("scale_factor must be a int/float")
    if scale_factor < 0:
        raise ValueError("scale_factor must be positive")
    if not isinstance(background_map, bool):
        raise TypeError("background_map must be a bool")

    grid = scenario.state.get_grid()
    lmp = scenario.state.get_lmp()
    bus_with_lmp = grid.bus.copy()
    bus_with_lmp["lmp"] = lmp.mean()

    return construct_lmp_visuals(
        bus_with_lmp,
        coordinate_rounding,
        lmp_min,
        lmp_max,
        num_ticks,
        figsize,
        scale_factor,
        background_map,
    )


def aggregate_bus_lmp(bus, coordinate_rounding):
    """Aggregate LMP for buses based on similar lat/lon coordinates.

    :param pandas.DataFrame bus: data frame containing 'lat', 'lon', 'lmp' columns.
    :param int coordinate_rounding: number of digits to round lat/lon for aggregation.
    :return: (*pandas.DataFrame*) -- aggregated data frame.
    """
    bus_w_xy = project_bus(bus)
    bus_w_xy["lat"] = bus_w_xy["lat"].round(coordinate_rounding)
    bus_w_xy["lon"] = bus_w_xy["lon"].round(coordinate_rounding)
    aggregated = bus_w_xy.groupby(["lat", "lon"]).agg(
        {"lmp": "mean", "x": "mean", "y": "mean"}
    )

    return aggregated


def construct_lmp_visuals(
    bus_with_lmp,
    coordinate_rounding,
    lmp_min,
    lmp_max,
    num_ticks,
    figsize,
    scale_factor,
    background_map,
):
    """Use bokeh to plot formatted data. Make map showing LMP using color.

    :param list bus_with_lmp: bus data frame with LMP values.
    :param int coordinate_rounding: number of digits to round lat/lon for aggregation.
    :param str file_name: name for output png file.
    :param int lmp_min: minimum LMP to clamp plot range to.
    :param int lmp_max: maximum LMP to clamp plot range to.
    :param int num_ticks: number of ticks to display on the color bar.
    :param tuple figsize: size of the bokeh figure (in pixels).
    :param int/float scale_factor: scaling factor for size of circles centered on buses.
    :param bool background_map: whether to plot map tiles behind figure.
    :return: (*bokeh.plotting.figure*) -- bokeh LMP map.
    """

    p = figure(
        tools="pan,wheel_zoom,reset,save",
        x_axis_location=None,
        y_axis_location=None,
        plot_width=figsize[0],
        plot_height=figsize[1],
        output_backend="webgl",
        sizing_mode="scale_both",
        match_aspect=True,
    )
    p.xgrid.visible = False
    p.ygrid.visible = False

    plot_states(bokeh_figure=p, background_map=background_map)

    # aggregate buses by lat/lon
    grouped_bus = aggregate_bus_lmp(bus_with_lmp, coordinate_rounding)

    # assign color
    norm = BoundaryNorm(boundaries=range(lmp_min, lmp_max + 1), ncolors=256, clip=True)
    grouped_bus["col"] = norm(grouped_bus["lmp"])
    grouped_bus["col"] = grouped_bus["col"].apply(lambda x: Turbo256[x])

    grouped_bus_info = {
        "x": grouped_bus["x"],
        "y": grouped_bus["y"],
        "col": grouped_bus["col"],
        "lmp": grouped_bus["lmp"].round(2),
    }

    circle = p.circle(
        "x",
        "y",
        color="col",
        size=2 * scale_factor,
        alpha=0.2,
        source=ColumnDataSource(grouped_bus_info),
    )
    hover = HoverTool(
        tooltips=[
            ("$/MWh", "@lmp{1.11}"),
        ],
        renderers=[circle],
    )
    p.add_tools(hover)

    cm = LinearColorMapper(palette="Turbo256", low=norm.vmin, high=norm.vmax)
    cb = ColorBar(
        color_mapper=cm,
        ticker=BasicTicker(desired_num_ticks=num_ticks),
        title="$/MWh",
        title_standoff=8,
        orientation="vertical",
        location=(0, 0),
    )
    p.add_layout(cb, "left")

    return p
