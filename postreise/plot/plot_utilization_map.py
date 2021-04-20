# This plotting module has a corresponding demo notebook in
#   PostREISE/postreise/plot/demo: utilization_map_demo.ipynb

import numpy as np
import pandas as pd
from bokeh.models import ColorBar, ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.transform import linear_cmap

from postreise.plot.colors import traffic_palette
from postreise.plot.plot_states import plot_states
from postreise.plot.projection_helpers import project_branch


def map_risk_bind(
    risk_or_bind,
    congestion_stats,
    branch,
    us_states_dat=None,
    vmin=None,
    vmax=None,
    is_website=False,
    palette=None,
    all_branch_scale_factor=5e-4,
    all_branch_min_width=0.2,
    select_branch_scale_factor=1e-3,
    select_branch_min_width=2,
    figsize=(1400, 800),
    show_color_bar=True,
    plot_states_kwargs=None,
):
    """Makes map showing risk or binding incidents on US states map.

    :param str risk_or_bind: specify plotting "risk" or "bind"
    :param pandas.DataFrame congestion_stats: data frame as returned by
        :func:`postreise.analyze.transmission.utilization.generate_cong_stats`.
    :param pandas.DataFrame branch: branch data frame.
    :param int/float vmin: minimum value for color range. If None, use data minimum.
    :param int/float vmax: maximum value for color range. If None, use data maximum.
    :param bool is_website: changes text/legend formatting to look better on the website
    :param iterable palette: sequence of colors used for color range, passed as
        `palette` kwarg to :func:`bokeh.transform.linear_cmap`.
        If None, default to `postreise.plot.colors.traffic_palette`.
    :param int/float all_branch_scale_factor: scale factor for unhighlighted branches.
    :param int/float all_branch_min_width: minimum width for unhighlighted branches.
    :param int/float select_branch_scale_factor: scale factor for highlighted branches.
    :param int/float select_branch_min_width: minimum width for highlighted branches.
    :param tuple(int, int) figsize: size of the bokeh figure (in pixels).
    :param bool show_color_bar: whether to render the color bar on the figure.
    :param dict plot_states_kwargs: keyword arguments to be passed to
        :func:`postreise.plot.plot_states.plot_states`.
    :return: (*bokeh.plotting.figure*) -- map of lines with risk and bind incidents
        color coded.
    """
    if risk_or_bind == "risk":
        risk_or_bind_units = "Risk (MWH)"

    if risk_or_bind == "bind":
        risk_or_bind_units = "Binding incidents"

    if palette is None:
        palette = list(traffic_palette)

    # projection steps for mapping
    branch_congestion = pd.concat(
        [branch.loc[congestion_stats.index], congestion_stats], axis=1
    )
    branch_map_all = project_branch(branch)

    branch_congestion = branch_congestion[branch_congestion[risk_or_bind] > 0]
    branch_congestion.sort_values(by=[risk_or_bind])
    branch_map = project_branch(branch_congestion)
    min_val = branch_congestion[risk_or_bind].min() if vmin is None else vmin
    max_val = branch_congestion[risk_or_bind].max() if vmax is None else vmax
    mapper = linear_cmap(
        field_name=risk_or_bind, palette=palette, low=min_val, high=max_val
    )
    multi_line_source = ColumnDataSource(
        {
            "xs": branch_map[["from_x", "to_x"]].values.tolist(),
            "ys": branch_map[["from_y", "to_y"]].values.tolist(),
            risk_or_bind: branch_map[risk_or_bind],
            "value": branch_map[risk_or_bind].round(),
            "cap": (
                branch_map["capacity"] * select_branch_scale_factor
                + select_branch_min_width
            ),
            "capacity": branch_map.rateA.round(),
        }
    )

    # Set up figure
    p = figure(
        tools="pan,wheel_zoom,reset,save",
        x_axis_location=None,
        y_axis_location=None,
        plot_width=figsize[0],
        plot_height=figsize[1],
        output_backend="webgl",
        match_aspect=True,
    )
    if show_color_bar:
        color_bar = ColorBar(
            color_mapper=mapper["transform"],
            width=385 if is_website else 500,
            height=5,
            location=(0, 0),
            title=risk_or_bind_units,
            orientation="horizontal",
            padding=5,
        )
        p.add_layout(color_bar, "center")
    default_plot_states_kwargs = {"fill_alpha": 0.0, "background_map": True}
    if plot_states_kwargs is not None:
        all_plot_states_kwargs = default_plot_states_kwargs.update(**plot_states_kwargs)
    else:
        all_plot_states_kwargs = default_plot_states_kwargs
    plot_states(bokeh_figure=p, **all_plot_states_kwargs)
    p.multi_line(
        branch_map_all[["from_x", "to_x"]].to_numpy().tolist(),
        branch_map_all[["from_y", "to_y"]].to_numpy().tolist(),
        color="gray",
        line_width=(
            branch_map_all["rateA"] * all_branch_scale_factor + all_branch_min_width
        ),
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
    utilization_df,
    branch,
    vmin=None,
    vmax=None,
    is_website=False,
    palette=None,
    branch_scale_factor=5e-4,
    branch_min_width=0.2,
    figsize=(1400, 800),
    plot_states_kwargs=None,
):
    """Makes map showing utilization. Utilization input can either be medians
    only, or can be normalized utilization dataframe

    :param pandas.DataFrame utilization_df: utilization returned by
        :func:`postreise.analyze.transmission.utilization.get_utilization`
    :param pandas.DataFrame branch: branch data frame.
    :param int/float vmin: minimum value for color range. If None, use data minimum.
    :param int/float vmax: maximum value for color range. If None, use data maximum.
    :param bool is_website: changes text/legend formatting to look better on the website
    :param iterable palette: sequence of colors used for color range, passed as
        `palette` kwarg to :func:`bokeh.transform.linear_cmap`.
        If None, default to `postreise.plot.colors.traffic_palette`.
    :param int/float branch_scale_factor: scale factor for branches.
    :param int/float branch_min_width: minimum width for branches.
    :param tuple(int, int) figsize: size of the bokeh figure (in pixels).
    :param dict plot_states_kwargs: keyword arguments to be passed to
        :func:`postreise.plot.plot_states.plot_states`.
    :return: (*bokeh.plotting.figure*) -- map of lines with median utilization color
        coded.
    """
    if palette is None:
        palette = list(traffic_palette)

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
        palette=palette,
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

    multi_line_source = ColumnDataSource(
        {
            "xs": branch_map[["from_x", "to_x"]].values.tolist(),
            "ys": branch_map[["from_y", "to_y"]].values.tolist(),
            "median_utilization": branch_map.median_utilization,
            "width": branch_map.rateA * branch_scale_factor + branch_min_width,
            "util": branch_map.median_utilization.round(2),
            "capacity": branch_map.rateA.round(),
        }
    )

    p = figure(
        tools="pan,wheel_zoom,reset,save",
        x_axis_location=None,
        y_axis_location=None,
        plot_width=figsize[0],
        plot_height=figsize[1],
        output_backend="webgl",
        match_aspect=True,
    )
    p.add_layout(color_bar, "center")
    default_plot_states_kwargs = {"fill_alpha": 0.0, "line_width": 2}
    if plot_states_kwargs is not None:
        all_plot_states_kwargs = default_plot_states_kwargs.update(**plot_states_kwargs)
    else:
        all_plot_states_kwargs = default_plot_states_kwargs
    plot_states(bokeh_figure=p, **all_plot_states_kwargs)
    lines = p.multi_line(
        "xs", "ys", color=mapper1, line_width="width", source=multi_line_source
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
