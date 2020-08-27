import numpy as np
import pandas as pd
from bokeh.plotting import show, figure
from bokeh.tile_providers import get_provider, Vendors
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, LabelSet, Label
from bokeh.layouts import row
from bokeh.sampledata import us_states
from postreise.plot.projection_helpers import project_bus
from pyproj import Transformer

# make default states list
default_states_dict = us_states.data.copy()
del default_states_dict["HI"]
del default_states_dict["AK"]
default_states_list = list(default_states_dict.keys())


def get_borders(us_states_dat, state_list=None):
    """Prepares US state borders data for use on the map.

    :param dict us_states_dat: us_states data file, imported from bokeh
    :param list state_list: us states, defaults to all states except AK and HI
    :return: (*tuple*) -- reprojected coordinates for use on map.
    """
    # separate latitude and longitude points for the borders of the states.
    if state_list is None:
        state_list = default_states_list
    num_states = len(state_list)
    us_states_dat = dict((k, us_states_dat[k]) for k in state_list)
    state_lats = [us_states_dat[code]["lats"] for code in us_states_dat]
    state_lons = [us_states_dat[code]["lons"] for code in us_states_dat]
    # transform/re-project coordinates for Bokeh
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    all_state_xs = []
    all_state_ys = []
    for j in range(num_states):
        state_xs, state_ys = transformer.transform(state_lats[j], state_lons[j])
        all_state_xs.append(state_xs)
        all_state_ys.append(state_ys)

    return all_state_xs, all_state_ys


def plot_states(
    state_list, col_list, labels_list, font_size, us_states_dat=us_states.data
):
    """Plots US state borders and allows color coding by state,
        for example to represent different emissions goals.

    :param labels_list: list of labels for us states.
    :param state_list: list of us states to color code.
    :param col_list: list of colors associated with states in state_list.
    :param dict us_states_dat: us_states data file, imported from bokeh.
    :return:  -- map of us states with option to color by value.
    """
    # warn if inputs diff lengths
    if len(state_list) != len(col_list):
        print("warning: state_list and col_list must be same length")
    if len(state_list) != len(labels_list):
        print("warning: state_list and labels_list must be same length")

    a, b = get_borders(us_states_dat.copy())

    tools: str = "pan,wheel_zoom,reset,hover,save"
    p = figure(
        title="US States",
        tools=tools,
        x_axis_location=None,
        y_axis_location=None,
        plot_width=800,
        plot_height=800,
    )
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))
    p.patches(a, b, fill_alpha=0, fill_color="blue", line_color="black", line_width=2)
    # counter
    n = -1
    # loop through states and colors, plot patches
    for i in state_list:
        n = n + 1
        a1, b1 = get_borders(us_states_dat.copy(), state_list=[i])
        p.patches(
            a1,
            b1,
            fill_alpha=0.8,
            fill_color=[col_list[n]],
            line_color="black",
            line_width=2,
        )
        citation = Label(
            x=min(a1[0]) + 100000,
            y=(max(b1[0]) + min(b1[0])) / 2,
            x_units="data",
            y_units="data",
            text_font_size=font_size,
            text=labels_list[n],
            render_mode="css",
            border_line_color="black",
            border_line_alpha=0,
            background_fill_color="white",
            background_fill_alpha=0.8,
        )
        p.add_layout(citation)
    return p


def group_lat_lon(bus_map):
    """Groups data and sums values, based on coordinates.
        Rounds to the nearest lat lon degrees

    :param pandas.DataFrame bus_map: data frame with coal, ng, and lat lon
        coordinates per bus
    :return: (pandas.DataFrame) -- data frame, aggregated by rounded lat lon
        coordinates
    """
    bus_map1 = bus_map

    bus_map1.lat = bus_map1.lat.round()
    bus_map1.lon = bus_map1.lon.round()

    bus_map1 = bus_map1.groupby(["lat", "lon"]).agg(
        {"coal": "sum", "ng": "sum", "x": "mean", "y": "mean"}
    )

    return bus_map1


