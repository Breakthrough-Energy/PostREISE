from bokeh.plotting import figure, show
import matplotlib
import matplotlib.cm as cm
import pandas as pd
from pyproj import Proj
from pyproj import transform
from bokeh.tile_providers import get_provider, Vendors
from bokeh.models import CustomJS, ColumnDataSource, ColorBar
from bokeh.palettes import Spectral6
from bokeh.transform import linear_cmap

get_provider(Vendors.CARTODBPOSITRON)

def projection_fields(branch_map):
    """Makes projection fields to be used for Bokeh mapping
    :param pandas dataframe branch_map: dataframe with branches coord
    :return: dataframe version with coord for Bokeh
    """
    r_from = branch_map[['from_lon', 'from_lat']].apply(reproject_wgs_to_itm, axis=1)
    branch_map['from_x'] = r_from.apply(lambda x: x[0])
    branch_map['from_y'] = r_from.apply(lambda x: x[1])
    r_to = branch_map[['to_lon', 'to_lat']].apply(reproject_wgs_to_itm, axis=1)
    branch_map['to_x'] = r_to.apply(lambda x: x[0])
    branch_map['to_y'] = r_to.apply(lambda x: x[1])
    return branch_map


def reproject_wgs_to_itm(x_lon_lat):
    """Reprojects from WGS coord system to ITM coord system, used for Bokeh mapping
    :param pandas dataframe x_lon_lat: dataframe with first col lon and second col lat, in WGS
    :return: dataframe with first col lon and seocnd col lat in ITM
    """
    prj_wgs = Proj(init='epsg:4326')
    prj_itm = Proj(init='EPSG:3857')
    x, y = transform(prj_wgs, prj_itm, x_lon_lat[0], x_lon_lat[1])
    r = [x, y]
    return r

def makemap(congestion, branch):
    """Make map showing congestion, with green dot for transformer winding, blue dot transformer, and lines for
        congested branches with varying color and thickness indicating degeree of congestion

    :param congestion:
    :param branch:
    :return: map
    """
    print("Mapping")
    branch = branch.loc[congestion.index]
    lines = congestion.loc[(congestion['branch_device_type'] == 'Line')]
    risk = lines['risk']
    congestion = congestion.drop(['branch_device_type'], axis=1)
    branch_map = pd.concat([branch, congestion], axis=1)

    minima = risk.min()
    maxima = risk.max()

    mapper1 = linear_cmap(field_name='risk', palette=Spectral6,
                          low=minima,
                          high=maxima)

    color_bar = ColorBar(color_mapper=mapper1['transform'], width=8, location=(0, 0), title="risk")

    norm = matplotlib.colors.Normalize(vmin=minima, vmax=maxima, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.jet)
    mapper.set_array([])

    projection_fields(branch_map)

    multi_line_source = ColumnDataSource({
        'xs': branch_map[['from_x', 'to_x']].values.tolist(),
        'ys': branch_map[['from_y', 'to_y']].values.tolist(),
        'risk': branch_map.risk
    })

    # Set up figure
    tools: str = "pan,wheel_zoom,reset,hover,save"

    p = figure(title="Western Interconnect", tools=tools, x_axis_location=None, y_axis_location=None,
               plot_width=800, plot_height=800)
    p.add_layout(color_bar, 'right')
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))
    p.multi_line('xs',
                 'ys',
                 color=mapper1,
                 line_width=8,
                 source=multi_line_source)

    show(p)
    return


def makemap_all(cong_df, branch):
    """Make map showing congestion, with green dot for transformer winding, blue dot transformer, and lines for
        congested branches with varying color and thickness indicating degeree of congestion

    :param cong_df: congestion datafame
    :param branch: branches dataframe
    :return: map, shows all lines and degree of congestion (median)
    """
    print("Mapping all lines")
    cong_median = cong_df.median()
    branch_map = pd.concat([branch, cong_median], axis=1)
    branch_map.rename(columns={0: 'medianval'}, inplace=True)
    lines = branch_map.loc[(branch_map['branch_device_type'] == 'Line')]
    medianval = lines.medianval

    minima = medianval.min()
    maxima = medianval.max()

    mapper1 = linear_cmap(field_name='medianval', palette=Spectral6,
                          low=minima,
                          high=maxima)

    color_bar = ColorBar(color_mapper=mapper1['transform'], width=8, location=(0, 0), title="median utilization")

    norm = matplotlib.colors.Normalize(vmin=minima, vmax=maxima, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.jet)
    mapper.set_array([])


    multi_line_source = ColumnDataSource({
        'xs': branch_map[['from_x', 'to_x']].values.tolist(),
        'ys': branch_map[['from_y', 'to_y']].values.tolist(),
        'medianval': branch_map.medianval
    })

    # Set up figure
    tools: str = "pan,wheel_zoom,reset,hover,save"

    p = figure(title="Western Interconnect", tools=tools, x_axis_location=None, y_axis_location=None,
               plot_width=800, plot_height=800)
    p.add_layout(color_bar, 'right')
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))
    p.multi_line('xs',
                 'ys',
                 color=mapper1,
                 line_width=8,
                 source=multi_line_source)
    show(p)
    return


def makemap_binding(cong_df, branch):
    """Make map showing congestion, with green dot for transformer winding, blue dot transformer, and lines for
        congested branches with varying color and thickness indicating degeree of congestion

    :param cong_df: congestion datafame
    :param branch: branches dataframe
    :return: map, shows all lines and degree of congestion (median)
    """
    print("Mapping binding")
    cong_max = cong_df.max()
    branch_map = pd.concat([branch, cong_max], axis=1)
    branch_map.rename(columns={0: 'maxval'}, inplace=True)
    branch_map = branch_map.loc[(branch_map['maxval'] >= 1)]

    multi_line_source = ColumnDataSource({
        'xs': branch_map[['from_x', 'to_x']].values.tolist(),
        'ys': branch_map[['from_y', 'to_y']].values.tolist()
    })

    # Set up figure
    tools: str = "pan,wheel_zoom,reset,hover,save"

    p = figure(title="Binding Incidents", tools=tools, x_axis_location=None, y_axis_location=None,
               plot_width=800, plot_height=800)
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))
    p.multi_line('xs',
                 'ys',
                 line_width=8,
                 source=multi_line_source)
    transformers = branch_map.loc[(branch_map['branch_device_type'] == 'Transformer')]
    transformerwinding = branch_map.loc[(branch_map['branch_device_type'] == 'TransformerWinding')]
    p.circle(transformers['from_x'],
             transformers['from_y'],
             color="blue", alpha=0.6, size=10)
    p.circle(transformerwinding['from_x'],
             transformerwinding['from_y'],
             color="green", size=10, alpha=0.6)
    binding_df = branch_map
    show(p)
    return binding_df
