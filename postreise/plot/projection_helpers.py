import copy
from pyproj import Proj, transform


def project_branch(branch):
    """Projects branches on new coordinates system.

    :param pandas.DataFrame branch: branch data frame.
    :return: (*pandas.DataFrame*) -- projected branch data frame.
    """
    branch_map = copy.deepcopy(branch)

    r_from = branch[["from_lon", "from_lat"]].apply(_wgs2itm, axis=1)
    branch_map["from_x"] = r_from.apply(lambda x: x[0])
    branch_map["from_y"] = r_from.apply(lambda x: x[1])

    r_to = branch[["to_lon", "to_lat"]].apply(_wgs2itm, axis=1)
    branch_map["to_x"] = r_to.apply(lambda x: x[0])
    branch_map["to_y"] = r_to.apply(lambda x: x[1])

    return branch_map


def project_bus(bus):
    """Projects buses on new coordinates system.

    :param pandas.DataFrame bus: bus data frame.
    :return: (*pandas.DataFrame*) -- projected bus data frame.
    """
    bus_map = copy.deepcopy(bus)

    r_from = bus[["lon", "lat"]].apply(_wgs2itm, axis=1)
    bus_map["x"] = r_from.apply(lambda x: x[0])
    bus_map["y"] = r_from.apply(lambda x: x[1])

    return bus_map


def _wgs2itm(x_lon_lat):
    """Convert WGS coordinates system to ITM coordinates system.

    :param pandas.DataFrame x_lon_lat: first column is longitude, second column
        is latitude, in WGS coordinates system.
    :return: (*list*) -- first elements is longitude, second element is latitude
        in the ITM coordinates system.
    """
    prj_wgs = Proj(init="epsg:4326")
    prj_itm = Proj(init="EPSG:3857")
    x, y = transform(prj_wgs, prj_itm, x_lon_lat[0], x_lon_lat[1])
    r = [x, y]

    return r
