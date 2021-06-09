# This plotting module has a corresponding demo notebook in
#   PostREISE/postreise/plot/demo: utilization_map_demo.ipynb

import numpy as np
import pandas as pd
from bokeh.models import ColorBar, ColumnDataSource, HoverTool
from bokeh.transform import linear_cmap

from postreise.analyze.transmission.utilization import (
    generate_cong_stats,
    get_utilization,
)
from postreise.plot.canvas import create_map_canvas
from postreise.plot.check import _check_func_kwargs
from postreise.plot.colors import traffic_palette
from postreise.plot.plot_states import add_state_borders
from postreise.plot.projection_helpers import project_branch


def map_risk_bind(
    risk_or_bind,
    scenario=None,
    congestion_stats=None,
    branch=None,
    us_states_dat=None,
    vmin=None,
    vmax=None,
    color_bar_width=500,
    palette=None,
    all_branch_scale_factor=0.5,
    all_branch_min_width=0.2,
    select_branch_scale_factor=1,
    select_branch_min_width=2,
    figsize=(1400, 800),
    show_color_bar=True,
    state_borders_kwargs=None,
):
    """Make map showing risk or binding incidents on US states map.
    Either ``scenario`` XOR (``congestion_stats`` AND ``branch``) must be specified.

    :param str risk_or_bind: specify plotting "risk" or "bind".
    :param powersimdata.scenario.scenario.Scenario scenario: scenario to analyze.
    :param pandas.DataFrame congestion_stats: data frame as returned by
        :func:`postreise.analyze.transmission.utilization.generate_cong_stats`.
    :param pandas.DataFrame branch: branch data frame.
    :param int/float vmin: minimum value for color range. If None, use data minimum.
    :param int/float vmax: maximum value for color range. If None, use data maximum.
    :param int color_bar_width: width of color bar (pixels).
    :param iterable palette: sequence of colors used for color range, passed as
        `palette` kwarg to :func:`bokeh.transform.linear_cmap`.
        If None, default to `postreise.plot.colors.traffic_palette`.
    :param int/float all_branch_scale_factor: scale factor for unhighlighted branches
        (pixels/GW).
    :param int/float all_branch_min_width: minimum width for unhighlighted branches
        (pixels).
    :param int/float select_branch_scale_factor: scale factor for highlighted branches
        (pixels/GW).
    :param int/float select_branch_min_width: minimum width for highlighted branches
        (pixels).
    :param tuple(int, int) figsize: size of the bokeh figure (in pixels).
    :param bool show_color_bar: whether to render the color bar on the figure.
    :param dict state_borders_kwargs: keyword arguments to be passed to
        :func:`postreise.plot.plot_states.add_state_borders`.
    :raises ValueError: if (``scenario`` XOR (``congestion_stats`` AND ``branch``)) are
        not properly specified.
    :return: (*bokeh.plotting.figure*) -- map of lines with risk and bind incidents
        color coded.
    """
    unit_labels = {"risk": "Risk (MWH)", "bind": "Binding incidents"}
    if risk_or_bind not in unit_labels:
        raise ValueError("risk_or_bind must be either 'risk' or 'bind'")
    risk_or_bind_units = unit_labels[risk_or_bind]

    # Check that we've appropriately specified:
    #    `scenario` XOR (`congestion_stats` AND `branch`)
    if scenario is not None:
        branch = scenario.state.get_grid().branch
        congestion_stats = generate_cong_stats(scenario.state.get_pf(), branch)
    elif congestion_stats is not None and branch is not None:
        pass
    else:
        raise ValueError(
            "Either scenario XOR (congestion_stats AND branch) must be specified"
        )

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
                branch_map["capacity"] * select_branch_scale_factor / 1000
                + select_branch_min_width
            ),
            "capacity": branch_map.rateA.round(),
        }
    )

    # Create canvas
    canvas = create_map_canvas(figsize=figsize)

    # Add state borders
    default_state_borders_kwargs = {"fill_alpha": 0.0, "background_map": True}
    all_state_borders_kwargs = (
        {**default_state_borders_kwargs, **state_borders_kwargs}
        if state_borders_kwargs is not None
        else default_state_borders_kwargs
    )
    _check_func_kwargs(
        add_state_borders, set(all_state_borders_kwargs), "state_borders_kwargs"
    )
    canvas = add_state_borders(canvas, **all_state_borders_kwargs)

    # Add color bar
    if show_color_bar:
        color_bar = ColorBar(
            color_mapper=mapper["transform"],
            width=color_bar_width,
            height=5,
            location=(0, 0),
            title=risk_or_bind_units,
            orientation="horizontal",
            padding=5,
        )
        canvas.add_layout(color_bar, "center")

    canvas.multi_line(
        branch_map_all[["from_x", "to_x"]].to_numpy().tolist(),
        branch_map_all[["from_y", "to_y"]].to_numpy().tolist(),
        color="gray",
        line_width=(
            branch_map_all["rateA"] * all_branch_scale_factor / 1000
            + all_branch_min_width
        ),
        alpha=0.5,
    )
    lines = canvas.multi_line(
        "xs", "ys", color=mapper, line_width="cap", source=multi_line_source
    )
    hover = HoverTool(
        tooltips=[
            ("Capacity MW", "@capacity"),
            (risk_or_bind_units, "@value"),
        ],
        renderers=[lines],
    )
    canvas.add_tools(hover)
    return canvas


