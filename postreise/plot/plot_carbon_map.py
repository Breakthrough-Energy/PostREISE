import numpy as np
import pandas as pd
from bokeh.layouts import row
from bokeh.models import ColumnDataSource, HoverTool, Label, LabelSet
from bokeh.plotting import figure
from bokeh.sampledata import us_states
from bokeh.tile_providers import Vendors, get_provider

from postreise.plot.colors import be_green, be_purple, be_red
from postreise.plot.projection_helpers import project_borders, project_bus


def group_lat_lon(bus_map, agg=True):
    """Groups data and sums values, based on coordinates.
        Rounds to the nearest lat lon degrees

    :param pandas.DataFrame bus_map: data frame with coal, ng, and lat lon
        coordinates per bus
    :param boolean agg: aggregate by rounded lat/lon if true
    :return: (pandas.DataFrame) -- data frame, aggregated by rounded lat lon
        coordinates
    """
    bus_map1 = bus_map
    if agg:
        bus_map1.lat = bus_map1.lat.round(1)
        bus_map1.lon = bus_map1.lon.round(1)

    bus_map1 = bus_map1.groupby(["lat", "lon", "color", "type"]).agg(
        {"coal": "sum", "ng": "sum", "x": "mean", "y": "mean"}
    )
    bus_map1 = bus_map1.reset_index()
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
    us_states_dat=None,
    size_factor=1.0,
):
    """Makes map of carbon emissions, color code by fuel type. Size/area
        indicates emissions.

    :param dict us_states_dat: if None default to us_states data file, imported from bokeh
    :param pandas.DataFrame bus_info_and_emission: info and
        emission of buses by :func:`combine_bus_info_and_emission`.
    :param str scenario_name: name of scenario for labeling.
    :param str color_coal: color assigned for coal
    :param str color_ng: color assigned for natural gas
    :param float size_factor: height scale for bars
    """

    if us_states_dat is None:
        us_states_dat = us_states.data

    bus_map = project_bus(bus_info_and_emission)
    bus_map = group_zone(bus_map)

    a, b = project_borders(us_states_dat)

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


def _prepare_busmap(
    bus_info_and_emission, color_ng, color_coal, agg, type1="natural gas", type2="coal"
):
    """Prepare data with amount of emissions and type for hover tips

    :param pandas.DataFrame bus_info_and_emission: info and emission of buses
        as returned by :func:`combine_bus_info_and_emission`.
    :param str color_ng: color assigned for ng, default to BE purple
    :param str color_coal: color associated with coal, default to black/gray
        :param boolean agg: if true, aggregates points by lat lon within a given radius
    :param str type1: label for hover over tool tips, first color/type
        (usual choices: natural gas or increase if making a diff map)
    :param str type2: label for hover over tool tips, second color/type
        (usual choices: coal or decrease if making diff map)
    :return: (pandas.DataFrame) -- data frame with amount and tye fields
    """
    bus_map = bus_info_and_emission
    bus_map["color"] = ""
    bus_map["type"] = ""
    bus_map.loc[(bus_map["ng"] > 0), "color"] = color_ng
    bus_map.loc[(bus_map["coal"] > 0), "color"] = color_coal
    bus_map.loc[(bus_map["ng"] > 0), "type"] = type1
    bus_map.loc[(bus_map["coal"] > 0), "type"] = type2

    bus_map = project_bus(bus_map)
    bus_map1 = group_lat_lon(bus_map, agg=agg)
    bus_map1["amount"] = bus_map1["ng"] + bus_map1["coal"]
    return bus_map1


