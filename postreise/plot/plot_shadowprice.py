import numpy as np
import pandas as pd
from bokeh.io import output_notebook, show
from bokeh.layouts import row
from bokeh.models import ColorBar, ColumnDataSource
from bokeh.plotting import figure
from bokeh.tile_providers import Vendors, get_provider
from bokeh.transform import linear_cmap
from powersimdata.scenario.scenario import Scenario

from postreise.plot.multi.constants import SHADOW_PRICE_COLORS
from postreise.plot.projection_helpers import project_branch, project_bus


def plot_shadowprice(scenario_id, hour, lmp_split_points=None):
    """Make map lmp variation and shadow prices

    :param scenario_id: the id of the scenario to gather data from
    :type scenario_id: string
    :param hour: the hour we will be analyzing
    :type hour: string
    :param lmp_split_points: the locational marginal pricing (lmp) values
        we have chosen to split the bus data. Includes min and max values.
        Must have 10 items or fewer. defaults to None
        example: [-1, 1, 20, 25, 30, 35, 40, 100]
    :type lmp_split_points: list(float), optional
    :raises ValueError: lmp_split_points must have 10 items or fewer
    """
    if lmp_split_points is not None and len(lmp_split_points) > 10:
        raise ValueError("ERROR: lmp_split_points must have 10 items or fewer")

    interconnect, bus, lmp, branch, cong = _get_shadowprice_data(scenario_id)
    lmp_split_points, bus_segments = _construct_bus_data(
        bus, lmp, lmp_split_points, hour
    )
    branches_selected = _construct_branch_data(branch, cong, hour)
    _construct_shadowprice_visuals(
        interconnect, lmp_split_points, bus_segments, branches_selected
    )


def _get_shadowprice_data(scenario_id):
    """Get data necessary for plotting shadowprice

    :param scenario_id: the id of the scenario to gather data from
    :type scenario_id: string
    :return: interconnect, bus data, lmp data, branch data, congestion data
    :rtype: string, pandas.DataFrame, pandas.DataFrame, pandas.DataFrame,
        pandas.DataFrame
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


def _construct_bus_data(bus_map, lmp, user_set_split_points, hour):
    """Adds lmp data to each bus, splits buses into 9 segments by lmp

    :param bus_map: bus dataframe with location data
    :type bus_map: pandas.DataFrame
    :param lmp: lmp dataframe
    :type lmp: pandas.DataFrame
    :param user_set_split_points: user-set lmp values to split the bus data.
        Must have 10 items or fewer
        example: [-1, 1, 20, 25, 30, 35, 40, 100]
    :type user_set_split_points: list(float), None
    :param hour: the hour we will be analyzing
    :type hour: string
    :return: the lmp vals we have chosen to split the bus data,
        bus data split into segments
    :rtype: list(float), list(pandas.DataFrame)
    """
    # Add lmp to bus dataframe
    lmp_hour = lmp[lmp.index == hour]
    lmp_hour = lmp_hour.T
    lmp_hour = lmp_hour.rename(columns={lmp_hour.columns[0]: "lmp"})
    bus_map = pd.concat([bus_map, lmp_hour], axis=1)

    lmp_split_points = (
        user_set_split_points
        if user_set_split_points is not None
        else _get_lmp_split_points(bus_map)
    )

    bus_segments = []
    for i in range(len(lmp_split_points) - 1):
        bus_segment = bus_map[
            (bus_map["lmp"] > lmp_split_points[i])
            & (bus_map["lmp"] <= lmp_split_points[i + 1])
        ]
        bus_segments.append(bus_segment)

    return lmp_split_points, bus_segments


def _get_lmp_split_points(bus_map):
    """Determine up to ten points to split the bus data (inc. min and max lmp).
        Always split on lmp -1 and 1 if possible
        Split the rest of the buses into groups
        with an equal number of members

    :param bus_map: bus data with lmp
    :type bus_map: pandas.DataFrame
    :return: the lmp vals we have chosen to split the bus data
    :rtype: list(float)
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


