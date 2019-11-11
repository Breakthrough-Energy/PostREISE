import geopy.distance


def great_circle_distance(x):
    """Calculates distance between two sites.

    :param pandas.dataFrame x: start and end point coordinates of branches.
    :return: (*float*) -- length of branch (in km.).
    """
    site_coords = (x.from_lat, x.from_lon)
    place2_coords = (x.to_lat, x.to_lon)
    return geopy.distance.vincenty(site_coords, place2_coords).km
