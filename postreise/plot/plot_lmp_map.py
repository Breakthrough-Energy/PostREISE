# This plotting module has a corresponding demo notebook in
#   PostREISE/postreise/plot/demo: lmp_map_demo.ipynb

import pandas as pd
from bokeh.layouts import row
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Turbo256
from bokeh.plotting import figure
from bokeh.tile_providers import Vendors, get_provider

from postreise.plot.plot_states import get_state_borders
from postreise.plot.projection_helpers import project_borders, project_bus


def map_lmp(grid, lmp, us_states_dat=None, lmp_min=20, lmp_max=45, is_website=False):
    """Plot average LMP by color coding buses.

    :param powersimdata.input.grid.Grid grid: grid object
    :param pandas.DataFrame lmp: locational marginal prices calculated for the scenario
    :param dict us_states_dat: dictionary of state border lats/lons. If None, get
        from :func:`postreise.plot.plot_states.get_state_borders`.
    :param inf/float lmp_min: minimum LMP to clamp plot range to.
    :param inf/float lmp_max: maximum LMP to clamp plot range to.
    :param bool is_website: changes text/legend formatting to look better on the website
    :return: (*bokeh.models.layout.Row*) bokeh map visual in row layout
    """
    if us_states_dat is None:
        us_states_dat = get_state_borders()

    bus = project_bus(grid.bus)
    bus_segments = _construct_bus_data(bus, lmp, lmp_min, lmp_max)
    return _construct_shadowprice_visuals(
        bus_segments, us_states_dat, lmp_min, lmp_max, is_website
    )


def _construct_bus_data(bus_map, lmp, lmp_min, lmp_max):
    """Add lmp data to each bus, splits buses into lmp segments for coloring

    :param pandas.DataFrame bus_map: bus dataframe with location data
    :param pandas.DataFrame lmp: lmp dataframe
    :param inf/float lmp_min: minimum LMP to clamp plot range to.
    :param inf/float lmp_max: maximum LMP to clamp plot range to.
    :return: (list(pandas.DataFrame)) -- bus data split into segments
    """
    # Add mean lmp to bus dataframe
    lmp_mean = pd.DataFrame(lmp.mean())
    lmp_mean = lmp_mean.rename(columns={lmp_mean.columns[0]: "lmp"})
    lmp_mean["lmp_norm"] = (lmp_mean.lmp - lmp_min) / (lmp_max - lmp_min) * 256
    bus_map = pd.concat([bus_map, lmp_mean], axis=1)
    bus_map_agg = group_lat_lon(bus_map)

    # set a min and a max so all values are assigned a color
    bus_map_agg.loc[(bus_map_agg.lmp_norm <= 0), "lmp_norm"] = 0.01
    bus_map_agg.loc[(bus_map_agg.lmp_norm > 255), "lmp_norm"] = 255
    bus_map_agg = pd.DataFrame(bus_map_agg)

    return bus_map_agg


def group_lat_lon(bus_map):
    """Group data and sums values, based on coordinates. Takes mean of means of buses
    at same coordinates. Round locations for grouping to nearest latlon decimal (1/10)
    degrees.

    :param pandas.DataFrame bus_map: data frame bus location and lmp means.
    :return: (*pandas.DataFrame*) -- data frame aggregated by rounded lat/lon
        coordinates.
    """
    bus_map1 = bus_map.copy()

    bus_map1.lat = bus_map1.lat.round(1)
    bus_map1.lon = bus_map1.lon.round(1)

    bus_map2 = bus_map1.groupby(["lat", "lon"]).agg(
        {"lmp_norm": "mean", "lmp": "mean", "x": "mean", "y": "mean"}
    )

    return bus_map2


