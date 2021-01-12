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
        us_states_dat minus AK, HI, & DC.
    :return: (*tuple*) -- reprojected coordinates for use on map.
    """
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    if state_list is None:
        state_list = set(us_states_dat.keys()) - {"AK", "HI", "DC"}
    state_xys = [
        transformer.transform(us_states_dat[s]["lats"], us_states_dat[s]["lons"])
        for s in state_list
    ]
    all_state_xs, all_state_ys = zip(*state_xys)

    return all_state_xs, all_state_ys
