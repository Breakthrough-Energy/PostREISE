#import general functions
import pandas as pd
import numpy as np

#import mapping functions
from bokeh.plotting import show, figure
from pyproj import Proj, transform
from bokeh.tile_providers import get_provider, Vendors
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, LabelSet
from matplotlib import pyplot as plt
from bokeh.layouts import row

def makemap_carbon(bus_map, scenario_name, color1 = 'black', 
                   color2 = 'purple', label1 = "Coal: tons", 
                   label2 = "NG: tons"):
    """Make map showing carbon emissions, color coded by fuel type, size indicates emissions (area)
    :param: grid bus object with coordinates for bus, df
    :param carbon_dict: coal and ng emissions by bus and type dictionary
    :return: map
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
    
    p_legend = figure(  x_axis_location=None, 
                      y_axis_location=None, toolbar_location=None,
                      plot_width=200, plot_height=400, 
                     y_range=(0, 4),
                      x_range=( 0, 2))

    p.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))

    p.circle('x','y', fill_color=color1, 
             color=color1,
             alpha=0.25, size='coal',
             source = bus_source)
    
    p.circle('x','y',
             fill_color=color2, 
             color=color2,
             alpha=0.25, 
             size='ng',
             source = bus_source)

    #legend is custom: white square background and circles of different size on top
    
    p_legend.square(1, [1, 3],
             fill_color='white', color='white', 
             size=300)
    
    p_legend.square(1, [1, 3],
             fill_color='white', color='black', 
             size=(2000000/100)**0.5)

    
    p_legend.circle(1, y = np.repeat([1,3],3),
             fill_color = np.repeat([color1, color2],3), 
             color = np.repeat([color1, color2],3), alpha = 0.25, 
             size = [(5000000/500)**0.5, (2000000/500)**0.5, (100000/500)**0.5]*2)
 
    source = ColumnDataSource(
        data=dict(x=[1,1,1,0.5,1,1,1,0.5],
                  y= [.9, 1.1, 1.3, 1.55, 2.9,3.1, 3.3, 3.55],
                  text=['100000', '2000000','5000000', 
                        label1, '100000', '2000000','5000000', label2]))   
    
    source1 = ColumnDataSource(
        data=dict(x=[10]*8,
                  y= [10]*8,
                  text=['100000', '2000000','5000000', 
                        label1, '100000', '2000000','5000000', label2]))   
    
    labels = LabelSet(x = 'x', y = 'y',
                      text = 'text',source = source, level = 'glyph', 
                      x_offset=0, y_offset=0, render_mode='css')

    
    p_legend.add_layout(labels)

    #p.add_layout(legend)
    output_notebook()
    show(row(p_legend, p))

    return 
    
def makemap_carbon_compare(gridbus, carbon_dictionary,carbon_dictionary2, scenario_name1, scenario_name2):
    bus_map1 = make_busmap(gridbus, carbon_dictionary)
    bus_map2 = make_busmap(gridbus, carbon_dictionary2)
    makemap_carbon(bus_map1,scenario_name1)
    makemap_carbon(bus_map2,scenario_name2)

    bus_map_merge = bus_map1.merge(bus_map2, right_index = True, left_index = True, how = 'outer' )
    bus_map_merge.coal_x = bus_map_merge.coal_x.fillna(0)
    bus_map_merge.coal_y = bus_map_merge.coal_y.fillna(0)
    bus_map_merge.ng_x = bus_map_merge.ng_x.fillna(0)
    bus_map_merge.ng_y = bus_map_merge.ng_y.fillna(0)

    bus_map_merge['coal_dif'] = bus_map_merge['coal_x'] - bus_map_merge['coal_y']
    bus_map_merge['ng_dif'] = bus_map_merge['ng_x'] - bus_map_merge['ng_y']
    bus_map_merge['x'] = bus_map_merge['x_x'].fillna(bus_map_merge['x_y'])
    bus_map_merge['y'] = bus_map_merge['y_x'].fillna(bus_map_merge['y_y'])
    bus_map_merge["coal"] = 0
    bus_map_merge["ng"] = 0
    bus_map_merge.loc[bus_map_merge.coal_dif >0, ['coal']] = bus_map_merge['coal_dif']; bus_map_merge
    bus_map_merge.loc[bus_map_merge.ng_dif >0, ['coal']] = bus_map_merge['ng_dif']; bus_map_merge  
    
    bus_map_merge.loc[bus_map_merge.coal_dif <0, ['ng']] = abs(bus_map_merge['coal_dif']); bus_map_merge
    bus_map_merge.loc[bus_map_merge.ng_dif <0, ['ng']] = abs(bus_map_merge['ng_dif']); bus_map_merge  
    
    makemap_carbon(bus_map_merge,"compare","green","red","Less: tons", "More: tons")
    
    return bus_map_merge
