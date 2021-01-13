import numpy as np
from powersimdata.utility.helpers import _check_import
from pyproj import Transformer


def project_branch(branch):
    """Projects branches on new coordinates system.

    :param pandas.DataFrame branch: branch data frame.
    :return: (*pandas.DataFrame*) -- projected branch data frame.
    """
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")

    from_lat, from_lon = branch.from_lat.to_numpy(), branch.from_lon.to_numpy()
    from_x, from_y = transformer.transform(from_lat, from_lon)
    to_lat, to_lon = branch.to_lat.to_numpy(), branch.to_lon.to_numpy()
    to_x, to_y = transformer.transform(to_lat, to_lon)

    new_columns = {
        "from_x": from_x,
        "from_y": from_y,
        "to_x": to_x,
        "to_y": to_y,
    }
    branch_map = branch.assign(**new_columns)

    return branch_map


def project_bus(bus):
    """Projects buses on new coordinates system.

    :param pandas.DataFrame bus: bus data frame.
    :return: (*pandas.DataFrame*) -- projected bus data frame.
    """
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")

    lat, lon = bus.lat.to_numpy(), bus.lon.to_numpy()
    x, y = transformer.transform(lat, lon)
    bus_map = bus.assign(x=x, y=y)

    return bus_map


def project_borders(us_states_dat, state_list=None):
    """Prepares US state borders data for use on the map.

    :param dict us_states_dat: keys are state abbrevs, values are dicts with keys of
        {"lats", "lons"}, values of coordinates.
    :param iterable state_list: abbrevs of states to project, defaults to the keys of
        us_states_dat minus AK, HI, DC, & PR.
    :return: (*tuple*) -- reprojected coordinates for use on map.
    """
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    if state_list is None:
        state_list = set(us_states_dat.keys()) - {"AK", "HI", "DC", "PR"}
    state_xys = [
        transformer.transform(us_states_dat[s]["lats"], us_states_dat[s]["lons"])
        for s in state_list
    ]
    all_state_xs, all_state_ys = zip(*state_xys)

    return all_state_xs, all_state_ys


def convert_shapefile_to_latlon_dict(filename, key):
    """Converts a shapefile to a dictionary of lat/lon data.

    :param str filename: the location of the shapefile to interpret.
    :param str key: the shapefile column values used as dictionary keys.
    :return: (*dict*) -- dictionary with keys from the specified shapefile column,
        values are dict with keys of {"lat", "lon"}, values are coordinates, padded by
        nan values to indicate the end of each polygon before the start of the next one.
    :raises ValueError: if the specified key is not present in the shapefile, or the
        shapefile contains at least one polygon with a hole.
    """
    gpd = _check_import("geopandas")
    shapes = gpd.read_file(filename)
    if key not in shapes.columns:
        raise ValueError("key must be present in the columns of the shapefile")
    exploded_shapes = shapes.explode()
    if sum([len(g.interiors) for g in exploded_shapes.geometry]) > 0:
        raise ValueError("Cannot convert shapes with holes")
    keys_to_latlon_dicts = {}
    for i in shapes.index:
        latlon_arrays_list = [np.array(g.xy) for g in exploded_shapes.exterior.loc[i]]
        # Join individual arrays, padding inbetween with (nan, nan) coordinate point
        nanpadded_array = np.concatenate(
            [
                np.concatenate([s.T, np.empty((1, 2)) * np.nan])
                if i < (len(latlon_arrays_list) - 1)
                else s.T
                for i, s in enumerate(latlon_arrays_list)
            ]
        ).T
        latlon_dict = {"lats": nanpadded_array[1], "lons": nanpadded_array[0]}
        keys_to_latlon_dicts[shapes.loc[i, key]] = latlon_dict
    return keys_to_latlon_dicts
