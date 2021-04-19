# This plotting module has a corresponding demo notebook in
#   PostREISE/postreise/plot/demo: utilization_map_demo.ipynb

import numpy as np
import pandas as pd
from bokeh.models import ColorBar, ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.tile_providers import Vendors, get_provider
from bokeh.transform import linear_cmap

from postreise.plot.colors import traffic_palette
from postreise.plot.plot_states import get_state_borders
from postreise.plot.projection_helpers import project_borders, project_branch


def map_risk_bind(
    risk_or_bind,
    congestion_stats,
    branch,
    us_states_dat=None,
    vmin=None,
    vmax=None,
    is_website=False,
):
    """Makes map showing risk or binding incidents on US states map.

    :param str risk_or_bind: specify plotting "risk" or "bind"
    :param pandas.DataFrame congestion_stats: data frame as returned by
        :func:`postreise.analyze.transmission.utilization.generate_cong_stats`.
    :param pandas.DataFrame branch: branch data frame.
    :param dict us_states_dat: dictionary of state border lats/lons. If None, get
        from :func:`postreise.plot.plot_states.get_state_borders`.
    :param int/float vmin: minimum value for color range. If None, use data minimum.
    :param int/float vmax: maximum value for color range. If None, use data maximum.
    :param bool is_website: changes text/legend formatting to look better on the website
    :return:  -- map of lines with risk and bind incidents color coded
    """
    if us_states_dat is None:
        us_states_dat = get_state_borders()

    if risk_or_bind == "risk":
        risk_or_bind_units = "Risk (MWH)"

    if risk_or_bind == "bind":
        risk_or_bind_units = "Binding incidents"

    # projection steps for mapping
    branch_congestion = pd.concat(
        [branch.loc[congestion_stats.index], congestion_stats], axis=1
    )
    branch_map_all = project_branch(branch)
    multi_line_source_all = ColumnDataSource(
        {
            "xs": branch_map_all[["from_x", "to_x"]].values.tolist(),
            "ys": branch_map_all[["from_y", "to_y"]].values.tolist(),
            "cap": branch_map_all["rateA"] / 2000 + 0.2,
        }
    )
    a, b = project_borders(us_states_dat)
    tools: str = "pan,wheel_zoom,reset,save"

    branch_congestion = branch_congestion[branch_congestion[risk_or_bind] > 0]
    branch_congestion.sort_values(by=[risk_or_bind])
    branch_map = project_branch(branch_congestion)
    min_val = branch_congestion[risk_or_bind].min() if vmin is None else vmin
    max_val = branch_congestion[risk_or_bind].max() if vmax is None else vmax
    mapper = linear_cmap(
        field_name=risk_or_bind, palette=traffic_palette, low=min_val, high=max_val
    )
    color_bar = ColorBar(
        color_mapper=mapper["transform"],
        width=385 if is_website else 500,
        height=5,
        location=(0, 0),
        title=risk_or_bind_units,
        orientation="horizontal",
        padding=5,
    )
    multi_line_source = ColumnDataSource(
        {
            "xs": branch_map[["from_x", "to_x"]].values.tolist(),
            "ys": branch_map[["from_y", "to_y"]].values.tolist(),
            risk_or_bind: branch_map[risk_or_bind],
            "value": branch_map[risk_or_bind].round(),
            "cap": branch_map["capacity"] / 1000 + 2,
            "capacity": branch_map.rateA.round(),
        }
    )

    # Set up figure
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
    p.add_layout(color_bar, "center")
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))
    p.patches(a, b, fill_alpha=0.0, line_color="gray", line_width=1)
    p.multi_line(
        "xs",
        "ys",
        color="gray",
        line_width="cap",
        source=multi_line_source_all,
        alpha=0.5,
    )
    lines = p.multi_line(
        "xs", "ys", color=mapper, line_width="cap", source=multi_line_source
    )
    hover = HoverTool(
        tooltips=[
            ("Capacity MW", "@capacity"),
            (risk_or_bind_units, "@value"),
        ],
        renderers=[lines],
    )
    p.add_tools(hover)
    return p


def map_utilization(
    utilization_df, branch, us_states_dat=None, vmin=None, vmax=None, is_website=False
):
    """Makes map showing utilization. Utilization input can either be medians
    only, or can be normalized utilization dataframe

    :param pandas.DataFrame utilization_df: utilization returned by
        :func:`postreise.analyze.transmission.utilization.get_utilization`
    :param pandas.DataFrame branch: branch data frame.
    :param dict us_states_dat: dictionary of state border lats/lons. If None, get
        from :func:`postreise.plot.plot_states.get_state_borders`.
    :param int/float vmin: minimum value for color range. If None, use data minimum.
    :param int/float vmax: maximum value for color range. If None, use data maximum.
    :param bool is_website: changes text/legend formatting to look better on the website
    :return:  -- map of lines with median utilization color coded
    """
    if us_states_dat is None:
        us_states_dat = get_state_borders()

    branch_mask = branch.rateA != 0
    median_util = utilization_df[branch.loc[branch_mask].index].median()
    branch_utilization = pd.concat(
        [branch.loc[branch_mask], median_util.rename("median_utilization")], axis=1
    )
    lines = branch_utilization.loc[(branch_utilization["branch_device_type"] == "Line")]

    min_val = lines["median_utilization"].min() if vmin is None else vmin
    max_val = lines["median_utilization"].max() if vmax is None else vmax

    mapper1 = linear_cmap(
        field_name="median_utilization",
        palette=traffic_palette,
        low=min_val,
        high=max_val,
    )

    color_bar = ColorBar(
        color_mapper=mapper1["transform"],
        width=385 if is_website else 500,
        height=5,
        location=(0, 0),
        title="median utilization",
        orientation="horizontal",
        padding=5,
    )

    branch_map = project_branch(branch_utilization)
    branch_map = branch_map.sort_values(by=["median_utilization"])
    branch_map = branch_map[~branch_map.isin([np.nan, np.inf, -np.inf]).any(1)]

    # state borders
    a, b = project_borders(us_states_dat)

    multi_line_source = ColumnDataSource(
        {
            "xs": branch_map[["from_x", "to_x"]].values.tolist(),
            "ys": branch_map[["from_y", "to_y"]].values.tolist(),
            "median_utilization": branch_map.median_utilization,
            "cap": branch_map.rateA / 2000 + 0.2,
            "util": branch_map.median_utilization.round(2),
            "capacity": branch_map.rateA.round(),
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
    p.add_layout(color_bar, "center")
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))
    p.patches(a, b, fill_alpha=0.0, line_color="gray", line_width=2)
    lines = p.multi_line(
        "xs", "ys", color=mapper1, line_width="cap", source=multi_line_source
    )
    hover = HoverTool(
        tooltips=[
            ("Capacity MW", "@capacity"),
            ("Utilization", "@util{f0.00}"),
        ],
        renderers=[lines],
    )
    p.add_tools(hover)
    return p
