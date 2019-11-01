import pandas as pd
from pyproj import Proj, transform


def reproject_wgs_to_itm(x_lon_lat):
    """Reprojects from WGS coord system to ITM coord system, used for Bokeh mapping
    :param pandas.DataFrame x_lon_lat: first col lon and second col lat, in WGS
    :return pandas.DataFrame: first col lon and seocnd col lat in ITM
    """
    prj_wgs = Proj(init='epsg:4326')
    prj_itm = Proj(init='EPSG:3857')
    x, y = transform(prj_wgs, prj_itm, x_lon_lat[0], x_lon_lat[1])
    r = [x, y]
    return r


def make_busmap(gridbus, carbon_dictionary):
    """Merges grid dataframe with bus-carbon dataframe. Rerojects coordinates for Bokeh.
    :param pandas.DataFrame gridbus: grid with coordinates for buses
    :param dict carbon_dictionary: buses and carbon emissions per type; ng or coal.
    :return pandas.DataFrame bus_map: coordinates and carbon per bus
    """
    df = pd.DataFrame.from_dict(carbon_dictionary)
    bus = gridbus.loc[df.index]
    bus_map = bus.merge(df, right_index=True, left_index=True)

    r_from = bus_map[['lon', 'lat']].apply(reproject_wgs_to_itm, axis=1)
    bus_map['x'] = r_from.apply(lambda x: x[0])
    bus_map['y'] = r_from.apply(lambda x: x[1])

    return bus_map


def projection_field(branch_map):
    """Makes projection fields to be used for Bokeh mapping
    :param pandas.DataFrame branch_map: dataframe with branches coord
    :return pandas.DataFrame branch_map: dataframe version with coord for Bokeh
    """
    r_from = branch_map[['from_lon', 'from_lat']].apply(
        reproject_wgs_to_itm, axis=1)
    branch_map['from_x'] = r_from.apply(lambda x: x[0])
    branch_map['from_y'] = r_from.apply(lambda x: x[1])
    r_to = branch_map[['to_lon', 'to_lat']].apply(reproject_wgs_to_itm, axis=1)
    branch_map['to_x'] = r_to.apply(lambda x: x[0])
    branch_map['to_y'] = r_to.apply(lambda x: x[1])
    return branch_map