def _construct_shadowprice_visuals(
    bus_segments, us_states_dat, lmp_min, lmp_max, is_website=False
):
    """Use bokeh to plot formatted data. Make map showing lmp using color.

    :param list bus_segments: bus data split by lmp as data frame.
    :param dict us_states_dat: dictionary of state border lats/lons.
    :param str file_name: name for output png file.
    :param inf/float lmp_min: minimum LMP to clamp plot range to.
    :param inf/float lmp_max: maximum LMP to clamp plot range to.
    :param bool is_website: changes text/legend formatting to look better on website.
    :return: (*bokeh.models.layout.Row*) -- bokeh map visual in row layout.
    """

    tools = "pan,wheel_zoom,reset,save"
    p = figure(
        tools=tools,
        x_axis_location=None,
        y_axis_location=None,
        plot_width=800,
        plot_height=800,
        output_backend="webgl",
        sizing_mode="stretch_both",
        match_aspect=True,
    )

    # Add USA map
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))
    # state borders
    a, b = project_borders(us_states_dat)
    p.patches(a, b, fill_alpha=0.0, line_color="gray", line_width=1)
    # Add colored circles for bus locations

    bus_segments.lmp_norm = bus_segments.lmp_norm.astype(int)
    bus_segments["col"] = bus_segments["lmp_norm"].apply(lambda x: Turbo256[x])

    bus_cds = ColumnDataSource(
        {
            "x": bus_segments["x"],
            "y": bus_segments["y"],
            "col": bus_segments["col"],
            "lmp": bus_segments["lmp"].round(2),
        }
    )
    circle = p.circle("x", "y", color="col", radius=10000, alpha=0.2, source=bus_cds)

    hover = HoverTool(
        tooltips=[
            ("$/MWh", "@lmp{1.11}"),
        ],
        renderers=[circle],
    )
    p.add_tools(hover)
    # Add legend
    bus_legend = _construct_bus_legend(lmp_min, lmp_max, is_website)
    return row(bus_legend, p, sizing_mode="stretch_both")


def _construct_bus_legend(lmp_min, lmp_max, is_website=False):
    """Constructs the legend for lmp at each bus.

    :param int/float lmp_min: minimum LMP to clamp plot range to.
    :param int/float lmp_max: maximum LMP to clamp plot range to.
    :param bool is_website: changes text/legend formatting to look better on website.
    :return: (*bokeh.plotting.figure*) -- legend showing lmp for each bus
    """
    x_range = [""]
    bars, bar_len_sum, labels = _get_bus_legend_bars_and_labels(
        x_range, lmp_min, lmp_max
    )

    # Make legend
    p = figure(
        x_range=x_range,
        plot_height=800,
        plot_width=50 if is_website else 110,
        toolbar_location=None,
        tools="",
        output_backend="webgl",
        sizing_mode="stretch_height",
        match_aspect=True,
    )
    p.vbar_stack(
        list(bars.keys())[1:],
        x="x_range",
        width=0.9,
        color=Turbo256[: (len(bars) - 1)],
        source=bars,
    )

    p.y_range.start = -1
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    ticker_vals = list(labels.keys())
    # Label colorbar in increments of 5 for website
    p.yaxis.ticker = ticker_vals[0::5] if is_website else ticker_vals
    p.yaxis.major_label_overrides = labels

    if is_website:
        # Prevents $/MWh text from being cut off
        p.rect(
            x=0,
            y=bar_len_sum + 7,
            width=1,
            height=7,
            alpha=0,
        )
    p.text(
        x=[0.05],
        y=[bar_len_sum * 1.01],
        text=["$/\nMWh" if is_website else " $/MWh"],
        text_font_size="7pt" if is_website else "12pt",
        level="overlay",
    )

    return p


def _get_bus_legend_bars_and_labels(x_range, lmp_min, lmp_max):
    """Get the bar lengths and labels for the bus legend.

    :param list x_range: the x-range for the vbar_stack.
    :param int/float lmp_min: minimum LMP to clamp plot range to.
    :param int/float lmp_max: maximum LMP to clamp plot range to.
    :return: (*tuple*) -- bar lengths and labels for the bus legend.
    """
    bars = {"x_range": x_range}
    lmp_split_points = list(range(0, 256, 1))
    bar_length_sum = 0
    labels = {}  # { y-position: label_text, ... }
    for i in range(len(lmp_split_points) - 2):
        bar_length = 0
        if i == 0 or i == len(lmp_split_points) - 1:
            # For first and last bars, clamp bar length
            # to prevent extreme min, max vals from overwhelming the legend
            lmp_diff = lmp_split_points[i + 1] - lmp_split_points[i]
            bar_length = 1 if lmp_diff < 1 else 5 if lmp_diff > 5 else lmp_diff
        elif i != len(lmp_split_points) - 1:
            # max_lmp has a label but no bar
            lmp_diff = lmp_split_points[i + 1] - lmp_split_points[i]
            # Min bar length of 1 to ensure small bars are visible
            bar_length = max(1, round(lmp_diff, 1))

        label_num = int(
            round(((lmp_split_points[i] - 1) * (lmp_max - lmp_min) / 256 + lmp_min), 0)
        )
        labels[round(bar_length_sum, -1)] = str(label_num)
        if i != len(lmp_split_points) - 1:
            bars[str(i)] = [bar_length]
            bar_length_sum += bar_length

    return bars, bar_length_sum, labels
