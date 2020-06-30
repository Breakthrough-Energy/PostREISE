import pandas as pd
from bokeh.models import ColumnDataSource, ColorBar
from bokeh.plotting import figure
from bokeh.sampledata import us_states
from bokeh.tile_providers import get_provider, Vendors
from bokeh.transform import linear_cmap
import numpy as np

from postreise.plot import plot_carbon_map
from postreise.plot.projection_helpers import project_branch

traffic_palette = [
    "darkgreen",
    "green",
    "limegreen",
    "lawngreen",
    "yellowgreen",
    "yellow",
    "gold",
    "goldenrod",
    "orange",
    "orangered",
    "red",
    "darkred",
]


def map_risk_bind(risk_or_bind, congestion_stats, branch, us_states_dat=us_states.data):
    """Makes map showing risk or binding incidents on US states map.

    :param str risk_or_bind: specify plotting "risk" or "bind"
    :param pandas.DataFrame congestion_stats: data frame as returned by
        :func:`postreise.analyze.transmission.generate_cong_stats`.
    :param pandas.DataFrame branch: branch data frame.
    :param dict us_states_dat: us_states data file, imported from bokeh.
    :return:  -- map of lines with risk and bind incidents color coded
    """
    # projection steps for mapping
    branch_congestion = pd.concat(
        [branch.loc[congestion_stats.index], congestion_stats], axis=1
    )
    branch_map_all = project_branch(branch)
    multi_line_source_all = ColumnDataSource(
        {
            "xs": branch_map_all[["from_x", "to_x"]].values.tolist(),
            "ys": branch_map_all[["from_y", "to_y"]].values.tolist(),
            "cap": branch_map_all["rateA"] / 1000 + 1,
        }
    )
    a, b = plot_carbon_map.get_borders(us_states_dat.copy())
    tools: str = "pan,wheel_zoom,reset,hover,save"

    branch_congestion1 = branch_congestion[branch_congestion[risk_or_bind] > 0]
    branch_congestion1.sort_values(by=[risk_or_bind])
    branch_map = project_branch(branch_congestion1)
    min_val = branch_congestion1[risk_or_bind].min()
    max_val = branch_congestion1[risk_or_bind].max()
    mapper1 = linear_cmap(
        field_name=risk_or_bind, palette=traffic_palette, low=min_val, high=max_val
    )
    color_bar = ColorBar(
        color_mapper=mapper1["transform"], width=8, location=(0, 0), title=risk_or_bind
    )
    multi_line_source = ColumnDataSource(
        {
            "xs": branch_map[["from_x", "to_x"]].values.tolist(),
            "ys": branch_map[["from_y", "to_y"]].values.tolist(),
            risk_or_bind: branch_map[risk_or_bind],
            "cap": branch_map["capacity"] / 1000 + 2,
        }
    )

    # Set up figure
    p = figure(
        title=risk_or_bind,
        tools=tools,
        x_axis_location=None,
        y_axis_location=None,
        plot_width=800,
        plot_height=800,
    )
    p.add_layout(color_bar, "right")
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))
    p.patches(a, b, fill_alpha=0.0, line_color="black", line_width=2)
    p.multi_line(
        "xs",
        "ys",
        color="gray",
        line_width="cap",
        source=multi_line_source_all,
        alpha=0.5,
    )
    p.multi_line("xs", "ys", color=mapper1, line_width="cap", source=multi_line_source)
    return p


def map_utilization(utilization_df, branch, us_states_dat=us_states.data):
    """Makes map showing utilization. Utilization input can either be medians
    only, or can be normalized utilization dataframe

    :param us_states_dat: us_states data file, imported from bokeh.
    :param pandas.DataFrame utilization_df: utilization returned by
        :func:`postreise.analyze.transmission.utilization.get_utilization`
    :param pandas.DataFrame branch: branch data frame.
    :return:  -- map of lines with median utilization color coded
    """

    branch_utilization = pd.concat(
        [
            branch.loc[branch.rateA != 0],
            utilization_df[branch.loc[branch.rateA != 0].index]
            .median()
            .rename("median_utilization"),
        ],
        axis=1,
    )
    lines = branch_utilization.loc[(branch_utilization["branch_device_type"] == "Line")]

    min_val = lines["median_utilization"].min()
    max_val = lines["median_utilization"].max()

    mapper1 = linear_cmap(
        field_name="median_utilization",
        palette=traffic_palette,
        low=min_val,
        high=max_val,
    )

    color_bar = ColorBar(
        color_mapper=mapper1["transform"],
        width=8,
        location=(0, 0),
        title="median utilization",
    )

    branch_map = project_branch(branch_utilization)
    branch_map = branch_map.sort_values(by=["median_utilization"])
    branch_map = branch_map[~branch_map.isin([np.nan, np.inf, -np.inf]).any(1)]

    # state borders
    a, b = plot_carbon_map.get_borders(us_states_dat.copy())

    multi_line_source = ColumnDataSource(
        {
            "xs": branch_map[["from_x", "to_x"]].values.tolist(),
            "ys": branch_map[["from_y", "to_y"]].values.tolist(),
            "median_utilization": branch_map.median_utilization,
            "cap": branch_map.rateA / 1000 + 2,
        }
    )

    # Set up figure
    tools: str = "pan,wheel_zoom,reset,hover,save"

    p = figure(
        title="Utilization",
        tools=tools,
        x_axis_location=None,
        y_axis_location=None,
        plot_width=800,
        plot_height=800,
        output_backend="webgl",
    )
    p.add_layout(color_bar, "right")
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))
    p.patches(a, b, fill_alpha=0.0, line_color="black", line_width=2)
    p.multi_line("xs", "ys", color=mapper1, line_width="cap", source=multi_line_source)
    return p
