import numpy as np
from bokeh.plotting import show, figure
from bokeh.tile_providers import get_provider, Vendors
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.layouts import row


def map_carbon_emission(bus_map, scenario_name, color1='black', color2='purple',
                        label1="Coal: tons", label2="NG: tons"):
    """Make map of carbon emissions, color code by fuel type, size/area
        indicates emissions.

    :param pandas.DataFrame bus_map: emissions and coordinates of buses as
        returned by :func:`postreise.analyze.plot_helper.make_emitter_map`.
    :param str scenario_name: name of scenario for labeling.
    :param str color1: color assigned for coal, default to black.
    :param str color2: color assigned for ng, default to purple.
    :param str label1: label for legend associated with coal.
    :param str label2: label for legend associated with ng.
    """
    bus_source = ColumnDataSource({
        'x': bus_map['x'],
        'y': bus_map['y'],
        'coal': (bus_map['coal']/500)**0.5,
        'ng': (bus_map['ng']/500)**0.5})

    # Set up figure
    tools: str = "pan,wheel_zoom,reset,hover,save"

    p = figure(title=scenario_name, tools=tools, x_axis_location=None,
               y_axis_location=None, plot_width=800, plot_height=800)

    p_legend = figure(x_axis_location=None, y_axis_location=None,
                      toolbar_location=None, plot_width=200, plot_height=400,
                      y_range=(0, 4), x_range=(0, 2))

    p.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))

    p.circle('x', 'y', fill_color=color1, color=color1, alpha=0.25, size='coal',
             source=bus_source)

    p.circle('x', 'y', fill_color=color2, color=color2, alpha=0.25, size='ng',
             source=bus_source)

    # legend is custom: white square background and circles of different size
    # on top

    p_legend.square(1, [1, 3], fill_color='white', color='white', size=300)

    p_legend.square(1, [1, 3], fill_color='white', color='black',
                    size=(2000000/100)**0.5)

    p_legend.circle(1, y=np.repeat([1, 3], 3),
                    fill_color=np.repeat([color1, color2], 3),
                    color=np.repeat([color1, color2], 3), alpha=0.25,
                    size=[(5000000/500)**0.5, (2000000/500)**0.5,
                          (100000/500)**0.5]*2)

    source = ColumnDataSource(
        data=dict(x=[1, 1, 1, 0.5, 1, 1, 1, 0.5],
                  y=[.9, 1.1, 1.3, 1.55, 2.9, 3.1, 3.3, 3.55],
                  text=['100000', '2000000', '5000000', label1, '100000',
                        '2000000', '5000000', label2]))

    labels = LabelSet(x='x', y='y', text='text', source=source, level='glyph',
                      x_offset=0, y_offset=0, render_mode='css')

    p_legend.add_layout(labels)

    output_notebook()
    show(row(p_legend, p))


def map_carbon_emission_comparison(bus_map1, bus_map2, scenario_name1,
                                   scenario_name2):
    """Make map of carbon emissions, color code by fuel type, size/area
        indicates emissions.

    :param pandas.DataFrame bus_map1: emissions and coordinates of buses for
        first scenario.
    :param pandas.DataFrame bus_map2: emissions and coordinates of buses for
        second scenario.
    :param str scenario_name1: name of first scenario for labeling.
    :param str scenario_name2: name of second scenario for labeling
    :return: (pandas.DataFrame) -- comparison map
        indicating increase or decrease
    """
    map_carbon_emission(bus_map1, scenario_name1)
    map_carbon_emission(bus_map2, scenario_name2)

    bus_map = bus_map1.merge(bus_map2, right_index=True, left_index=True,
                                   how='outer')
    bus_map.coal_x = bus_map.coal_x.fillna(0)
    bus_map.coal_y = bus_map.coal_y.fillna(0)
    bus_map.ng_x = bus_map.ng_x.fillna(0)
    bus_map.ng_y = bus_map.ng_y.fillna(0)

    bus_map['coal_dif'] = bus_map['coal_x'] - bus_map['coal_y']
    bus_map['ng_dif'] = bus_map['ng_x'] - bus_map['ng_y']
    bus_map['x'] = bus_map['x_x'].fillna(bus_map['x_y'])
    bus_map['y'] = bus_map['y_x'].fillna(bus_map['y_y'])
    bus_map["coal"] = 0
    bus_map["ng"] = 0
    bus_map.loc[bus_map.coal_dif > 0, ['coal']] = bus_map['coal_dif']
    bus_map.loc[bus_map.ng_dif > 0, ['coal']] = bus_map['ng_dif']

    bus_map.loc[bus_map.coal_dif < 0, ['ng']] = abs(bus_map['coal_dif'])
    bus_map.loc[bus_map.ng_dif < 0, ['ng']] = abs(bus_map['ng_dif'])

    map_carbon_emission(bus_map, "compare", "green", "red", "Less: tons",
                        "More: tons")

    return bus_map
