# This plotting module has a corresponding demo notebook in
#   PostREISE/postreise/plot/demo: renewable_capacity_map_demo.ipynb

import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.tile_providers import Vendors, get_provider

from postreise.analyze.check import _check_scenario_is_in_analyze_state
from postreise.plot.colors import be_green
from postreise.plot.plot_states import get_state_borders
from postreise.plot.projection_helpers import project_borders, project_bus


def map_plant_capacity(scenario, us_states_dat=None, size_factor=1):
    """Makes map of renewables from change table 'new plants'. Size/area
    indicates capacity.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param dict us_states_dat: dictionary of state border lats/lons. If None, get
        from :func:`postreise.plot.plot_states.get_state_borders`.
    :param float/int size_factor: scale size of glyphs.
    """

    _check_scenario_is_in_analyze_state(scenario)

    # prepare data from the change table to select new plants
    ct = scenario.state.get_ct()
    # check that there are new plants, check scenario is in analyze state
    if "new_plant" not in ct.keys():
        raise ValueError(
            "There are no new plants added in the selected scenario. Please choose a different scenario."
        )
    if us_states_dat is None:
        us_states_dat = get_state_borders()

    newplant = pd.DataFrame(ct["new_plant"])
    newplant = newplant.set_index("bus_id")
    newplant = newplant[newplant.Pmax > 0]

    # merge with bus info to get coordinates
    gridscen = scenario.state.get_grid()
    bus_of_interest = gridscen.bus.loc[list(set(newplant.index))]
    bus_capacity = bus_of_interest.merge(newplant, right_index=True, left_index=True)

    bus_map = project_bus(bus_capacity)
    bus_map1 = bus_map.loc[bus_map.Pmax > 1]
    rar_df = bus_map1.loc[(bus_map1.type_y == "solar") | (bus_map1.type_y == "wind")]

    # group by coordinates
    rar_df = rar_df.groupby(["lat", "lon"]).agg(
        {"Pmax": "sum", "x": "mean", "y": "mean"}
    )

    a, b = project_borders(us_states_dat)

    rar_source = ColumnDataSource(
        {
            "x": rar_df["x"],
            "y": rar_df["y"],
            "capacity": (rar_df["Pmax"] * size_factor) ** 0.5,
            "capacitymw": rar_df["Pmax"],
        }
    )

    tools: str = "pan,wheel_zoom,reset,save"
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

    # for legend, plot behind tiles
    p.circle(
        -8.1e6,
        5.2e6,
        fill_color=be_green,
        color=be_green,
        alpha=0.5,
        size=50,
        legend_label="Renewable Capacity Added",
    )

    p.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))

    # state borders
    p.patches(a, b, fill_alpha=0.0, line_color="gray", line_width=2)

    # capacity circles
    circle = p.circle(
        "x",
        "y",
        fill_color=be_green,
        color=be_green,
        alpha=0.8,
        size="capacity",
        source=rar_source,
    )
    p.legend.label_text_font_size = "12pt"
    p.legend.location = "bottom_right"

    hover = HoverTool(
        tooltips=[
            ("Capacity (MW)", "@capacitymw"),
        ],
        renderers=[circle],
    )

    p.add_tools(hover)

    return p
