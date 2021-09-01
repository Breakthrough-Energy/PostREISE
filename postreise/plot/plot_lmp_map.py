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
from matplotlib.colors import BoundaryNorm
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state

from postreise.plot.canvas import create_map_canvas
from postreise.plot.check import _check_func_kwargs
from postreise.plot.plot_states import add_state_borders
from postreise.plot.projection_helpers import project_bus


def map_lmp(
    scenario,
    coordinate_rounding=1,
    lmp_min=20,
    lmp_max=45,
    num_ticks=6,
    figsize=(1400, 800),
    scale_factor=1,
    state_borders_kwargs=None,
):
    """Plot average LMP at bus level.

    :param powersimdata.scenario,scenario.Scenario scenario: scenario instance..
    :param int coordinate_rounding: number of digits to round lat/lon for aggregation.
    :param int lmp_min: minimum LMP to clamp plot range to.
    :param int lmp_max: maximum LMP to clamp plot range to.
    :param int num_ticks: number of ticks to display on the color bar.
    :param tuple figsize: size of the bokeh figure (in pixels).
    :param int/float scale_factor: scaling factor for size of circles centered on buses.
    :param dict state_borders_kwargs: keyword arguments to be passed to
        :func:`postreise.plot.plot_states.add_state_borders`.
    :return: (*bokeh.plotting.figure*) -- LMP map.
    :raises TypeError:
        if ``coordinate_rounding`` is not ``int``.
        if ``lmp_min`` and ``lmp_max`` are not ``int``.
        if ``num_ticks`` is not ``int``.
        if ``scale_factor`` is not ``int`` or ``float``.
    :raises ValueError:
        if ``coordinate_rounding`` is not positive.
        if ``num_ticks`` is negative.
        if ``lmp_min`` or ``lmp_max`` is negative or ``lmp_min`` >= ``lmp_max``.
        if ``scale_factor`` is negative.
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
    if not isinstance(scale_factor, (int, float)):
        raise TypeError("scale_factor must be a int/float")
    if scale_factor < 0:
        raise ValueError("scale_factor must be positive")

    grid = scenario.state.get_grid()
    lmp = scenario.state.get_lmp()
    bus_with_lmp = grid.bus.copy()
    bus_with_lmp["lmp"] = lmp.mean()

    return add_lmp(
        bus_with_lmp,
        coordinate_rounding,
        lmp_min,
        lmp_max,
        num_ticks,
        figsize,
        scale_factor,
        state_borders_kwargs,
    )


def add_lmp(
    bus_with_lmp,
    coordinate_rounding,
    lmp_min,
    lmp_max,
    num_ticks,
    figsize,
    scale_factor,
    state_borders_kwargs,
):
    """Add LMP to canvas.

    :param list bus_with_lmp: bus data frame with LMP values.
    :param int coordinate_rounding: number of digits to round lat/lon for aggregation.
    :param str file_name: name for output png file.
    :param int lmp_min: minimum LMP to clamp plot range to.
    :param int lmp_max: maximum LMP to clamp plot range to.
    :param int num_ticks: number of ticks to display on the color bar.
    :param tuple figsize: size of the bokeh figure (in pixels).
    :param int/float scale_factor: scaling factor for size of circles centered on buses.
    :param dict state_borders_kwargs: keyword arguments to be passed to
        :func:`postreise.plot.plot_states.add_state_borders`.
    :return: (*bokeh.plotting.figure*) -- canvas with LMP..
    """

    # create canvas
    canvas = create_map_canvas(figsize=figsize)

    # add state borders
    default_state_borders_kwargs = {
        "line_color": "gray",
        "line_width": 2,
        "fill_alpha": 0,
        "background_map": False,
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

    circle = canvas.circle(
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
    canvas.add_tools(hover)

    # Add color bar
    cm = LinearColorMapper(palette="Turbo256", low=norm.vmin, high=norm.vmax)
    cb = ColorBar(
        color_mapper=cm,
        ticker=BasicTicker(desired_num_ticks=num_ticks),
        title="$/MWh",
        title_standoff=8,
        orientation="vertical",
        location=(0, 0),
    )
    canvas.add_layout(cb, "left")

    return canvas


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
