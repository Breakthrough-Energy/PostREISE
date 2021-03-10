import pandas as pd
from bokeh.io import show
from bokeh.models import Arrow, VeeHead
from bokeh.plotting import figure
from powersimdata.utility.distance import haversine

from postreise.analyze.check import (
    _check_date_range_in_scenario,
    _check_scenario_is_in_analyze_state,
)
from postreise.plot.plot_states import plot_states
from postreise.plot.projection_helpers import project_branch, project_bus


def plot_arrows(bokeh_figure, branch, color, pf_threshold=0, dist_threshold=0, n=1):
    """Add addorws for powerflow to figure.

    :param bokeh.plotting.figure.Figure bokeh_figure: figure to plot arrows onto.
    :param pandas.DataFrame branch: data frame containing:
        'pf', 'dist', 'arrow_size', 'from_x', 'from_y', 'to_x', 'to_y'.
        x/y coordinates for to/from can be obtained from lat/lon coordinates
        using :func:`postreise.plot.projection_helpers.project_branch`.
    :param str color: arrow line color.
    :param int/float pf_threshold: minimum power flow for a branch to get arrow(s).
    :param int/float pf_threshold: minimum distance for a branch to get arrow(s).
    :param int n: number of arrows to plot along each branch.
    """
    positive_arrows = branch.loc[
        (branch.pf > pf_threshold) & (branch.dist > dist_threshold)
    ]
    negative_arrows = branch.loc[
        (branch.pf < -1 * pf_threshold) & (branch.dist > dist_threshold)
    ]
    # Swap direction of negative arrows
    negative_arrows = negative_arrows.rename(
        columns={"from_x": "to_x", "to_x": "from_x", "to_y": "from_y", "from_y": "to_y"}
    )
    # Finally, plot arrows
    arrows = pd.concat([positive_arrows, negative_arrows])
    for i in range(n):
        start_fraction = i / n
        end_fraction = (i + 1) / n
        arrows.apply(
            lambda a: bokeh_figure.add_layout(
                Arrow(
                    end=VeeHead(
                        line_color="black",
                        fill_color="gray",
                        line_width=2,
                        fill_alpha=0.5,
                        line_alpha=0.5,
                        size=a["arrow_size"],
                    ),
                    x_start=(a["from_x"] + (a["to_x"] - a["from_x"]) * start_fraction),
                    y_start=(a["from_y"] + (a["to_y"] - a["from_y"]) * start_fraction),
                    x_end=(a["from_x"] + (a["to_x"] - a["from_x"]) * end_fraction),
                    y_end=(a["from_y"] + (a["to_y"] - a["from_y"]) * end_fraction),
                    line_color=color,
                    line_alpha=0.7,
                )
            ),
            axis=1,
        )


def aggregate_plant_generation(plant, coordinate_rounding=0):
    """Aggregate generation for plants based on similar lat/lon coordinates.

    :param int coordinate_rounding: number of digits to round lat & lon for aggregation.
    :param pandas.DataFrame plant: data frame containing: 'lat', 'lon', 'x', 'y', 'pg'.
    :return: (*pandas.DataFrame*) -- data frame aggregated to the desired precision.
    """
    plant_w_xy = project_bus(plant)
    plant_w_xy["lat"] = plant_w_xy["lat"].round(coordinate_rounding)
    plant_w_xy["lon"] = plant_w_xy["lon"].round(coordinate_rounding)
    aggregated = plant_w_xy.groupby(["lat", "lon"]).agg(
        {"pg": "sum", "x": "mean", "y": "mean"}
    )
    return aggregated


