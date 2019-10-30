from math import radians, cos, sin, asin, sqrt

from powersimdata.input.grid import Grid


def haversine(point1, point2):
    """Given two lat/long pairs, return distance in miles.

    :param tuple (number, number) point1: first point, (lat, long) in degrees.
    :param tuple (number, number) point2: second point, (lat, long) in degrees.

    :return: distance in miles, float

    """

    _AVG_EARTH_RADIUS_MILES = 3958.7613

    # unpack latitude/longitude
    lat1, lng1 = point1
    lat2, lng2 = point2

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(radians, (lat1, lng1, lat2, lng2))

    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = 2 * _AVG_EARTH_RADIUS_MILES * asin(sqrt(
        sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2))

    return d


def calculate_mw_miles(scenario):
    """Given a Scenario object, calculate the number of upgraded lines and
    transformers, and the total upgrade quantity (in MW and MW-miles).
    Currently only supports change_tables that specify branches, not zone_name.
    Currently lumps Transformer and TransformerWinding upgrades together.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    """

    original_grid = Grid(scenario.info['interconnect'].split('_'))
    ct = scenario.change_table.ct
    upgrades = _calculate_mw_miles(original_grid, ct)
    return upgrades


def _calculate_mw_miles(original_grid, ct):
    """Given a base grid and a change table, calculate the number of upgraded
    lines and transformers, and the total upgrade quantity (in MW & MW-miles).
    This function is separate from calculate_mw_miles() for testing purposes.
    Currently only supports change_tables that specify branches, not zone_name.
    Currently lumps Transformer and TransformerWinding upgrades together.

    :param powersimdata.input.grid original_grid: grid instance.
    :param powersimdata.input.change_table ct: change_table instance.

    :return: a dict of keys (types of upgrades) and values (floats/ints).
    """

    upgrade_categories = (
        'mw_miles', 'transformer_mw', 'num_lines', 'num_transformers')
    upgrades = {u: 0 for u in upgrade_categories}

    base_branch = original_grid.branch
    upgraded_branches = ct['branch']['branch_id']
    for b, v in upgraded_branches.items():
        # 'upgraded' capacity is v-1 because a scale of 1 = an upgrade of 0
        upgraded_capacity = base_branch.loc[b, 'rateA'] * (v-1)
        device_type = base_branch.loc[b, 'branch_device_type']
        if device_type == 'Line':
            from_coords = (
                base_branch.loc[b, 'from_lat'], base_branch.loc[b, 'from_lon'])
            to_coords = (
                base_branch.loc[b, 'to_lat'], base_branch.loc[b, 'to_lon'])
            addtl_mw_miles = (
                upgraded_capacity * haversine(from_coords, to_coords))
            upgrades['mw_miles'] += addtl_mw_miles
            upgrades['num_lines'] += 1
        elif device_type == 'Transformer':
            upgrades['transformer_mw'] += upgraded_capacity
            upgrades['num_transformers'] += 1
        elif device_type == 'TransformerWinding':
            upgrades['transformer_mw'] += upgraded_capacity
            upgrades['num_transformers'] += 1
        else:
            raise Exception('Unknown branch: ' + str(b))

    return upgrades
