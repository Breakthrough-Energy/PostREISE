import numpy as np
from bokeh.models import ColumnDataSource
from powersimdata.design.compare.transmission import (
    calculate_branch_difference,
    calculate_dcline_difference,
)
from powersimdata.utility.distance import haversine

from postreise.plot import colors
from postreise.plot.canvas import create_map_canvas
from postreise.plot.check import _check_func_kwargs
from postreise.plot.plot_states import add_state_borders
from postreise.plot.projection_helpers import project_branch


def add_transmission_upgrades(
    canvas,
    branch_merge,
    dc_merge,
    b2b_indices=None,
    diff_threshold=100,
    all_branch_scale=1,
    diff_branch_scale=1,
    all_branch_min=0.1,
    diff_branch_min=1.0,
    b2b_scale=5,
    dcline_upgrade_dist_threshold=0,
):
    """Make map of branches showing upgrades.

    :param bokeh.plotting.figure.Figure canvas: canvas to add upgrades to.
    :param pandas.DataFrame branch_merge: branch of scenarios 1 and 2
    :param pandas.DataFrame dc_merge: dclines for scenarios 1 and 2
    :param list/set/tuple b2b_indices: indices of HVDC lines which are back-to-backs.
    :param int/float diff_threshold: difference threshold (in MW), above which branches
        are highlighted.
    :param int/float all_branch_scale: scale factor for plotting all branches
        (pixels/GW).
    :param int/float diff_branch_scale: scale factor for plotting branches with
        differences above the threshold (pixels/GW).
    :param int/float all_branch_min: minimum width to plot all branches.
    :param int/float diff_branch_min: minimum width to plot branches with significant
        differences.
    :param int/float b2b_scale: scale factor for plotting b2b facilities (pixels/GW).
    :param int/float dcline_upgrade_dist_threshold: minimum distance (miles) for
        plotting DC line upgrades (if none are longer, no legend entry will be created).
    :return: (*bokeh.plotting.figure.Figure*) -- Bokeh map plot of color-coded upgrades.
    """
    # plotting constants
    legend_alpha = 0.9
    all_elements_alpha = 0.5
    differences_alpha = 0.8
    # convert scale factors from pixels/GW to pixels/MW (base units for our grid data)
    all_branch_scale_MW = all_branch_scale / 1000  # noqa: N806
    diff_branch_scale_MW = diff_branch_scale / 1000  # noqa: N806
    b2b_scale_MW = b2b_scale / 1000  # noqa: N806

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
    branch_dc_lines["dist"] = branch_dc_lines.apply(
        lambda x: haversine((x.from_lat, x.from_lon), (x.to_lat, x.to_lon)), axis=1
    )
    branch_dc_lines = branch_dc_lines.loc[
        branch_dc_lines.dist >= dcline_upgrade_dist_threshold
    ]
    branch_dc_lines.loc[:, "color"] = np.nan
    branch_dc_lines.loc[branch_dc_lines["diff"] > 0, "color"] = colors.be_green
    branch_dc_lines.loc[branch_dc_lines["diff"] < 0, "color"] = colors.be_lightblue

    # Create ColumnDataSources for bokeh to plot with
    source_all_ac = ColumnDataSource(
        {
            "xs": branch_all[["from_x", "to_x"]].values.tolist(),
            "ys": branch_all[["from_y", "to_y"]].values.tolist(),
            "cap": branch_all["rateA"] * all_branch_scale_MW + all_branch_min,
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
                ac_diff_branches["diff"].abs() * diff_branch_scale_MW + diff_branch_min
            ),
            "color": ac_diff_branches["color"],
        }
    )
    source_all_dc = ColumnDataSource(
        {
            "xs": branch_dc_lines[["from_x", "to_x"]].values.tolist(),
            "ys": branch_dc_lines[["from_y", "to_y"]].values.tolist(),
            "cap": branch_dc_lines.Pmax * all_branch_scale_MW + all_branch_min,
            "color": branch_dc_lines["color"],
        }
    )
    dc_diff_lines = branch_dc_lines.loc[~branch_dc_lines.color.isnull()]
    source_dc_differences = ColumnDataSource(
        {
            "xs": dc_diff_lines[["from_x", "to_x"]].values.tolist(),
            "ys": dc_diff_lines[["from_y", "to_y"]].values.tolist(),
            "diff": (
                dc_diff_lines["diff"].abs() * diff_branch_scale_MW + diff_branch_min
            ),
            "color": dc_diff_lines["color"],
        }
    )
    source_pseudoac = ColumnDataSource(  # pseudo ac scen 1
        {
            "xs": b2b[["from_x", "to_x"]].values.tolist(),
            "ys": b2b[["from_y", "to_y"]].values.tolist(),
            "cap": b2b.Pmax * all_branch_scale_MW + all_branch_min,
            "diff": b2b["diff"].abs() * diff_branch_scale_MW + diff_branch_min,
            "color": b2b["color"],
        }
    )

    # Build the legend
    leg_x = [-8.1e6] * 2
    leg_y = [5.2e6] * 2

    # These are 'dummy' series to populate the legend with
    if len(branch_dc_lines[branch_dc_lines["diff"] > 0]) > 0:
        canvas.multi_line(
            leg_x,
            leg_y,
            color=colors.be_green,
            alpha=legend_alpha,
            line_width=10,
            legend_label="Additional HVDC Capacity",
        )
    if len(branch_dc_lines[branch_dc_lines["diff"] < 0]) > 0:
        canvas.multi_line(
            leg_x,
            leg_y,
            color=colors.be_lightblue,
            alpha=legend_alpha,
            line_width=10,
            legend_label="Reduced HVDC Capacity",
        )
    if len(branch_all[branch_all["diff"] < 0]) > 0:
        canvas.multi_line(
            leg_x,
            leg_y,
            color=colors.be_purple,
            alpha=legend_alpha,
            line_width=10,
            legend_label="Reduced AC Transmission",
        )
    if len(branch_all[branch_all["diff"] > 0]) > 0:
        canvas.multi_line(
            leg_x,
            leg_y,
            color=colors.be_blue,
            alpha=legend_alpha,
            line_width=10,
            legend_label="Upgraded AC transmission",
        )
    if len(b2b[b2b["diff"] > 0]) > 0:
        canvas.scatter(
            x=b2b.from_x[1],
            y=b2b.from_y[1],
            color=colors.be_magenta,
            marker="triangle",
            legend_label="Upgraded B2B capacity",
            size=30,
            alpha=legend_alpha,
        )

    # Everything below gets plotted into the 'main' figure
    background_plot_dicts = [
        {"source": source_all_ac, "color": "gray", "line_width": "cap"},
        {"source": source_all_dc, "color": "gray", "line_width": "cap"},
        {"source": source_pseudoac, "color": "gray", "line_width": "cap"},
    ]
    for d in background_plot_dicts:
        canvas.multi_line(
            "xs",
            "ys",
            color=d["color"],
            line_width=d["line_width"],
            source=d["source"],
            alpha=all_elements_alpha,
        )

    # all B2Bs
    canvas.scatter(
        x=b2b.from_x,
        y=b2b.from_y,
        color="gray",
        marker="triangle",
        size=b2b["Pmax"].abs() * b2b_scale_MW,
        alpha=all_elements_alpha,
    )

    difference_plot_dicts = [
        {"source": source_pseudoac, "color": "color", "line_width": "diff"},
        {"source": source_ac_difference, "color": "color", "line_width": "diff"},
        {"source": source_dc_differences, "color": "color", "line_width": "diff"},
    ]

    for d in difference_plot_dicts:
        canvas.multi_line(
            "xs",
            "ys",
            color=d["color"],
            line_width=d["line_width"],
            source=d["source"],
            alpha=differences_alpha,
        )

    # B2Bs with differences
    canvas.scatter(
        x=b2b.from_x,
        y=b2b.from_y,
        color=colors.be_magenta,
        marker="triangle",
        size=b2b["diff"].abs() * b2b_scale_MW,
    )

    return canvas


