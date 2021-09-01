import numpy as np
import pandas as pd
from bokeh.layouts import row
from bokeh.models import ColorBar, ColumnDataSource
from bokeh.plotting import figure
from bokeh.tile_providers import Vendors, get_provider
from bokeh.transform import linear_cmap
from powersimdata.input.check import _check_date
from powersimdata.scenario.scenario import Scenario

from postreise.plot.colors import shadow_price_pallette
from postreise.plot.projection_helpers import project_branch, project_bus


def plot_shadowprice(scenario_id, datetime, lmp_split_points=None):
    """Map lmp variation and shadow prices

    :param str/int scenario_id: scenario id
    :param pandas.Timestamp/numpy.datetime64/datetime.datetime datetime: timestamp of
        the hour to analyze
    :param list/tuple/set/numpy.array lmp_split_points: the locational marginal
        pricing (lmp) values we have chosen to split the bus data. Includes min and
        max values. Must have 10 items or fewer. defaults to None. Example: [-1, 1,
        20, 25, 30, 35, 40, 100]
    :return: (*bokeh.models.layout.Row*) -- bokeh map visual in row layout.
    :raises TypeError: if *'scenario_id'* is not a str/int, *'datetime'* is not a str
        or *'lmp_split_points'* is not a list
    :raises ValueError: if *'lmp_split_points'* array has more than 10 elements
    """
    if not isinstance(scenario_id, (str, int)):
        raise TypeError("scenario_id must be a str/int")
    _check_date(datetime)
    if lmp_split_points is not None:
        if not isinstance(lmp_split_points, list):
            raise TypeError("lmp_split_points must be a list")
        if len(lmp_split_points) > 10:
            raise ValueError("lmp_split_points must have 10 items or fewer")

    interconnect, bus, lmp, branch, cong = _get_shadowprice_data(scenario_id)
    lmp_split_points, bus_segments = _construct_bus_data(
        bus, lmp, lmp_split_points, datetime
    )
    branches_selected = _construct_branch_data(branch, cong, datetime)
    return _construct_shadowprice_visuals(
        interconnect, lmp_split_points, bus_segments, branches_selected
    )


def _get_shadowprice_data(scenario_id):
    """Gets data necessary for plotting shadow price

    :param str/int scenario_id: scenario id
    :return: (*tuple*) -- interconnect as a str, bus data as a data frame, lmp data
        as a data frame, branch data as a data frame and congestion data as a data
        frame
    """
    s = Scenario(scenario_id)

    interconnect = s.info["interconnect"]
    interconnect = " ".join(interconnect.split("_"))

    s_grid = s.state.get_grid()

    # Get bus and add location data
    bus_map = project_bus(s_grid.bus)

    # get branch and add location data
    branch_map = project_branch(s_grid.branch)

    # get congestion
    congu = s.state.get_congu()
    congl = s.state.get_congl()
    cong_abs = pd.DataFrame(
        np.maximum(congu.to_numpy(), congl.to_numpy()),
        columns=congu.columns,
        index=congu.index,
    )

    return interconnect, bus_map, s.state.get_lmp(), branch_map, cong_abs


def _construct_bus_data(bus_map, lmp, user_set_split_points, datetime):
    """Adds lmp data to each bus, splits buses into 9 segments by lmp

    :param pandas.DataFrame bus_map: bus data frame with location data
    :param pandas.DataFrame lmp: lmp data frame
    :param list/tuple/set/numpy.array user_set_split_points: user-set lmp values to
        split the bus data. Must have 10 items or fewer. Example: [-1, 1, 20, 25, 30,
        35, 40, 100]
    :param pandas.Timestamp/numpy.datetime64/datetime.datetime datetime: timestamp of
        the hour to analyze
    :return: (*tuple*) -- the lmp vals we have chosen to split the bus data, bus data
        split into segments
    """
    lmp_hour = lmp.loc[datetime]
    lmp_hour = lmp_hour.T
    lmp_hour.name = "lmp"
    bus_map = pd.concat([bus_map, lmp_hour], axis=1)

    lmp_split_points = (
        user_set_split_points
        if user_set_split_points is not None
        else _get_lmp_split_points(bus_map)
    )
    bus_segments = [
        bus_map[(bus_map["lmp"] > p) & (bus_map["lmp"] <= c)]
        for p, c in zip(lmp_split_points, lmp_split_points[1:])
    ]

    return lmp_split_points, bus_segments


def _get_lmp_split_points(bus_map):
    """Determine up to ten points to split the bus data (inc. min and max lmp).
    Always split on lmp -1 and 1 if possible. Split the rest of the buses into groups
    with an equal number of members

    :param pandas.DataFrame bus_map: bus data with lmp
    :return: (*list*) -- lmp values for split points
    """
    min_lmp = round(bus_map["lmp"].min(), 2)
    max_lmp = round(bus_map["lmp"].max(), 2)

    split_points = [min_lmp]

    # If we have busses with negative lmp we always split at -1 and 1
    if min_lmp < -1:
        split_points.append(-1)
    if min_lmp < 1:
        split_points.append(1)
        # remove busses with lmp below 1
        bus_map_pos = bus_map[(bus_map["lmp"] >= 1)]
    else:
        bus_map_pos = bus_map

    # split remaining busses into equally sized groups
    num_splits = 9 - len(split_points)
    quantiles = [(i + 1) / (num_splits + 1) for i in range(num_splits)]
    split_points += [round(bus_map_pos.lmp.quantile(val), 2) for val in quantiles]
    return split_points + [max_lmp]


