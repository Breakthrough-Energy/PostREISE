from postreise.plot.projection_helpers import project_branch
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.sampledata import us_states
from postreise.plot import plot_carbon_map
from bokeh.tile_providers import get_provider, Vendors


def map_interconnections(grid, hvdc_width=1, us_states_dat=None):
    """Maps transmission lines color coded by interconnection

    :param grid: grid object
    :param dict us_states_dat: if None default to us_states data file, imported from bokeh.
    :param float hvdc_width: adjust width of HVDC lines on map
    :return:  -- map of transmission
    """
    if us_states_dat is None:
        us_states_dat = us_states.data

    # projection steps for mapping
    branch = grid.branch
    branch_bus = grid.bus
    branch_map = project_branch(branch)
    branch_west = branch_map.loc[branch_map.interconnect == "Western"]
    branch_east = branch_map.loc[branch_map.interconnect == "Eastern"]
    branch_tx = branch_map.loc[branch_map.interconnect == "Texas"]
    branch_mdc = grid.dcline

    branch_mdc["from_lon"] = branch_bus.loc[branch_mdc.from_bus_id, "lon"].values
    branch_mdc["from_lat"] = branch_bus.loc[branch_mdc.from_bus_id, "lat"].values
    branch_mdc["to_lon"] = branch_bus.loc[branch_mdc.to_bus_id, "lon"].values
    branch_mdc["to_lat"] = branch_bus.loc[branch_mdc.to_bus_id, "lat"].values
    branch_mdc = project_branch(branch_mdc)
    # state borders
    a, b = plot_carbon_map.get_borders(us_states_dat.copy())

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

    multi_line_source4 = ColumnDataSource(
        {
            "xs": branch_mdc[["from_x", "to_x"]].values.tolist(),
            "ys": branch_mdc[["from_y", "to_y"]].values.tolist(),
            "capacity": branch_mdc.Pmax.astype(float) * line_width_const * hvdc_width
            + 0.1,
            "cap": branch_mdc.Pmax.astype(float),
        }
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
    leg_clr = ["#d8428d", "#0c84e2", "#6D3376", "#012f56"]
    leg_lab = ["Western", "Eastern", "ERCOT", "HVDC"]
    leg_xs = [-1.084288e07] * 4
    leg_ys = [4.639031e06] * 4

    for (colr, leg, x, y) in zip(leg_clr, leg_lab, leg_xs, leg_ys):
        p.line(x, y, color=colr, width=5, legend=leg)

    # background tiles
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))

    # state borders
    p.patches(a, b, fill_alpha=0.0, line_color="#808184", line_width=2)

    # branches
    source_list = [multi_line_source, multi_line_source2, multi_line_source3]

    for (colr, source) in zip(leg_clr[0:3], source_list):
        p.multi_line("xs", "ys", color=colr, line_width="capacity", source=source)

    lines = p.multi_line(
        "xs", "ys", color="#012f56", line_width="capacity", source=multi_line_source4
    )
    p.legend.location = "bottom_right"

    hover = HoverTool(
        tooltips=[
            ("HVDC capacity MW", "@cap"),
        ],
        renderers=[lines],
    )
    p.add_tools(hover)

    return p
