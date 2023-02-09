import pandas as pd
from powersimdata.input.check import _check_grid_type
from powersimdata.network.model import ModelImmutables
from powersimdata.utility import distance

from postreise.plot.canvas import create_map_canvas
from postreise.plot.colors import grid_colors
from postreise.plot.plot_borders import add_borders, add_tooltips
from postreise.plot.projection_helpers import project_branch


def count_nodes_per_area(grid):
    """Count nodes per area to add as hover-over info in :func`map_interconnections`

    :param powersimdata.input.grid.Grid grid: grid object.
    :return: (*pandas.Series*) -- index: area names, values: number of nodes.
    """
    id2area = ModelImmutables(grid.grid_model).zones["id2abv"]
    grid.bus["area"] = grid.bus["zone_id"].map(id2area)
    counts = pd.Series(grid.bus["area"].value_counts())

    return counts


def map_interconnections(
    grid,
    branch_distance_cutoff=5,
    figsize=(1400, 800),
    branch_width_scale_factor=0.5,
    hvdc_width_scale_factor=1,
    b2b_size_scale_factor=50,
    borders_kwargs=None,
):
    """Map transmission lines color coded by interconnection.

    :param powersimdata.input.grid.Grid grid: grid object.
    :param int/float branch_distance_cutoff: distance cutoff for branch display.
    :param tuple figsize: size of the bokeh figure (in pixels).
    :param int/float branch_width_scale_factor: scale factor for branch capacities.
    :param int/float hvdc_width_scale_factor: scale factor for hvdc capacities.
    :param int/float b2b_size_scale_factor: scale factor for back-to_back capacities.
    :param dict borders_kwargs: keyword arguments to be passed to
        :func:`postreise.plot.plot_borders.add_borders`.
    :return: (*bokeh.plotting.figure*) -- interconnection map with lines and nodes.
    :raises TypeError:
        if ``branch_device_cutoff`` is not ``float``.
        if ``branch_width_scale_factor`` is not ``int`` or ``float``.
        if ``hvdc_width_scale_factor`` is not ``int`` or ``float``.
        if ``b2b_size_scale_factor`` is not ``int`` or ``float``.
    :raises ValueError:
        if ``branch_device_cutoff`` is negative.
        if ``branch_width_scale_factor`` is negative.
        if ``hvdc_width_scale_factor`` is negative.
        if ``b2b_size_scale_factor`` is negative.
        if grid model is not supported.
    """
    _check_grid_type(grid)
    if not isinstance(branch_distance_cutoff, (int, float)):
        raise TypeError("branch_distance_cutoff must be an int")
    if branch_distance_cutoff <= 0:
        raise ValueError("branch_distance_cutoff must be strictly positive")
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

    # branches
    branch = grid.branch.copy()
    branch["to_coord"] = list(zip(branch["to_lat"], branch["to_lon"]))
    branch["from_coord"] = list(zip(branch["from_lat"], branch["from_lon"]))
    branch["dist"] = branch.apply(
        lambda row: distance.haversine(row["to_coord"], row["from_coord"]), axis=1
    )
    branch = branch.loc[branch["dist"] > branch_distance_cutoff]
    branch = project_branch(branch)

    # HVDC lines
    all_dcline = grid.dcline.copy()
    all_dcline["from_lon"] = grid.bus.loc[all_dcline["from_bus_id"], "lon"].values
    all_dcline["from_lat"] = grid.bus.loc[all_dcline["from_bus_id"], "lat"].values
    all_dcline["to_lon"] = grid.bus.loc[all_dcline["to_bus_id"], "lon"].values
    all_dcline["to_lat"] = grid.bus.loc[all_dcline["to_bus_id"], "lat"].values
    all_dcline = project_branch(all_dcline)

    if grid.grid_model == "usa_tamu":
        b2b_id = range(9)
    elif grid.grid_model == "europe_tub":
        b2b_id = []
        all_dcline = all_dcline.loc[all_dcline["pypsa_length"] > 0.0]
    else:
        raise ValueError("grid model is not supported")
    dcline = all_dcline.iloc[~all_dcline.index.isin(b2b_id)]
    b2b = all_dcline.iloc[b2b_id]

    # create canvas
    canvas = create_map_canvas(figsize=figsize)

    # add borders
    default_borders_kwargs = {
        "line_width": 2,
        "fill_alpha": 0,
        "background_map": False,
    }
    all_borders_kwargs = (
        {**default_borders_kwargs, **borders_kwargs}
        if borders_kwargs is not None
        else default_borders_kwargs
    )

    canvas = add_borders(grid.grid_model, canvas, all_borders_kwargs)

    # create labels for tooltips
    # TODO: tooltips working for USA, needs fix for europe
    # node_counts = count_nodes_per_area(grid)
    # area2label = {a: c for a, c in zip(node_counts.index, node_counts.to_numpy())}
    # canvas = add_tooltips(grid.model, canvas, "nodes", area2label)

    for interconnect in branch["interconnect"].unique():
        branches = branch.loc[branch["interconnect"] == interconnect]
        canvas.multi_line(
            branches[["from_x", "to_x"]].to_numpy().tolist(),
            branches[["from_y", "to_y"]].to_numpy().tolist(),
            color=grid_colors.get(grid.grid_model, {}).get(interconnect, "black"),
            line_width=branches["rateA"].abs() * 1e-3 * branch_width_scale_factor,
            legend_label=interconnect,
        )

    canvas.multi_line(
        dcline[["from_x", "to_x"]].to_numpy().tolist(),
        dcline[["from_y", "to_y"]].to_numpy().tolist(),
        color="#FF2370",
        line_width=dcline["Pmax"] * 1e-3 * hvdc_width_scale_factor,
        legend_label="HVDC",
    )

    canvas.scatter(
        x=b2b["from_x"],
        y=b2b["from_y"],
        color="#FF2370",
        marker="triangle",
        size=b2b["Pmax"] * 1e-3 * b2b_size_scale_factor,
        legend_label="Back-to-Back",
    )

    canvas.legend.location = "bottom_left"
    canvas.legend.label_text_font_size = "12pt"

    return canvas