def plot_powerflow_snapshot(
    scenario,
    hour,
    b2b_dclines=None,
    demand_centers=None,
    ac_branch_color="#8B36FF",
    dc_branch_color="#01D4ED",
    solar_color="#FFBB45",
    wind_color="#78D911",
    demand_color="gray",
    figsize=(1400, 800),
    circle_scale_factor=0.25,
    bg_width_scale_factor=0.001,
    pf_width_scale_factor=0.00125,
    arrow_pf_threshold=3000,
    arrow_dist_threshold=20,
    num_ac_arrows=1,
    num_dc_arrows=1,
    min_arrow_size=5,
    branch_alpha=0.5,
    background_map=False,
    x_range=None,
    y_range=None,
    legend_font_size=None,
):
    """Plot a snapshot of powerflow.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario to plot.
    :param pandas.Timestamp/numpy.datetime64/datetime.datetime hour: snapshot interval.
    :param dict b2b_dclines: which DC lines are actually B2B facilities. Keys are:
        {"from", "to"}, values are iterables of DC line indices to plot (indices in
        "from" get plotted at the "from" end, and vice versa).
    :param pandas.DataFrame demand_centers: lat/lon centers at which to plot the demand
        from each load zone.
    :param str ac_branch_color: color to plot AC branches.
    :param str dc_branch_color: color to plot DC branches.
    :param str solar_color: color to plot solar generation.
    :param str wind_color: color to plot wind generation.
    :param str demand_color: color to plot demand.
    :param tuple(int, int) figsize: size of the bokeh figure (in pixels).
    :param int/float circle_scale_factor: scale factor for demand/solar/wind circles.
    :param int/float bg_width_scale_factor: scale factor for grid capacities.
    :param int/float pf_width_scale_factor: scale factor for power flows.
    :param int/float arrow_pf_threshold: minimum power flow (MW) for adding arrows.
    :param int/float arrow_dist_threshold: minimum distance (miles) for adding arrows.
    :param int num_ac_arrows: number of arrows for each AC branch.
    :param int num_dc_arrows: number of arrows for each DC branch.
    :param int/float min_arrow_size: minimum arrow size.
    :param int/float branch_alpha: opaqueness of branches.
    :param bool background_map: whether to plot map tiles behind figure.
    :param tuple(float, float) x_range: x range to zoom plot to (EPSG:3857).
    :param tuple(float, float) y_range: y range to zoom plot to (EPSG:3857).
    :param int/str legend_font_size: size to display legend specified as e.g. 12/'12pt'.
    """
    _check_scenario_is_in_analyze_state(scenario)
    _check_date_range_in_scenario(scenario, hour, hour)
    # Get scenario data
    grid = scenario.state.get_grid()
    bus = grid.bus
    plant = grid.plant
    # Augment the branch dataframe with extra info needed for plotting
    branch = grid.branch
    branch["pf"] = scenario.state.get_pf().loc[hour]
    branch = branch.query("pf != 0").copy()
    branch["dist"] = branch.apply(
        lambda x: haversine((x.from_lat, x.from_lon), (x.to_lat, x.to_lon)), axis=1
    )
    branch["arrow_size"] = branch["pf"].abs() * pf_width_scale_factor + min_arrow_size
    branch = project_branch(branch)
    # Augment the dcline dataframe with extra info needed for plotting
    dcline = grid.dcline
    dcline["pf"] = scenario.state.get_dcline_pf().loc[hour]
    dcline["from_lat"] = dcline.apply(lambda x: bus.loc[x.from_bus_id, "lat"], axis=1)
    dcline["from_lon"] = dcline.apply(lambda x: bus.loc[x.from_bus_id, "lon"], axis=1)
    dcline["to_lat"] = dcline.apply(lambda x: bus.loc[x.to_bus_id, "lat"], axis=1)
    dcline["to_lon"] = dcline.apply(lambda x: bus.loc[x.to_bus_id, "lon"], axis=1)
    dcline["dist"] = dcline.apply(
        lambda x: haversine((x.from_lat, x.from_lon), (x.to_lat, x.to_lon)), axis=1
    )
    dcline["arrow_size"] = dcline["pf"].abs() * pf_width_scale_factor + min_arrow_size
    dcline = project_branch(dcline)
    # Create a dataframe for demand plotting, if necessary
    if demand_centers is not None:
        demand = scenario.state.get_demand()
        demand_centers["demand"] = demand.loc[hour]
        demand_centers = project_bus(demand_centers)

    bokeh_figure = figure(
        tools="pan,wheel_zoom,reset,save",
        x_axis_location=None,
        y_axis_location=None,
        plot_width=figsize[0],
        plot_height=figsize[1],
        output_backend="webgl",
        match_aspect=True,
        x_range=x_range,
        y_range=y_range,
    )
    bokeh_figure.xgrid.visible = False
    bokeh_figure.ygrid.visible = False

    plot_states(bokeh_figure=bokeh_figure, background_map=background_map)

    if b2b_dclines is not None:
        # Append the pseudo AC lines to the branch dataframe, remove from dcline
        all_b2b_dclines = list(b2b_dclines["to"]) + list(b2b_dclines["from"])
        pseudo_ac_lines = dcline.loc[all_b2b_dclines]
        pseudo_ac_lines["rateA"] = pseudo_ac_lines[["Pmin", "Pmax"]].abs().max(axis=1)
        branch = branch.append(pseudo_ac_lines)
        # Construct b2b dataframe so that all get plotted at their 'from' x/y
        b2b_from = dcline.loc[b2b_dclines["from"]]
        b2b_to = dcline.loc[b2b_dclines["to"]].rename(
            {"from_x": "to_x", "from_y": "to_y", "to_x": "from_x", "to_y": "from_y"},
            axis=1,
        )
        b2b = pd.concat([b2b_from, b2b_to])
        dcline = dcline.loc[~dcline.index.isin(all_b2b_dclines)]

    # Plot grid background in grey
    bokeh_figure.multi_line(
        branch[["from_x", "to_x"]].to_numpy().tolist(),
        branch[["from_y", "to_y"]].to_numpy().tolist(),
        color="gray",
        alpha=branch_alpha,
        line_width=(branch["rateA"].abs() * bg_width_scale_factor),
    )
    bokeh_figure.multi_line(
        dcline[["from_x", "to_x"]].to_numpy().tolist(),
        dcline[["from_y", "to_y"]].to_numpy().tolist(),
        color="gray",
        alpha=branch_alpha,
        line_width=(dcline[["Pmin", "Pmax"]].abs().max(axis=1) * bg_width_scale_factor),
    )
    bokeh_figure.scatter(
        x=b2b.from_x,
        y=b2b.from_y,
        color="gray",
        alpha=0.5,
        marker="triangle",
        size=(b2b[["Pmin", "Pmax"]].abs().max(axis=1) * bg_width_scale_factor),
    )

    fake_location = branch.iloc[0].drop("x").rename({"from_x": "x", "from_y": "y"})
    # Legend entries
    bokeh_figure.multi_line(
        (fake_location.x, fake_location.x),
        (fake_location.y, fake_location.y),
        color=dc_branch_color,
        alpha=branch_alpha,
        line_width=10,
        legend_label="HVDC powerflow",
        visible=False,
    )
    bokeh_figure.multi_line(
        (fake_location.x, fake_location.x),
        (fake_location.y, fake_location.y),
        color=ac_branch_color,
        alpha=branch_alpha,
        line_width=10,
        legend_label="AC powerflow",
        visible=False,
    )
    bokeh_figure.circle(
        fake_location.x,
        fake_location.y,
        color=solar_color,
        alpha=0.6,
        size=5,
        legend_label="Solar Gen.",
        visible=False,
    )
    bokeh_figure.circle(
        fake_location.x,
        fake_location.y,
        color=wind_color,
        alpha=0.6,
        size=5,
        legend_label="Wind Gen.",
        visible=False,
    )
    bokeh_figure.circle(
        fake_location.x,
        fake_location.y,
        color=demand_color,
        alpha=0.3,
        size=5,
        legend_label="Demand",
        visible=False,
    )

    # Plot demand
    bokeh_figure.circle(
        demand_centers.x,
        demand_centers.y,
        color=demand_color,
        alpha=0.3,
        size=(demand_centers.demand * circle_scale_factor) ** 0.5,
    )
    # Aggregate solar and wind for plotting
    plant_with_pg = plant.copy()
    plant_with_pg["pg"] = scenario.state.get_pg().loc[hour]
    grouped_solar = aggregate_plant_generation(plant_with_pg.query("type == 'solar'"))
    grouped_wind = aggregate_plant_generation(plant_with_pg.query("type == 'wind'"))
    # Plot solar, wind
    bokeh_figure.circle(
        grouped_solar.x,
        grouped_solar.y,
        color=solar_color,
        alpha=0.6,
        size=(grouped_solar.pg * circle_scale_factor) ** 0.5,
    )
    bokeh_figure.circle(
        grouped_wind.x,
        grouped_wind.y,
        color=wind_color,
        alpha=0.6,
        size=(grouped_wind.pg * circle_scale_factor) ** 0.5,
    )

    # Plot powerflow on AC branches
    bokeh_figure.multi_line(
        branch[["from_x", "to_x"]].to_numpy().tolist(),
        branch[["from_y", "to_y"]].to_numpy().tolist(),
        color=ac_branch_color,
        alpha=branch_alpha,
        line_width=(branch["pf"].abs() * pf_width_scale_factor),
    )
    plot_arrows(
        bokeh_figure,
        branch,
        color=ac_branch_color,
        pf_threshold=arrow_pf_threshold,
        dist_threshold=arrow_dist_threshold,
        n=num_ac_arrows,
    )

    # Plot powerflow on DC lines
    bokeh_figure.multi_line(
        dcline[["from_x", "to_x"]].to_numpy().tolist(),
        dcline[["from_y", "to_y"]].to_numpy().tolist(),
        color=dc_branch_color,
        alpha=branch_alpha,
        line_width=(dcline["pf"].abs() * pf_width_scale_factor),
    )
    plot_arrows(
        bokeh_figure,
        dcline,
        color=dc_branch_color,
        pf_threshold=0,
        dist_threshold=0,
        n=num_dc_arrows,
    )
    # B2Bs
    bokeh_figure.scatter(
        x=b2b.from_x,
        y=b2b.from_y,
        color=dc_branch_color,
        alpha=0.5,
        marker="triangle",
        size=(b2b["pf"].abs() * pf_width_scale_factor * 5),
    )

    bokeh_figure.legend.location = "bottom_left"
    if legend_font_size is not None:
        if isinstance(legend_font_size, (int, float)):
            legend_font_size = f"{legend_font_size}pt"
        bokeh_figure.legend.label_text_font_size = legend_font_size

    show(bokeh_figure)
