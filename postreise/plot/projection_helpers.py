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