def map_utilization(
    scenario=None,
    utilization_df=None,
    branch=None,
    vmin=None,
    vmax=None,
    color_bar_width=500,
    palette=None,
    branch_scale_factor=0.5,
    branch_min_width=0.2,
    figsize=(1400, 800),
    show_color_bar=True,
    state_borders_kwargs=None,
):
    """Make map showing utilization. Utilization input can either be medians
    only, or can be normalized utilization dataframe.
    Either ``scenario`` XOR (``utilization_df`` AND ``branch``) must be specified.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario to analyze.
    :param pandas.DataFrame utilization_df: utilization returned by
        :func:`postreise.analyze.transmission.utilization.get_utilization`
    :param pandas.DataFrame branch: branch data frame.
    :param int/float vmin: minimum value for color range. If None, use data minimum.
    :param int/float vmax: maximum value for color range. If None, use data maximum.
    :param int color_bar_width: width of color bar (pixels).
    :param iterable palette: sequence of colors used for color range, passed as
        `palette` kwarg to :func:`bokeh.transform.linear_cmap`.
        If None, default to `postreise.plot.colors.traffic_palette`.
    :param int/float branch_scale_factor: scale factor for branches (pixels/GW).
    :param int/float branch_min_width: minimum width for branches (pixels).
    :param tuple(int, int) figsize: size of the bokeh figure (in pixels).
    :param dict state_borders_kwargs: keyword arguments to be passed to
        :func:`postreise.plot.plot_states.add_state_borders`.
    :raises ValueError: if (``scenario`` XOR (``utilization_df`` AND ``branch``)) are
        not properly specified.
    :return: (*bokeh.plotting.figure*) -- map of lines with median utilization color
        coded.
    """
    # Check that we've appropriately specified:
    #    `scenario` XOR (`utilization_df` AND `branch`)
    if scenario is not None:
        branch = scenario.state.get_grid().branch
        utilization_df = get_utilization(branch, scenario.state.get_pf(), median=True)
    elif utilization_df is not None and branch is not None:
        pass
    else:
        raise ValueError(
            "Either scenario XOR (utilization_df AND branch) must be specified"
        )

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

    mapper = linear_cmap(
        field_name="median_utilization",
        palette=palette,
        low=min_val,
        high=max_val,
    )

    branch_map = project_branch(branch_utilization)
    branch_map = branch_map.sort_values(by=["median_utilization"])
    branch_map = branch_map[~branch_map.isin([np.nan, np.inf, -np.inf]).any(1)]

    multi_line_source = ColumnDataSource(
        {
            "xs": branch_map[["from_x", "to_x"]].values.tolist(),
            "ys": branch_map[["from_y", "to_y"]].values.tolist(),
            "median_utilization": branch_map.median_utilization,
            "width": branch_map.rateA * branch_scale_factor / 1000 + branch_min_width,
            "util": branch_map.median_utilization.round(2),
            "capacity": branch_map.rateA.round(),
        }
    )

    # Create canvas
    canvas = create_map_canvas(figsize=figsize)

    # Add state borders
    default_state_borders_kwargs = {"fill_alpha": 0.0, "line_width": 2}
    all_state_borders_kwargs = (
        {**default_state_borders_kwargs, **state_borders_kwargs}
        if state_borders_kwargs is not None
        else default_state_borders_kwargs
    )
    _check_func_kwargs(
        add_state_borders, set(all_state_borders_kwargs), "state_borders_kwargs"
    )
    canvas = add_state_borders(canvas, **all_state_borders_kwargs)

    # Add color bar
    if show_color_bar:
        color_bar = ColorBar(
            color_mapper=mapper["transform"],
            width=color_bar_width,
            height=5,
            location=(0, 0),
            title="median utilization",
            orientation="horizontal",
            padding=5,
        )
        canvas.add_layout(color_bar, "center")

    lines = canvas.multi_line(
        "xs", "ys", color=mapper, line_width="width", source=multi_line_source
    )
    hover = HoverTool(
        tooltips=[
            ("Capacity MW", "@capacity"),
            ("Utilization", "@util{f0.00}"),
        ],
        renderers=[lines],
    )
    canvas.add_tools(hover)
    return canvas