def map_carbon_emission(
    bus_info_and_emission,
    color_coal="black",
    color_ng=be_purple,
    label_coal=u"Coal: CO\u2082",
    label_ng=u"Natural gas: CO\u2082",
    us_states_dat=None,
    size_factor=1,
    web=True,
    agg=True,
    type1="natural gas",
    type2="coal",
):
    """Makes map of carbon emissions, color code by fuel type. Size/area
        indicates emissions.

    :param pandas.DataFrame bus_info_and_emission: info and emission of buses
        as returned by :func:`combine_bus_info_and_emission`.
    :param str color_ng: color assigned for ng, default to BE purple
    :param str color_coal: color associated with coal, default to black/gray
    :param str label_coal: label for legend associated with coal.
    :param str label_ng: label for legend associated with ng.
    :param dict us_states_dat: if None default to us_states data file, imported from bokeh
    :param float size_factor: scaling factor for size of emissions circles glyphs
    :param boolean web: if true, optimizes figure for web-based presentation
    :param boolean agg: if true, aggregates points by lat lon within a given radius
    :param str type1: label for hover over tool tips, first color/type
        (usual choices: natural gas or increase if making a diff map)
    :param str type2: label for hover over tool tips, second color/type
        (usual choices: coal or decrease if making diff map)
    """

    # us states borders, prepare data
    if us_states_dat is None:
        us_states_dat = us_states.data
    a, b = project_borders(us_states_dat)

    # prepare data frame for emissions data
    bus_map = _prepare_busmap(
        bus_info_and_emission, color_ng, color_coal, agg=agg, type1=type1, type2=type2
    )
    bus_map = bus_map.sort_values(by=["color"])

    bus_source = ColumnDataSource(
        {
            "x": bus_map["x"],
            "y": bus_map["y"],
            "size": (bus_map["amount"] / 10000 * size_factor) ** 0.5 + 2,
            "radius": (bus_map["amount"] * 1000 * size_factor) ** 0.5 + 10,
            "tons": bus_map["amount"],
            "color": bus_map["color"],
            "type": bus_map["type"],
        }
    )

    # Set up figure
    tools: str = "pan,wheel_zoom,reset,save"
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

    # circle glyphs that exist only for the web legend,
    # these are plotted behind the tiles, not visible
    p.circle(
        -8.1e6,
        5.2e6,
        fill_color=color_coal,
        color=color_coal,
        alpha=0.5,
        size=50,
        legend_label=label_coal,
    )
    p.circle(
        -8.1e6,
        5.2e6,
        fill_color=color_ng,
        color=color_ng,
        alpha=0.5,
        size=50,
        legend_label=label_ng,
    )

    p.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))
    # state borders
    p.patches(a, b, fill_alpha=0.0, line_color="gray", line_width=2)

    # emissions circles, web version
    if web:

        circle = p.circle(
            "x",
            "y",
            fill_color="color",
            color="color",
            alpha=0.25,
            radius="radius",
            source=bus_source,
        )

    else:
        p.circle(
            "x",
            "y",
            fill_color="color",
            color="color",
            alpha=0.25,
            size="size",
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
            (10000000 / 10000 * size_factor) ** 0.5 + 2,
            (5000000 / 10000 * size_factor) ** 0.5 + 2,
            (1000000 / 10000 * size_factor) ** 0.5 + 2,
        ]
        * 2,
    )
    source = ColumnDataSource(
        data=dict(
            x=[1, 1, 1, 0.3, 1, 1, 1, 0.3],
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

    if web:
        p.legend.location = "bottom_right"
        p.legend.label_text_font_size = "12pt"

        hover = HoverTool(
            tooltips=[
                ("Type", "@type"),
                (u"Tons CO\u2082", "@tons"),
            ],
            renderers=[circle],
        )

        p.add_tools(hover)
        return_p = p

    else:
        p.legend.visible = False
        return_p = row(p_legend, p)
    return return_p


def map_carbon_emission_comparison(
    bus_info_and_emission_1, bus_info_and_emission_2, web=True
):
    """Makes map of carbon emissions, color code by fuel type, size/area
        indicates emissions Also, returns data frame enclosing emission
        released by thermal generators.

    :param pandas.DataFrame bus_info_and_emission_1: info and emission
        of buses for 1st scenario
        returned by :func:`combine_bus_info_and_emission`.
    :param pandas.DataFrame bus_info_and_emission_2: info and emission
        of buses for 2nd scenario
        as returned by :func:`combine_bus_info_and_emission`.
    :param boolean web: if true, optimizes figure for web-based presentation
    :return: (pandas.DataFrame) -- comparison map indicating increase or
        decrease in emission
    """
    # merge
    bus_info_and_emission_1 = bus_info_and_emission_1.fillna(0)
    bus_info_and_emission_2 = bus_info_and_emission_2.fillna(0)

    bus_info_and_emission_1["amt"] = (
        bus_info_and_emission_1["ng"] + bus_info_and_emission_1["coal"]
    )
    bus_info_and_emission_2["amt"] = (
        bus_info_and_emission_2["ng"] + bus_info_and_emission_2["coal"]
    )

    bus_map = bus_info_and_emission_1.merge(
        bus_info_and_emission_2,
        right_index=True,
        left_index=True,
        suffixes=("_x", "_y"),
        how="outer",
    )
    # fill 0s so we can subtract
    bus_map = bus_map.fillna(0)

    bus_map["amt_dif"] = bus_map["amt_x"] - bus_map["amt_y"]
    bus_map["lon"] = bus_map["lon_x"].fillna(bus_map["lon_y"])
    bus_map["lat"] = bus_map["lat_x"].fillna(bus_map["lat_y"])
    bus_map["coal"] = 0
    bus_map["ng"] = 0
    bus_map.loc[bus_map.amt_dif > 0, ["coal"]] = bus_map["amt_dif"]

    bus_map.loc[bus_map.amt_dif < 0, ["ng"]] = abs(bus_map["amt_dif"])

    bus_map2 = bus_map[bus_map.amt_dif != 0]
    bus_map2 = project_bus(bus_map2)
    bus_map2 = _prepare_busmap(
        bus_map2, be_green, be_red, agg=False, type1="increase", type2="decrease"
    )

    p = map_carbon_emission(
        bus_map2,
        be_green,
        be_red,
        u"Less tons CO\u2082",
        u"More tons CO\u2082",
        web=web,
        type1="increase",
        type2="decrease",
    )

    return p


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
