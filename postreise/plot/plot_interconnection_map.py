from postreise.plot.projection_helpers import project_branch
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.sampledata import us_states
from postreise.plot import plot_carbon_map
from bokeh.tile_providers import get_provider, Vendors


def map_interconnections(grid, us_states_dat=us_states.data):
    """Makes map of transmission color coded by interconnection

    :param grid: grid object
    :param dict us_states_dat: us_states data file, imported from bokeh.
    :return:  -- map of transmission
    """
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
    multi_line_source = ColumnDataSource(
        {
            "xs": branch_west[["from_x", "to_x"]].values.tolist(),
            "ys": branch_west[["from_y", "to_y"]].values.tolist(),
            "capacity": (branch_west.rateA) / (99999 * 2) * 45 + 0.1,
        }
    )

    multi_line_source2 = ColumnDataSource(
        {
            "xs": branch_east[["from_x", "to_x"]].values.tolist(),
            "ys": branch_east[["from_y", "to_y"]].values.tolist(),
            "capacity": (branch_east.rateA) / (99999 * 2) * 45 + 0.1,
        }
    )

    multi_line_source3 = ColumnDataSource(
        {
            "xs": branch_tx[["from_x", "to_x"]].values.tolist(),
            "ys": branch_tx[["from_y", "to_y"]].values.tolist(),
            "capacity": (branch_tx.rateA) / (99999 * 2) * 45 + 0.1,
        }
    )

    multi_line_source4 = ColumnDataSource(
        {
            "xs": branch_mdc[["from_x", "to_x"]].values.tolist(),
            "ys": branch_mdc[["from_y", "to_y"]].values.tolist(),
            "capacity": (branch_mdc.Pmax.astype(float)) / (9999 * 2) * 45 + 0.1,
        }
    )

    # Set up figure
    tools: str = "pan,wheel_zoom,reset,hover,save"

    p = figure(
        title="Interconnections",
        tools=tools,
        x_axis_location=None,
        y_axis_location=None,
        plot_width=800,
        plot_height=800,
        output_backend="webgl",
    )

    # for legend
    p.multi_line(
        [-1.084288e07, -1.084288e07],
        [4.639031e06, 4.639031e06],
        color="blue",
        line_width=5,
        legend="Western",
    )
    p.multi_line(
        [-1.084288e07, -1.084288e07],
        [4.639031e06, 4.639031e06],
        color="red",
        line_width=5,
        legend="Eastern",
    )
    p.multi_line(
        [-1.084288e07, -1.084288e07],
        [4.639031e06, 4.639031e06],
        color="purple",
        line_width=5,
        legend="ERCOT",
    )
    p.multi_line(
        [-1.084288e07, -1.084288e07],
        [4.639031e06, 4.639031e06],
        color="green",
        line_width=5,
        legend="HVDC",
    )
    p.square(
        x=[-1.084288e07], y=[4.639031e06], size=170, fill_color="white", color="white"
    )
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))

    # state borders
    p.patches(a, b, fill_alpha=0.0, line_color="black", line_width=2)
    # branches
    p.multi_line(
        "xs", "ys", color="blue", line_width="capacity", source=multi_line_source
    )
    p.multi_line(
        "xs", "ys", color="red", line_width="capacity", source=multi_line_source2
    )
    p.multi_line(
        "xs", "ys", color="purple", line_width="capacity", source=multi_line_source3
    )
    p.multi_line(
        "xs", "ys", color="green", line_width="capacity", source=multi_line_source4
    )
    p.legend.location = "bottom_right"

    return p
