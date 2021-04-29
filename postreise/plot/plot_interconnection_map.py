import pandas as pd
from bokeh.plotting import figure
from powersimdata.network.model import ModelImmutables
from powersimdata.utility import distance

from postreise.analyze.check import _check_grid
from postreise.plot.plot_states import plot_states
from postreise.plot.projection_helpers import project_branch


def count_nodes_per_state(grid):
    """Count nodes per state to add as hover-over info in :func`map_interconnections`

    :param powersimdata.input.grid.Grid grid: grid object.
    :return: (*pandas.Series*) -- index: state names, values: number of nodes.
    """
    id2state = ModelImmutables(grid.get_grid_model()).zones["id2abv"]
    grid.bus["state"] = grid.bus["zone_id"].map(id2state)
    counts = pd.Series(grid.bus["state"].value_counts())

    return counts


def map_interconnections(
    grid,
    branch_distance_cutoff=5,
    figsize=(1400, 800),
    branch_width_scale_factor=0.5,
    hvdc_width_scale_factor=1,
    b2b_size_scale_factor=50,
    background_map=False,
):
    """Map transmission lines color coded by interconnection.

    :param powersimdata.input.grid.Grid grid: grid object.
    :param int/float branch_distance_cutoff: distance cutoff for branch display.
    :param tuple figsize: size of the bokeh figure (in pixels).
    :param int/float branch_width_scale_factor: scale factor for branch capacities.
    :param int/float hvdc_width_scale_factor: scale factor for hvdc capacities.
    :param int/float b2b_size_scale_factor: scale factor for back-to_back capacities.
    :param bool background_map: whether to plot map tiles behind figure.
    :return: (*bokeh.plotting.figure*) -- map of transmission lines.
    :raises TypeError:
        if ``branch_device_cutoff`` is not ``float``.
        if ``figsize`` is not a tuple.
        if ``branch_width_scale_factor`` is not ``int`` or ``float``.
        if ``hvdc_width_scale_factor`` is not ``int`` or ``float``.
        if ``b2b_size_scale_factor`` is not ``int`` or ``float``.
        if ``background_map`` is not a ``bool``.
    :raises ValueError:
        if ``branch_device_cutoff`` is negative.
        if both elements of ``figsize`` are not positive.
        if ``branch_width_scale_factor`` is negative.
        if ``hvdc_width_scale_factor`` is negative.
        if ``b2b_size_scale_factor`` is negative.
        if grid model is not supported.
    """
    _check_grid(grid)
    if not isinstance(branch_distance_cutoff, (int, float)):
        raise TypeError("branch_distance_cutoff must be an int")
    if branch_distance_cutoff <= 0:
        raise ValueError("branch_distance_cutoff must be strictly positive")
    if not isinstance(figsize, tuple):
        raise TypeError("figsize must be a tuple")
    if not (len(figsize) == 2 and all(e > 0 for e in figsize)):
        raise ValueError("both elemets of figsize must be positive")
    if not isinstance(branch_width_scale_factor, (int, float)):
        raise TypeError("branch_width_scale_factor must be a int/float")
    if branch_width_scale_factor < 0:
        raise ValueError("branch_width_scale_factor must be positive")
    if not isinstance(hvdc_width_scale_factor, (int, float)):
        raise TypeError("hvdc_width_scale_factor must be a int/float")
    if hvdc_width_scale_factor < 0:
        raise ValueError("hvdc_width_scale_factor must be positive")
    if not isinstance(b2b_size_scale_factor, (int, float)):
        raise TypeError("b2b_size_scale_factor must be a int/float")
    if b2b_size_scale_factor < 0:
        raise ValueError("b2b_size_scale_factor must be positive")
    if not isinstance(background_map, bool):
        raise TypeError("background_map must be a bool")

    # branches
    branch = grid.branch.copy()
    branch["to_coord"] = list(zip(branch["to_lat"], branch["to_lon"]))
    branch["from_coord"] = list(zip(branch["from_lat"], branch["from_lon"]))
    branch["dist"] = branch.apply(
        lambda row: distance.haversine(row["to_coord"], row["from_coord"]), axis=1
    )
    branch = branch.loc[branch["dist"] > branch_distance_cutoff]
    branch = project_branch(branch)

    branch_west = branch.loc[branch["interconnect"] == "Western"]
    branch_east = branch.loc[branch["interconnect"] == "Eastern"]
    branch_tx = branch.loc[branch["interconnect"] == "Texas"]

    # HVDC lines
    all_dcline = grid.dcline.copy()
    all_dcline["from_lon"] = grid.bus.loc[all_dcline["from_bus_id"], "lon"].values
    all_dcline["from_lat"] = grid.bus.loc[all_dcline["from_bus_id"], "lat"].values
    all_dcline["to_lon"] = grid.bus.loc[all_dcline["to_bus_id"], "lon"].values
    all_dcline["to_lat"] = grid.bus.loc[all_dcline["to_bus_id"], "lat"].values
    all_dcline = project_branch(all_dcline)

    if grid.get_grid_model() == "usa_tamu":
        b2b_id = range(9)
    else:
        raise ValueError("grid model is not supported")
    dcline = all_dcline.iloc[~all_dcline.index.isin(b2b_id)]
    b2b = all_dcline.iloc[b2b_id]

    p = figure(
        tools="pan,wheel_zoom,reset,save",
        x_axis_location=None,
        y_axis_location=None,
        plot_width=figsize[0],
        plot_height=figsize[1],
        output_backend="webgl",
        sizing_mode="scale_both",
        match_aspect=True,
    )

    p.xgrid.visible = False
    p.ygrid.visible = False

    state_counts = count_nodes_per_state(grid)
    plot_states(
        bokeh_figure=p,
        background_map=background_map,
        state_list=state_counts.index,
        labels_list=state_counts.to_numpy(),
        tooltip_name="nodes",
    )

    p.multi_line(
        branch_west[["from_x", "to_x"]].to_numpy().tolist(),
        branch_west[["from_y", "to_y"]].to_numpy().tolist(),
        color="#006ff9",
        line_width=branch_west["rateA"].abs() * 1e-3 * branch_width_scale_factor,
        legend_label="Western",
    )

    p.multi_line(
        branch_east[["from_x", "to_x"]].to_numpy().tolist(),
        branch_east[["from_y", "to_y"]].to_numpy().tolist(),
        color="#8B36FF",
        line_width=branch_east["rateA"].abs() * 1e-3 * branch_width_scale_factor,
        legend_label="Eastern",
    )

    p.multi_line(
        branch_tx[["from_x", "to_x"]].to_numpy().tolist(),
        branch_tx[["from_y", "to_y"]].to_numpy().tolist(),
        color="#01D4ED",
        line_width=branch_tx["rateA"].abs() * 1e-3 * branch_width_scale_factor,
        legend_label="Texas",
    )

    p.multi_line(
        dcline[["from_x", "to_x"]].to_numpy().tolist(),
        dcline[["from_y", "to_y"]].to_numpy().tolist(),
        color="#FF2370",
        line_width=dcline["Pmax"] * 1e-3 * hvdc_width_scale_factor,
        legend_label="HVDC",
    )

    p.scatter(
        x=b2b["from_x"],
        y=b2b["from_y"],
        color="#FF2370",
        marker="triangle",
        size=b2b["Pmax"] * 1e-3 * b2b_size_scale_factor,
        legend_label="Back-to-Back",
    )

    p.legend.location = "bottom_left"
    p.legend.label_text_font_size = "12pt"

    return p