def group_zone(bus_map):
    """Groups data and sums values, based on zone,
    with zones in the same state aggregated. To get the 'center'
    of each state, the midway point between the max and min
    for lat and lon are calculated.

    :param pandas.DataFrame bus_map: data frame with
     coal, ng, and zone id per bus
    :return: (pandas.DataFrame) -- data frame, aggregated by us state
        coordinates
    """
    bus_map1 = bus_map
    # for states with multiple zones, consolidate
    bus_map1["zone_id"] = bus_map1["zone_id"].replace([203, 204, 205, 206], 207)

    # bus_map1 = bus_map1.groupby(["zone_id"]).agg(
    # {'coal': 'sum', 'ng': 'sum', 'x': 'mean',
    #  'y': 'mean'})
    bus_map1 = bus_map1.groupby("zone_id").agg(
        coal=pd.NamedAgg(column="coal", aggfunc="sum"),
        ng=pd.NamedAgg(column="ng", aggfunc="sum"),
        max_x=pd.NamedAgg(column="x", aggfunc="max"),
        min_x=pd.NamedAgg(column="x", aggfunc="min"),
        max_y=pd.NamedAgg(column="y", aggfunc="max"),
        min_y=pd.NamedAgg(column="y", aggfunc="min"),
    )

    # average of x coordinates, towards the bottom of y coordinates by state
    bus_map1["x"] = (bus_map1["max_x"] + bus_map1["min_x"]) / 2
    bus_map1["y"] = (bus_map1["max_y"] - bus_map1["min_y"]) / 4 + bus_map1["min_y"]

    return bus_map1


def map_carbon_emission_bar(
    bus_info_and_emission,
    scenario_name,
    color_coal="black",
    color_ng="purple",
    us_states_dat=us_states.data,
    size_factor=1.0,
):
    """Makes map of carbon emissions, color code by fuel type. Size/area
        indicates emissions.

    :param dict us_states_dat: us_states data file, imported from bokeh
    :param pandas.DataFrame bus_info_and_emission: info and
        emission of buses by :func:`combine_bus_info_and_emission`.
    :param str scenario_name: name of scenario for labeling.
    :param str color_coal: color assigned for coal
    :param str color_ng: color assigned for natural gas
    :param float size_factor: height scale for bars
    """

    bus_map = project_bus(bus_info_and_emission)
    bus_map = group_zone(bus_map)

    a, b = get_borders(us_states_dat.copy())

    # plotting adjustment constants
    ha = 85000
    size_factor = size_factor * 0.02

    bus_source = ColumnDataSource(
        {
            "x": bus_map["x"],
            "x2": bus_map["x"] + ha * 2,
            "y": bus_map["y"],
            "coaly": bus_map["y"] + bus_map["coal"] * size_factor,
            "ngy": bus_map["y"] + bus_map["ng"] * size_factor,
        }
    )

    # Set up figure
    tools: str = "pan,wheel_zoom,reset,hover,save"
    p = figure(
        title=scenario_name,
        tools=tools,
        x_axis_location=None,
        y_axis_location=None,
        plot_width=800,
        plot_height=800,
    )
    p_legend = figure(
        x_axis_location=None,
        y_axis_location=None,
        toolbar_location=None,
        plot_width=200,
        plot_height=200,
        y_range=(0, 2),
        x_range=(0, 2),
    )
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))
    # state borders
    p.patches(a, b, fill_alpha=0.0, line_color="black", line_width=2)

    # emissions bars
    width = 150000.0
    alpha = 0.7
    p.vbar(
        x="x2",
        bottom="y",
        top="coaly",
        width=width,
        color=color_coal,
        source=bus_source,
        alpha=alpha,
    )
    p.vbar(
        x="x",
        bottom="y",
        top="ngy",
        width=width,
        color=color_ng,
        source=bus_source,
        alpha=alpha,
    )
    bus_map = pd.DataFrame(bus_map)

    # citation fields
    cit_x = []
    cit_y = []
    cit_text = []

    # constants for adjustments of text labels
    va = 1000
    m = 1000000

    # x values are offset so vbars are side by side.
    cit_x.append([i - ha * 1.5 for i in bus_map.x.values.tolist()])
    cit_x.append([i + ha for i in bus_map.x.values.tolist()])
    cit_y.append(
        np.add(
            [i + va * 2 for i in bus_map.y.values.tolist()],
            [i * size_factor for i in bus_map.ng.values.tolist()],
        )
    )
    cit_y.append(
        np.add(
            [i + va * 2 for i in bus_map.y.values.tolist()],
            [i * size_factor for i in bus_map.coal.values.tolist()],
        )
    )
    cit_text.append(
        [round(num, 1) for num in [i / m for i in bus_map.ng.values.tolist()]]
    )
    cit_text.append(
        [round(num, 1) for num in [i / m for i in bus_map.coal.values.tolist()]]
    )

    for j in range(0, len(cit_x)):
        for i in range(0, len(cit_x[j])):
            citation = Label(
                x=cit_x[j][i],
                y=cit_y[j][i],
                x_units="data",
                y_units="data",
                text_font_size="20pt",
                text=str(cit_text[j][i]),
                render_mode="css",
                border_line_color="black",
                border_line_alpha=0,
                background_fill_color="white",
                background_fill_alpha=0.8,
            )
            p.add_layout(citation)

    # custom legend
    p_legend.square(1, 1, fill_color="white", color="white", size=600)
    p_legend.square(1, 1, fill_color="white", color="black", size=400)
    p_legend.square(0.4, 0.8, fill_color="black", color="black", size=40, alpha=0.7)
    p_legend.square(0.4, 0.2, fill_color="purple", color="purple", size=40, alpha=0.7)
    source = ColumnDataSource(
        data=dict(
            x=[0.7, 0.7, 0.05],
            y=[0.6, 0.1, 1.5],
            text=["Coal", "Natural Gas", "Emissions (Million Tons)"],
        )
    )
    labels = LabelSet(
        x="x",
        y="y",
        text="text",
        source=source,
        level="glyph",
        x_offset=0,
        y_offset=0,
        render_mode="css",
        text_font_size="20pt",
    )
    p_legend.add_layout(labels)

    return row(p_legend, p)