def _construct_branch_data(branch_map, cong, hour):
    """Adds congestion data for each branch

    :param branch_map: dataframe of branch data
    :type branch_map: pandas.DataFrame
    :param cong: dataframe of congestion data for the selected hour
    :type cong: pandas.DataFrame
    :param hour: the hour we will be analyzing
    :type hour: string
    :return: modified branch data adding congestion data for each branch
    :rtype: pandas.DataFrame
    """
    # Add congestion to branch dataframe
    cong_hour = cong.iloc[cong.index == hour]
    cong_hour = cong_hour.T
    cong_hour = cong_hour.rename(columns={cong_hour.columns[0]: "medianval"})
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

    :param interconnect: the scenario interconnect
    :type interconnect: string
    :param lmp_split_points: the lmp vals we have chosen to split the bus data
    :type lmp_split_points: list(float)
    :param bus_segments: bus data split into 9 segments
    :type bus_segments: list(pandas.DataFrame)
    :param branch_data: branch data
    :type branch_data: pandas.DataFrame
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
            "x", "y", color=SHADOW_PRICE_COLORS[i], alpha=0.4, size=11, source=bus_cds
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
    palette = SHADOW_PRICE_COLORS[-5:]
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

    output_notebook()
    show(row(bus_legend, p))


def _construct_bus_legend(lmp_split_points):
    """Construct the legend for lmp at each bus

    :param lmp_split_points: the lmp values we have chosen to
        split the bus data
    :type lmp_split_points: list(float)
    :return: the legend showing lmp for each bus
    :rtype: bokeh.plotting.figure
    """
    x_range = [""]
    bars, bar_len_sum, labels = _get_bus_legend_bars_and_labels(
        lmp_split_points, x_range
    )

    # Make legend
    p = figure(
        x_range=x_range,
        plot_height=800,
        plot_width=110,
        toolbar_location=None,
        tools="",
    )
    p.vbar_stack(
        list(bars.keys())[1:],
        x="x_range",
        width=0.9,
        color=SHADOW_PRICE_COLORS[: (len(bars) - 1)],
        source=bars,
    )

    p.y_range.start = -1
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    p.yaxis.ticker = list(labels.keys())
    p.yaxis.major_label_overrides = labels

    p.text(
        x=[-0.05],
        y=[bar_len_sum * 1.01],
        text=[f"LMP ($/MWh)"],
        text_font_size="8pt",
        text_font_style="italic",
    )

    return p


def _get_bus_legend_bars_and_labels(lmp_split_points, x_range):
    """get the bar lengths and labels for the bus legend

    :param lmp_split_points: the lmp vs we have chosen to split the bus data
    :type lmp_split_points: list(float)
    :param x_range: the x-range for the vbar_stack
    :type x_range: list(string)
    :return: bar lengths and labels for the bus legend
    :rtype: dict, float, dict
    """
    bars = {"x_range": x_range}
    bar_length_sum = 0
    labels = {}  # { y-position: label_text, ... }
    for i in range(len(lmp_split_points)):
        bar_length = 0
        if i == 0 or i == len(lmp_split_points) - 2:
            # For first and last bars, clamp bar length between 1 and 5
            # to prevent extreme min and max vals from overwhelming the legend
            lmp_diff = lmp_split_points[i + 1] - lmp_split_points[i]
            bar_length = 1 if lmp_diff < 1 else 5 if lmp_diff > 5 else lmp_diff
        elif i != len(lmp_split_points) - 1:
            # max_lmp has a label but no bar
            lmp_diff = lmp_split_points[i + 1] - lmp_split_points[i]
            # Min bar length of 1 to ensure small bars are visible
            bar_length = max(1, round(lmp_diff, 1))

        labels[round(bar_length_sum, 1)] = str(lmp_split_points[i])
        if i != len(lmp_split_points) - 1:
            bars[str(i)] = [bar_length]
            bar_length_sum += bar_length

    return bars, bar_length_sum, labels