def map_transmission_upgrades(
    scenario1,
    scenario2,
    b2b_indices=None,
    figsize=(1400, 800),
    x_range=None,
    y_range=None,
    state_borders_kwargs=None,
    legend_font_size=20,
    legend_location="bottom_left",
    **plot_kwargs,
):
    """Plot capacity differences for branches & HVDC lines between two scenarios.

    :param powersimdata.scenario.scenario.Scenario scenario1: first scenario.
    :param powersimdata.scenario.scenario.Scenario scenario2: second scenario.
    :param list/set/tuple b2b_indices: indices of HVDC lines which are back-to-backs.
    :param tuple figsize: size of the bokeh figure (in pixels).
    :param tuple x_range: x range to zoom plot to (EPSG:3857).
    :param tuple y_range: y range to zoom plot to (EPSG:3857).
    :param dict state_borders_kwargs: keyword arguments to be passed to
        :func:`postreise.plot.plot_states.add_state_borders`.
    :param int/float legend_font_size: font size for legend.
    :param str legend_location: location for legend.
    :param \\*\\*plot_kwargs: collected keyword arguments to be passed to
        :func:`add_transmission_upgrades`.
    :raises ValueError: if grid model and interconnect of scenarios differ.
    :return: (*bokeh.plotting.figure.Figure*) -- map with color-coded upgrades.
    """
    # Validate inputs
    if not (
        scenario1.info["grid_model"] == scenario2.info["grid_model"]
        and scenario1.info["interconnect"] == scenario2.info["interconnect"]
    ):
        raise ValueError("Scenarios to compare must be same grid model & interconnect")

    # Pre-plot data processing
    grid1 = scenario1.state.get_grid()
    grid2 = scenario2.state.get_grid()
    branch_merge = calculate_branch_difference(grid1.branch, grid2.branch)
    dc_merge = calculate_dcline_difference(grid1, grid2)

    # Set up figure
    canvas = create_map_canvas(figsize=figsize, x_range=x_range, y_range=y_range)

    # Add state outlines
    default_state_borders_kwargs = {
        "line_color": "slategrey",
        "line_width": 1,
        "fill_alpha": 1,
        "background_map": False,
    }
    all_state_borders_kwargs = (
        {**default_state_borders_kwargs, **state_borders_kwargs}
        if state_borders_kwargs is not None
        else default_state_borders_kwargs
    )
    _check_func_kwargs(
        add_state_borders, set(all_state_borders_kwargs), "state_borders_kwargs"
    )
    canvas = add_state_borders(canvas, **all_state_borders_kwargs)

    # add transmission map
    canvas = add_transmission_upgrades(
        canvas, branch_merge, dc_merge, b2b_indices, **plot_kwargs
    )

    canvas.legend.location = legend_location
    canvas.legend.label_text_font_size = f"{legend_font_size}pt"

    return canvas