def map_carbon_emission(
    bus_info_and_emission,
    scenario_name,
    color_coal="black",
    color_ng="purple",
    label_coal="Coal: tons",
    label_ng="NG: tons",
    us_states_dat=us_states.data,
    size_factor=1,
):
    """Makes map of carbon emissions, color code by fuel type. Size/area
        indicates emissions.

    :param pandas.DataFrame bus_info_and_emission: info and emission of buses
        as returned by :func:`combine_bus_info_and_emission`.
    :param str scenario_name: name of scenario for labeling.
    :param str color_coal: color assigned for coal, default to black.
    :param str color_ng: color assigned for ng, default to purple.
    :param str label_coal: label for legend associated with coal.
    :param str label_ng: label for legend associated with ng.
    :param dict us_states_dat: us_states data file, imported from bokeh
    """
    bus_map = project_bus(bus_info_and_emission)
    bus_map = group_lat_lon(bus_map)

    a, b = get_borders(us_states_dat.copy())

    bus_source = ColumnDataSource(
        {
            "x": bus_map["x"],
            "y": bus_map["y"],
            "coal": (bus_map["coal"] / 1000 * size_factor) ** 0.5,
            "ng": (bus_map["ng"] / 1000 * size_factor) ** 0.5,
        }
    )

    # Set up figure
    tools: str = "pan,wheel_zoom,reset,hover,save"
    p = figure(
        title=scenario_name,
        tools=tools,
        x_axis_location=None,
        y_axis_location=None,
        plot_width=800,
        plot_height=800,
        output_backend="webgl",
    )
    p_legend = figure(
        x_axis_location=None,
        y_axis_location=None,
        toolbar_location=None,
        plot_width=200,
        plot_height=400,
        y_range=(0, 4),
        x_range=(0, 2),
        output_backend="webgl",
    )
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))
    # state borders
    p.patches(a, b, fill_alpha=0.0, line_color="black", line_width=2)
    # emissions circles
    p.circle(
        "x",
        "y",
        fill_color=color_coal,
        color=color_coal,
        alpha=0.25,
        size="coal",
        source=bus_source,
    )
    p.circle(
        "x",
        "y",
        fill_color=color_ng,
        color=color_ng,
        alpha=0.25,
        size="ng",
        source=bus_source,
    )

    # legend: white square background and bars per color code
    p_legend.square(1, [1, 3], fill_color="white", color="white", size=300)
    p_legend.square(
        1, [1, 3], fill_color="white", color="black", size=(2000000 / 100) ** 0.5
    )
    p_legend.circle(
        1,
        y=np.repeat([1, 3], 3),
        fill_color=np.repeat([color_coal, color_ng], 3),
        color=np.repeat([color_coal, color_ng], 3),
        alpha=0.25,
        size=[
            (10000000 / 1000 * size_factor) ** 0.5,
            (5000000 / 1000 * size_factor) ** 0.5,
            (1000000 / 1000 * size_factor) ** 0.5,
        ]
        * 2,
    )
    source = ColumnDataSource(
        data=dict(
            x=[1, 1, 1, 0.5, 1, 1, 1, 0.5],
            y=[0.9, 1.1, 1.3, 1.55, 2.9, 3.1, 3.3, 3.55],
            text=["1M", "5M", "10M", label_coal, "1M", "5M", "10M", label_ng],
        )
    )
    labels = LabelSet(
        x="x",
        y="y",
        text="text",
        source=source,
        level="glyph",
        x_offset=0,
        y_offset=0,
        render_mode="css",
    )
    p_legend.add_layout(labels)

    return row(p_legend, p)