def _construct_branch_data(branch_map, cong, datetime):
    """Add congestion data for each branch

    :param pandas.DataFrame branch_map: data frame of branch data
    :param pandas.DataFrame cong: data frame of congestion data for the selected hour
    :param pandas.Timestamp/numpy.datetime64/datetime.datetime datetime: timestamp of
        the hour to analyze
    :return: (*pandas.DataFrame*) -- modified branch data with congestion data added
        for each branch
    """
    # Add congestion to branch dataframe
    cong_hour = cong.loc[datetime]
    cong_hour = cong_hour.T
    cong_hour.name = "medianval"
    branch_map = pd.concat([branch_map, cong_hour], axis=1)

    # select branches that have a binding constraint and are of type Line
    branch_map = branch_map.loc[
        (branch_map["medianval"] > 1e-6) & (branch_map["branch_device_type"] == "Line")
    ]

    return branch_map


def _construct_shadowprice_visuals(
    interconnect, lmp_split_points, bus_segments, branch_data
):
    """Use bokeh to plot variation in lmp and shadow prices

    :param str interconnect: scenario interconnect
    :param list/tuple/set/numpy.array lmp_split_points: lmp values chosen to split
        the bus data
    :param list bus_segments: bus data split into 9 segments
    :param pandas.DataFrame branch_data: branch data
    :return: (*bokeh.models.layout.Row*) -- bokeh map visual in row layout.
    """

    tools = "pan,wheel_zoom,reset,hover,save"
    p = figure(
        title=f"{interconnect} Interconnect",
        tools=tools,
        x_axis_location=None,
        y_axis_location=None,
        plot_width=800,
        plot_height=800,
    )

    # Add USA map
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))

    # Add colored circles for bus locations
    indices = list(range(len(bus_segments)))
    indices.reverse()  # We want the lowest prices on top
    for i in indices:
        bus_cds = ColumnDataSource(
            {
                "x": bus_segments[i]["x"],
                "y": bus_segments[i]["y"],
                "lmp": bus_segments[i]["lmp"],
            }
        )
        p.circle(
            "x", "y", color=shadow_price_pallette[i], alpha=0.4, size=11, source=bus_cds
        )

    # Add branches
    branch_cds = ColumnDataSource(
        {
            "xs": branch_data[["from_x", "to_x"]].values.tolist(),
            "ys": branch_data[["from_y", "to_y"]].values.tolist(),
            "medianval": branch_data.medianval,
        }
    )
    # branch outline
    p.multi_line("xs", "ys", color="black", line_width=14, source=branch_cds)
    # branch color
    palette = shadow_price_pallette[-5:]
    mapper = linear_cmap(field_name="medianval", palette=palette, low=0, high=2000)
    p.multi_line("xs", "ys", color=mapper, line_width=9, source=branch_cds)

    # Add legends
    bus_legend = _construct_bus_legend(lmp_split_points)
    branch_legend = ColorBar(
        color_mapper=mapper["transform"],
        width=16,
        location=(0, 0),
        title="SP ($/MWh)",
        title_text_font_size="8pt",
        title_standoff=8,
    )

    p.add_layout(branch_legend, "right")

    return row(bus_legend, p)


def _construct_bus_legend(lmp_split_points):
    """Construct the legend for lmp at each bus

    :param list/tuple/set/numpy.array lmp_split_points: lmp values chosen to split
        the bus data
    :return: (*bokeh.plotting.figure*) -- the legend showing lmp for each bus
    """
    x_range = [""]
    bars, bar_len_sum, labels = _get_bus_legend_bars_and_labels(lmp_split_points)

    # Make legend
    p = figure(
        x_range=x_range,
        plot_height=800,
        plot_width=110,
        toolbar_location=None,
        tools="",
    )
    p.vbar_stack(
        [*bars],
        x="x_range",
        width=0.9,
        color=shadow_price_pallette[: len(bars)],
        source={**{"x_range": [""]}, **bars},
    )

    p.y_range.start = -1
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    p.yaxis.ticker = [*labels]
    p.yaxis.major_label_overrides = labels

    p.text(
        x=[-0.05],
        y=[bar_len_sum * 1.01],
        text=["LMP ($/MWh)"],
        text_font_size="8pt",
        text_font_style="italic",
    )

    return p


def _get_bus_legend_bars_and_labels(lmp_split_points):
    """Get the bar lengths and labels for the bus legend

    :param list/tuple/set/numpy.array lmp_split_points: lmp values chosen to split
        the bus data
    :return: (*tuple*) -- bar lengths and labels for the bus legend
    """
    bars = {}
    bar_length_sum = 0
    labels = {}  # { y-position: label_text, ... }
    for i, (p, c) in enumerate(zip(lmp_split_points, lmp_split_points[1:])):
        bar_length = max(1, min(5, c - p))
        bars[str(i)] = [bar_length]
        labels[bar_length_sum] = str(p)
        bar_length_sum += bar_length

    labels[bar_length_sum] = str(c)
    return bars, bar_length_sum, labels
