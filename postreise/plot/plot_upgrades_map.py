import numpy as np
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from postreise.analyze.transmission.upgrades import (
    get_branch_differences,
    get_dcline_differences,
)
from postreise.plot import colors
from postreise.plot.plot_states import plot_states
from postreise.plot.projection_helpers import project_branch


def _map_upgrades(
    branch_merge,
    dc_merge,
    b2b_indices=None,
    diff_threshold=100,
    all_branch_scale=1e-3,
    diff_branch_scale=1e-3,
    all_branch_min=0.1,
    diff_branch_min=1.0,
    b2b_scale=5e-3,
    x_range=None,
    y_range=None,
):
    """Makes map of branches showing upgrades

    :param pandas.DataFrame branch_merge: branch of scenarios 1 and 2
    :param pandas.DataFrame dc_merge: dclines for scenarios 1 and 2
    :param iterable b2b_indices: list/set/tuple of 'DC lines' which are back-to-backs.
    :param int/float diff_threshold: difference threshold (in MW), above which branches
        are highlighted.
    :param int/float all_branch_scale: scale factor for plotting all branches.
    :param int/float diff_branch_scale: scale factor for plotting branches with
        differences above the threshold.
    :param int/float all_branch_min: minimum width to plot all branches.
    :param int/float diff_branch_min: minimum width to plot branches with significant
        differences.
    :param int/float b2b_scale: scale factor for plotting b2b facilities.
    :param tuple(float, float) x_range: x range to zoom plot to (EPSG:3857).
    :param tuple(float, float) y_range: y range to zoom plot to (EPSG:3857).
    :return: (*bokeh.plotting.figure.Figure*) -- Bokeh map plot of color-coded upgrades.
    """
    # plotting constants
    bokeh_tools = "pan,wheel_zoom,reset,save"
    legend_alpha = 0.9
    all_elements_alpha = 0.5
    differences_alpha = 0.8

    # data prep
    branch_all = project_branch(branch_merge)
    branch_dc = project_branch(dc_merge)

    # For these, we will plot a triangle for the B2B location, plus 'pseudo' AC lines
    # get_level_values allows us to index into MultiIndex as necessary
    b2b_indices = {} if b2b_indices is None else b2b_indices
    b2b_mask = branch_dc.index.get_level_values(0).isin(b2b_indices)
    # .copy() avoids a pandas SettingWithCopyError later
    b2b = branch_dc.iloc[b2b_mask].copy()
    branch_dc_lines = branch_dc.loc[~b2b_mask].copy()

    # Color branches based on upgraded capacity
    branch_all["color"] = np.nan
    branch_all.loc[branch_all["diff"] > diff_threshold, "color"] = colors.be_blue
    branch_all.loc[branch_all["diff"] < -1 * diff_threshold, "color"] = colors.be_purple
    # Color pseudo AC branches based on upgraded capacity
    b2b["color"] = np.nan
    b2b.loc[b2b["diff"] > diff_threshold, "color"] = colors.be_blue
    b2b.loc[b2b["diff"] < -1 * diff_threshold, "color"] = colors.be_purple
    b2b = b2b[~b2b.color.isnull()]
    # Color DC lines based on upgraded capacity
    branch_dc_lines.loc[:, "color"] = np.nan
    branch_dc_lines.loc[branch_dc_lines["diff"] > 0, "color"] = colors.be_green
    branch_dc_lines.loc[branch_dc_lines["diff"] < 0, "color"] = colors.be_lightblue

    # Create ColumnDataSources for bokeh to plot with
    source_all_ac = ColumnDataSource(
        {
            "xs": branch_all[["from_x", "to_x"]].values.tolist(),
            "ys": branch_all[["from_y", "to_y"]].values.tolist(),
            "cap": branch_all["rateA"] * all_branch_scale + all_branch_min,
            "color": branch_all["color"],
        }
    )
    # AC branches with significant differences
    ac_diff_branches = branch_all.loc[~branch_all.color.isnull()]
    source_ac_difference = ColumnDataSource(
        {
            "xs": ac_diff_branches[["from_x", "to_x"]].values.tolist(),
            "ys": ac_diff_branches[["from_y", "to_y"]].values.tolist(),
            "diff": (
                ac_diff_branches["diff"].abs() * diff_branch_scale + diff_branch_min
            ),
            "color": ac_diff_branches["color"],
        }
    )
    source_all_dc = ColumnDataSource(
        {
            "xs": branch_dc_lines[["from_x", "to_x"]].values.tolist(),
            "ys": branch_dc_lines[["from_y", "to_y"]].values.tolist(),
            "cap": branch_dc_lines.Pmax * all_branch_scale + all_branch_min,
            "color": branch_dc_lines["color"],
        }
    )
    dc_diff_lines = branch_dc_lines.loc[~branch_dc_lines.color.isnull()]
    source_dc_differences = ColumnDataSource(
        {
            "xs": dc_diff_lines[["from_x", "to_x"]].values.tolist(),
            "ys": dc_diff_lines[["from_y", "to_y"]].values.tolist(),
            "diff": dc_diff_lines["diff"].abs() * diff_branch_scale + diff_branch_min,
            "color": dc_diff_lines["color"],
        }
    )
    source_pseudoac = ColumnDataSource(  # pseudo ac scen 1
        {
            "xs": b2b[["from_x", "to_x"]].values.tolist(),
            "ys": b2b[["from_y", "to_y"]].values.tolist(),
            "cap": b2b.Pmax * all_branch_scale + all_branch_min,
            "diff": b2b["diff"].abs() * diff_branch_scale + diff_branch_min,
            "color": b2b["color"],
        }
    )

    # Set up figure
    p = figure(
        tools=bokeh_tools,
        x_axis_location=None,
        y_axis_location=None,
        plot_width=1400,
        plot_height=800,
        output_backend="webgl",
        match_aspect=True,
        x_range=x_range,
        y_range=y_range,
    )
    p.xgrid.visible = False
    p.ygrid.visible = False

    # Build the legend
    leg_x = [-8.1e6] * 2
    leg_y = [5.2e6] * 2

    # These are 'dummy' series to populate the legend with
    if len(branch_dc_lines[branch_dc_lines["diff"] > 0]) > 0:
        p.multi_line(
            leg_x,
            leg_y,
            color=colors.be_green,
            alpha=legend_alpha,
            line_width=10,
            legend_label="Additional HVDC Capacity",
        )
    if len(branch_dc_lines[branch_dc_lines["diff"] < 0]) > 0:
        p.multi_line(
            leg_x,
            leg_y,
            color=colors.be_lightblue,
            alpha=legend_alpha,
            line_width=10,
            legend_label="Reduced HVDC Capacity",
        )
    if len(branch_all[branch_all["diff"] < 0]) > 0:
        p.multi_line(
            leg_x,
            leg_y,
            color=colors.be_purple,
            alpha=legend_alpha,
            line_width=10,
            legend_label="Reduced AC Transmission",
        )
    if len(branch_all[branch_all["diff"] > 0]) > 0:
        p.multi_line(
            leg_x,
            leg_y,
            color=colors.be_blue,
            alpha=legend_alpha,
            line_width=10,
            legend_label="Upgraded AC transmission",
        )
    if len(b2b[b2b["diff"] > 0]) > 0:
        p.scatter(
            x=b2b.from_x[1],
            y=b2b.from_y[1],
            color=colors.be_magenta,
            marker="triangle",
            legend_label="Upgraded B2B capacity",
            size=30,
            alpha=legend_alpha,
        )
    p.legend.location = "bottom_left"
    p.legend.label_text_font_size = "20pt"

    # Everything below gets plotted into the 'main' figure
    # state outlines
    plot_states(
        bokeh_figure=p,
        colors="white",
        line_color="slategrey",
        line_width=1,
        fill_alpha=1,
        background_map=False,
    )

    background_plot_dicts = [
        {"source": source_all_ac, "color": "gray", "line_width": "cap"},
        {"source": source_all_dc, "color": "gray", "line_width": "cap"},
        {"source": source_pseudoac, "color": "gray", "line_width": "cap"},
    ]
    for d in background_plot_dicts:
        p.multi_line(
            "xs",
            "ys",
            color=d["color"],
            line_width=d["line_width"],
            source=d["source"],
            alpha=all_elements_alpha,
        )

    # all B2Bs
    p.scatter(
        x=b2b.from_x,
        y=b2b.from_y,
        color="gray",
        marker="triangle",
        size=b2b["Pmax"].abs() * b2b_scale,
        alpha=all_elements_alpha,
    )

    difference_plot_dicts = [
        {"source": source_pseudoac, "color": "color", "line_width": "diff"},
        {"source": source_ac_difference, "color": "color", "line_width": "diff"},
        {"source": source_dc_differences, "color": "color", "line_width": "diff"},
    ]

    for d in difference_plot_dicts:
        p.multi_line(
            "xs",
            "ys",
            color=d["color"],
            line_width=d["line_width"],
            source=d["source"],
            alpha=differences_alpha,
        )

    # B2Bs with differences
    p.scatter(
        x=b2b.from_x,
        y=b2b.from_y,
        color=colors.be_magenta,
        marker="triangle",
        size=b2b["diff"].abs() * b2b_scale,
    )

    return p


def map_upgrades(scenario1, scenario2, b2b_indices=None, **plot_kwargs):
    """Plot capacity differences for branches & DC lines between two scenarios.

    :param powersimdata.scenario.scenario.Scenario scenario1: first scenario.
    :param powersimdata.scenario.scenario.Scenario scenario2: second scenario.
    :param iterable b2b_indices: list/set/tuple of 'DC lines' which are back-to-backs.
    :param \\*\\*plot_kwargs: collected keyword arguments to be passed to _map_upgrades.
    :return: (*bokeh.plotting.figure.Figure*) -- Bokeh map plot of color-coded upgrades.
    """
    if not (
        scenario1.info["grid_model"] == scenario2.info["grid_model"]
        and scenario1.info["interconnect"] == scenario2.info["interconnect"]
    ):
        raise ValueError("Scenarios to compare must be same grid_model & interconnect")
    grid1 = scenario1.state.get_grid()
    grid2 = scenario2.state.get_grid()
    branch_merge = get_branch_differences(grid1.branch, grid2.branch)
    dc_merge = get_dcline_differences(grid1.dcline, grid2.dcline, grid1.bus)
    map_plot = _map_upgrades(branch_merge, dc_merge, b2b_indices, **plot_kwargs)
    return map_plot
