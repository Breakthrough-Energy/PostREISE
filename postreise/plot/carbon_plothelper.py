import pandas as pd
from pyproj import Proj, transform


def projection_fields(branch_map):
    """Makes projection fields to be used for mapping.

    :param pandas.DataFrame branch_map: data frame with branches coordinates.
    :return: (*pandas.DataFrame*) -- version with coord for Bokeh
    """
    r_from = branch_map[['from_lon', 'from_lat']].apply(_wgs2itm, axis=1)
    branch_map['from_x'] = r_from.apply(lambda x: x[0])
    branch_map['from_y'] = r_from.apply(lambda x: x[1])

    r_to = branch_map[['to_lon', 'to_lat']].apply(_wgs2itm, axis=1)
    branch_map['to_x'] = r_to.apply(lambda x: x[0])
    branch_map['to_y'] = r_to.apply(lambda x: x[1])

    return branch_map


def _wgs2itm(x_lon_lat):
    """Convert WGS coordinates system to ITM coordinates system.

    :param pandas.DataFrame x_lon_lat: first column is longitude, second column
        is latitude, in WGS coordinates system.
    :return: (*pandas.DataFrame) -- first column is longitude, second column
        is latitude in the ITM coordinates system.
    """
    prj_wgs = Proj(init='epsg:4326')
    prj_itm = Proj(init='EPSG:3857')
    x, y = transform(prj_wgs, prj_itm, x_lon_lat[0], x_lon_lat[1])
    r = [x, y]
    return r


def make_emitter_map(bus_info, emitter):
    """Builds a data frame needed for plotting carbon emitted by thermal
        generators.

    :param pandas.DataFrame bus_info: grid with coordinates for buses.
    :param dict emitter: buses and carbon emission per type (natural
        gas or coal generators).
    :return: (*pandas.DataFrame*) -- index is bus id. Columns are coordinates
        and carbon emitted.
    """

    bus_emitter = bus_info.loc[pd.DataFrame.from_dict(emitter).index]
    bus_map = bus_emitter.merge(pd.DataFrame.from_dict(emitter),
                                right_index=True, left_index=True)

    r_from = bus_map[['lon', 'lat']].apply(_wgs2itm, axis=1)
    bus_map['x'] = r_from.apply(lambda x: x[0])
    bus_map['y'] = r_from.apply(lambda x: x[1])

    return bus_map
