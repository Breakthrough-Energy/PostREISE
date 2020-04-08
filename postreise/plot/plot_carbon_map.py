import numpy as np
import pandas as pd
from bokeh.plotting import show, figure
from bokeh.tile_providers import get_provider, Vendors
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.layouts import row
from bokeh.sampledata import us_states
from postreise.plot.projection_helpers import project_bus
from pyproj import Proj, transform

#prepare data for us state borders
def get_borders(us_states):
    del us_states["HI"]
    del us_states["AK"]
    # separate latitude and longitude points for the borders of the states.
    state_xs = [us_states[code]["lons"] for code in us_states]
    state_ys = [us_states[code]["lats"] for code in us_states]
    #transform/reproject coordinates for Bokeh
    prj_wgs = Proj(init='epsg:4326')
    prj_itm = Proj(init='EPSG:3857')
    a1 = []
    b1 = []
    a = []
    b = []
    for j in range(0, len(state_xs)):
        for i in range(0,len(state_xs[j])):
            a_a,b_b = transform(prj_wgs, prj_itm, state_xs[j][i], state_ys[j][i])
            a1.append(a_a)
            b1.append(b_b)
        a.append(a1)
        b.append(b1)
        a1 = []
        b1 = []

    return a, b

def map_carbon_emission(bus_info_and_emission, scenario_name,
                        color_coal='black', color_ng='purple',
                        label_coal="Coal: tons", label_ng="NG: tons", us_states = us_states):
    """Makes map of carbon emissions, color code by fuel type. Size/area
        indicates emissions.

    :param pandas.DataFrame bus_info_and_emission: info and emission of buses
        as returned by :func:`combine_bus_info_and_emission`.
    :param str scenario_name: name of scenario for labeling.
    :param str color_coal: color assigned for coal, default to black.
    :param str color_ng: color assigned for ng, default to purple.
    :param str label_coal: label for legend associated with coal.
    :param str label_ng: label for legend associated with ng.
    """
    bus_map = project_bus(bus_info_and_emission)
    us_states = us_states.data.copy()
    a,b = get_borders(us_states)
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
    #state borders
    p.patches(a, b, fill_alpha=0.0,
        line_color="black", line_width=2)
    #emissions circles
    p.circle('x', 'y', fill_color=color_coal, color=color_coal, alpha=0.25,
             size='coal', source=bus_source)
    p.circle('x', 'y', fill_color=color_ng, color=color_ng, alpha=0.25,
             size='ng', source=bus_source)

    # legend is custom: white square background and circles of different size
    # on top
    p_legend.square(1, [1, 3], fill_color='white', color='white', size=300)
    p_legend.square(1, [1, 3], fill_color='white', color='black',
                    size=(2000000/100)**0.5)
    p_legend.circle(1, y=np.repeat([1, 3], 3),
                    fill_color=np.repeat([color_coal, color_ng], 3),
                    color=np.repeat([color_coal, color_ng], 3), alpha=0.25,
                    size=[(5000000/500)**0.5, (2000000/500)**0.5,
                          (100000/500)**0.5]*2)
    source = ColumnDataSource(
        data=dict(x=[1, 1, 1, 0.5, 1, 1, 1, 0.5],
                  y=[.9, 1.1, 1.3, 1.55, 2.9, 3.1, 3.3, 3.55],
                  text=['100000', '2000000', '5000000', label_coal, '100000',
                        '2000000', '5000000', label_ng]))
    labels = LabelSet(x='x', y='y', text='text', source=source, level='glyph',
                      x_offset=0, y_offset=0, render_mode='css')
    p_legend.add_layout(labels)

    output_notebook()
    show(row(p_legend, p))


def map_carbon_emission_comparison(bus_info_and_emission_1,
                                   bus_info_and_emission_2):
    """Makes map of carbon emissions, color code by fuel type, size/area
        indicates emissions Also, returns data frame enclosing emission
        released by thermal generators.

    :param pandas.DataFrame bus_info_and_emission_1: info and emission of buses
        for 1st scenario as returned by :func:`combine_bus_info_and_emission`.
    :param pandas.DataFrame bus_info_and_emission_2: info and emission of buses
        for 2nd scenario as returned by :func:`combine_bus_info_and_emission`.
    :return: (pandas.DataFrame) -- comparison map indicating increase or
        decrease in emission
    """
    bus_map = bus_info_and_emission_1.merge(
        bus_info_and_emission_2, right_index=True, left_index=True, how='outer')

    bus_map.coal_x = bus_map.coal_x.fillna(0)
    bus_map.coal_y = bus_map.coal_y.fillna(0)
    bus_map.ng_x = bus_map.ng_x.fillna(0)
    bus_map.ng_y = bus_map.ng_y.fillna(0)

    bus_map['coal_dif'] = bus_map['coal_x'] - bus_map['coal_y']
    bus_map['ng_dif'] = bus_map['ng_x'] - bus_map['ng_y']
    bus_map['lon'] = bus_map['lon_x'].fillna(bus_map['lon_y'])
    bus_map['lat'] = bus_map['lat_x'].fillna(bus_map['lat_y'])
    bus_map["coal"] = 0
    bus_map["ng"] = 0
    bus_map.loc[bus_map.coal_dif > 0, ['coal']] = bus_map['coal_dif']
    bus_map.loc[bus_map.ng_dif > 0, ['coal']] = bus_map['ng_dif']

    bus_map.loc[bus_map.coal_dif < 0, ['ng']] = abs(bus_map['coal_dif'])
    bus_map.loc[bus_map.ng_dif < 0, ['ng']] = abs(bus_map['ng_dif'])

    map_carbon_emission(bus_map, "compare", "green", "red",
                        "Less: tons", "More: tons")

    return bus_map


def combine_bus_info_and_emission(bus_info, carbon_by_bus):
    """Builds data frame needed for plotting carbon emitted by thermal
        generators.

    :param pandas.DataFrame bus_info: bus data frame.
    :param dict carbon_by_bus: keys are fuel type and values is a dictionary
        where keys and values are the bus id and emission, respectively. This is
        returned :func:`postreise.analyze.generation.carbon.summarize_carbon_by_bus`.
    :return: (*pandas.DataFrame*) -- combined data frame.
    """

    bus_of_interest = bus_info.loc[pd.DataFrame.from_dict(carbon_by_bus).index]
    bus_info_and_emission = bus_of_interest.merge(
        pd.DataFrame.from_dict(carbon_by_bus), right_index=True,
        left_index=True)

    return bus_info_and_emission
