from postreise.analyze.generation.summarize import (
    get_generation_time_series_by_resources,
)


def get_demand_time_series(scenario, area, area_type=None):
    """Get time series demand in certain area of a scenario

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str area_type: one of *'loadzone'*, *'state'*, *'state_abbr'*,
        *'interconnect'*
    :return: (*pandas.Series*) -- time series of total demand, index: time stamps,
        column: demand values
    """
    grid = scenario.get_grid()
    loadzone_set = grid.model_immutables.area_to_loadzone(area, area_type=area_type)
    loadzone_id_set = {grid.zone2id[lz] for lz in loadzone_set if lz in grid.zone2id}

    return scenario.get_demand()[list(loadzone_id_set)].sum(axis=1)


def get_net_demand_time_series(scenario, area, area_type=None):
    """Get time series net demand in certain area of a scenario

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str area_type: one of *'loadzone'*, *'state'*, *'state_abbr'*,
        *'interconnect'*
    :return: (*pandas.Series*) -- time series of total demand, index: time stamps,
        column: net demand values
    """
    grid = scenario.get_grid()
    renewable_pg = get_generation_time_series_by_resources(
        scenario,
        area,
        grid.model_immutables.plants["renewable_resources"],
        area_type=area_type,
    )
    demand = get_demand_time_series(scenario, area, area_type=area_type)
    net_demand = demand - renewable_pg.sum(axis=1)

    return net_demand
