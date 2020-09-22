from postreise.plot.projection_helpers import project_branch
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.sampledata import us_states
from postreise.plot import plot_carbon_map
from bokeh.tile_providers import get_provider, Vendors
import numpy as np
from powersimdata.network.usa_tamu.constants import zones
import pandas as pd
from powersimdata.utility import distance


def count_nodes_per_state(grid):
    """
    count nodes per state to add as hover-over info in map_interconnections

    :param powersimdata.input.grid.Grid grid: grid object
    :return:  -- dataframe containing state names and count of nodes per state
    """
    grid.bus["state"] = grid.bus["zone_id"].map(zones.id2state)
    liststates = grid.bus["state"].value_counts()
    state_counts = pd.DataFrame(liststates)
    state_counts.reset_index(inplace=True)
    state_counts.rename(columns={"index": "state", "state": "count"}, inplace=True)

    return state_counts


def map_interconnections(
    grid, state_counts, hover_choice, hvdc_width=1, us_states_dat=None
):
    """Maps transmission lines color coded by interconnection

    :param powersimdata.input.grid.Grid grid: grid object
    :param pandas.DataFrame state_counts: state names and node counts, created by count_nodes_per_state
    :param str hover_choice: "nodes" for state_counts nodes per state, otherwise hvdc
        capacity in hover over tool tips for hvdc lines only
    :param float hvdc_width: adjust width of HVDC lines on map
    :param dict us_states_dat: if None default to us_states data file, imported from bokeh.
    :return:  -- map of transmission lines
    """
    if us_states_dat is None:
        us_states_dat = us_states.data

    # projection steps for mapping
    branch = grid.branch
    branch_bus = grid.bus
    branch_map = project_branch(branch)
    branch_map["point1"] = list(zip(branch_map.to_lat, branch_map.to_lon))
    branch_map["point2"] = list(zip(branch_map.from_lat, branch_map.from_lon))
    branch_map["dist"] = branch_map.apply(
        lambda row: distance.haversine(row["point1"], row["point2"]), axis=1
    )

    # speed rendering on website by removing very short branches
    branch_map = branch_map.loc[branch_map.dist > 5]

    branch_west = branch_map.loc[branch_map.interconnect == "Western"]
    branch_east = branch_map.loc[branch_map.interconnect == "Eastern"]
    branch_tx = branch_map.loc[branch_map.interconnect == "Texas"]
    branch_mdc = grid.dcline

    branch_mdc["from_lon"] = branch_bus.loc[branch_mdc.from_bus_id, "lon"].values
    branch_mdc["from_lat"] = branch_bus.loc[branch_mdc.from_bus_id, "lat"].values
    branch_mdc["to_lon"] = branch_bus.loc[branch_mdc.to_bus_id, "lon"].values
    branch_mdc["to_lat"] = branch_bus.loc[branch_mdc.to_bus_id, "lat"].values
    branch_mdc = project_branch(branch_mdc)

    # back to backs are index 0-8, treat separately
    branch_mdc1 = branch_mdc.iloc[
        9:,
    ]
    b2b = branch_mdc.iloc[
        0:9,
    ]

    branch_mdc_leg = branch_mdc
    branch_mdc_leg.loc[0:8, ["to_x"]] = np.nan
    branch_mdc_leg["to_x"] = branch_mdc_leg["to_x"].fillna(branch_mdc_leg["from_x"])
    branch_mdc_leg.loc[0:8, ["to_y"]] = np.nan
    branch_mdc_leg["to_y"] = branch_mdc_leg["to_y"].fillna(branch_mdc_leg["from_y"])

    # pseudolines for legend to show hvdc and back to back, plot UNDER map
    multi_line_source6 = ColumnDataSource(
        {
            "xs": branch_mdc_leg[["from_x", "to_x"]].values.tolist(),
            "ys": branch_mdc_leg[["from_y", "to_y"]].values.tolist(),
            "capacity": branch_mdc_leg.Pmax.astype(float) * 0.00023 + 0.2,
            "cap": branch_mdc_leg.Pmax.astype(float),
        }
    )

    # state borders
    a, b = plot_carbon_map.get_borders(
        us_states_dat.copy(), state_list=list(state_counts["state"])
    )

    # transmission data sources
    line_width_const = 0.000225

    multi_line_source = ColumnDataSource(
        {
            "xs": branch_west[["from_x", "to_x"]].values.tolist(),
            "ys": branch_west[["from_y", "to_y"]].values.tolist(),
            "capacity": branch_west.rateA * line_width_const + 0.1,
        }
    )

    multi_line_source2 = ColumnDataSource(
        {
            "xs": branch_east[["from_x", "to_x"]].values.tolist(),
            "ys": branch_east[["from_y", "to_y"]].values.tolist(),
            "capacity": branch_east.rateA * line_width_const + 0.1,
        }
    )

    multi_line_source3 = ColumnDataSource(
        {
            "xs": branch_tx[["from_x", "to_x"]].values.tolist(),
            "ys": branch_tx[["from_y", "to_y"]].values.tolist(),
            "capacity": branch_tx.rateA * line_width_const + 0.1,
        }
    )
    # hvdc
    multi_line_source4 = ColumnDataSource(
        {
            "xs": branch_mdc1[["from_x", "to_x"]].values.tolist(),
            "ys": branch_mdc1[["from_y", "to_y"]].values.tolist(),
            "capacity": branch_mdc1.Pmax.astype(float) * line_width_const * hvdc_width
            + 0.1,
            "cap": branch_mdc1.Pmax.astype(float),
        }
    )

    # pseudolines for ac
    multi_line_source5 = ColumnDataSource(
        {
            "xs": b2b[["from_x", "to_x"]].values.tolist(),
            "ys": b2b[["from_y", "to_y"]].values.tolist(),
            "capacity": b2b.Pmax.astype(float) * 0.00023 + 0.2,
            "cap": b2b.Pmax.astype(float),
            "col": (
                "#006ff9",
                "#006ff9",
                "#006ff9",
                "#006ff9",
                "#006ff9",
                "#006ff9",
                "#006ff9",
                "#8B36FF",
                "#8B36FF",
            ),
        }
    )

    # lower 48 states, patches
    source = ColumnDataSource(
        dict(
            xs=a,
            ys=b,
            col=["gray" for i in range(48)],
            col2=["gray" for i in range(48)],
            label=list(state_counts["count"]),
            state_name=list(state_counts["state"]),
        )
    )

    # Set up figure
    tools: str = "pan, wheel_zoom, reset, save"

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

    # for legend, hidden lines
    leg_clr = ["#006ff9", "#8B36FF", "#01D4ED", "#FF2370"]
    leg_lab = ["Western", "Eastern", "Texas", "HVDC"]
    leg_xs = [-1.084288e07] * 4
    leg_ys = [4.639031e06] * 4

    for (colr, leg, x, y) in zip(leg_clr, leg_lab, leg_xs, leg_ys):
        p.line(x, y, color=colr, width=5, legend=leg)

    # pseudo lines for hover tips
    lines = p.multi_line(
        "xs", "ys", color="black", line_width="capacity", source=multi_line_source6
    )

    # background tiles
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))

    # state borders
    patch = p.patches("xs", "ys", fill_alpha=0.0, line_color="col", source=source)

    # branches
    source_list = [multi_line_source, multi_line_source2, multi_line_source3]

    for (colr, source) in zip(leg_clr[0:3], source_list):
        p.multi_line("xs", "ys", color=colr, line_width="capacity", source=source)

    p.multi_line(
        "xs", "ys", color="#FF2370", line_width="capacity", source=multi_line_source4
    )
    # pseudo ac
    p.multi_line(
        "xs", "ys", color="col", line_width="capacity", source=multi_line_source5
    )

    # triangles for b2b
    p.scatter(
        x=b2b.from_x,
        y=b2b.from_y,
        color="#FF2370",
        marker="triangle",
        size=b2b.Pmax / 50 + 5,
        legend="Back-to-Back",
    )

    # legend formatting
    p.legend.location = "bottom_right"
    p.legend.label_text_font_size = "12pt"

    if hover_choice == "nodes":
        hover = HoverTool(
            tooltips=[
                ("State", "@state_name"),
                ("Nodes", "@label"),
            ],
            renderers=[patch],
        )

    else:
        hover = HoverTool(
            tooltips=[
                ("HVDC capacity MW", "@cap"),
            ],
            renderers=[lines],
        )

    p.add_tools(hover)

    return p