def map_carbon_emission_comparison(bus_info_and_emission_1, bus_info_and_emission_2):
    """Makes map of carbon emissions, color code by fuel type, size/area
        indicates emissions Also, returns data frame enclosing emission
        released by thermal generators.

    :param pandas.DataFrame bus_info_and_emission_1: info and emission
        of buses for 1st scenario
        returned by :func:`combine_bus_info_and_emission`.
    :param pandas.DataFrame bus_info_and_emission_2: info and emission
        of buses for 2nd scenario
        as returned by :func:`combine_bus_info_and_emission`.
    :return: (pandas.DataFrame) -- comparison map indicating increase or
        decrease in emission
    """
    bus_map = bus_info_and_emission_1.merge(
        bus_info_and_emission_2, right_index=True, left_index=True, how="outer"
    )

    bus_map.coal_x = bus_map.coal_x.fillna(0)
    bus_map.coal_y = bus_map.coal_y.fillna(0)
    bus_map.ng_x = bus_map.ng_x.fillna(0)
    bus_map.ng_y = bus_map.ng_y.fillna(0)

    bus_map["coal_dif"] = bus_map["coal_x"] - bus_map["coal_y"]
    bus_map["ng_dif"] = bus_map["ng_x"] - bus_map["ng_y"]
    bus_map["lon"] = bus_map["lon_x"].fillna(bus_map["lon_y"])
    bus_map["lat"] = bus_map["lat_x"].fillna(bus_map["lat_y"])
    bus_map["coal"] = 0
    bus_map["ng"] = 0
    bus_map.loc[bus_map.coal_dif > 0, ["coal"]] = bus_map["coal_dif"]
    bus_map.loc[bus_map.ng_dif > 0, ["coal"]] = bus_map["ng_dif"]

    bus_map.loc[bus_map.coal_dif < 0, ["ng"]] = abs(bus_map["coal_dif"])
    bus_map.loc[bus_map.ng_dif < 0, ["ng"]] = abs(bus_map["ng_dif"])

    map_carbon_emission(bus_map, "compare", "green", "red", "Less: tons", "More: tons")

    return bus_map


def combine_bus_info_and_emission(bus_info, carbon_by_bus):
    """Builds data frame needed for plotting carbon emitted by thermal
        generators.

    :param pandas.DataFrame bus_info: bus data frame.
    :param dict carbon_by_bus: keys are fuel type and values is a dictionary
        where keys and values are the bus id and emission, respectively.
        This is returned by
        :func:`postreise.analyze.generation.carbon.summarize_carbon_by_bus`.
    :return: (*pandas.DataFrame*) -- combined data frame.
    """

    bus_of_interest = bus_info.loc[pd.DataFrame.from_dict(carbon_by_bus).index]
    bus_info_and_emission = bus_of_interest.merge(
        pd.DataFrame.from_dict(carbon_by_bus), right_index=True, left_index=True
    )

    return bus_info_and_emission
