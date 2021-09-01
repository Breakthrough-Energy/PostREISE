import numpy as np
from powersimdata.input.check import (
    _check_number_hours_to_analyze,
    _check_resources_are_in_grid_and_format,
)
from powersimdata.input.helpers import (
    get_plant_id_for_resources_in_area,
    get_storage_id_in_area,
)
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state


def calculate_NLDC(scenario, resources, hours=100):  # noqa: N802
    """Calculate the capacity value of a class of resources by comparing the
    mean of the top N hour of absolute demand to the mean of the top N hours of
    net demand. NLDC = 'Net Load Duration Curve'.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str/list/tuple/set resources: one or more resources to analyze.
    :param int hours: number of hours to analyze.
    :return: (*float*) -- difference between peak demand and peak net demand.
    """
    _check_scenario_is_in_analyze_state(scenario)
    grid = scenario.state.get_grid()
    resources = _check_resources_are_in_grid_and_format(resources, grid)
    _check_number_hours_to_analyze(scenario, hours)

    # Then calculate capacity value
    total_demand = scenario.state.get_demand().sum(axis=1)
    prev_peak = total_demand.sort_values(ascending=False).head(hours).mean()
    plant_groupby = grid.plant.groupby("type")
    plant_indices = sum(
        [plant_groupby.get_group(r).index.tolist() for r in resources], []
    )
    resource_generation = scenario.state.get_pg()[plant_indices].sum(axis=1)
    net_demand = total_demand - resource_generation
    net_peak = net_demand.sort_values(ascending=False).head(hours).mean()
    return prev_peak - net_peak


def calculate_net_load_peak(scenario, resources, hours=100):
    """Calculate the capacity value of a class of resources by averaging the
    power generated in the top N hours of net load peak.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str/list/tuple/set resources: one or more resources to analyze.
    :param int hours: number of hours to analyze.
    :return: (*float*) -- resource capacity during hours of peak net demand.
    """
    _check_scenario_is_in_analyze_state(scenario)
    grid = scenario.state.get_grid()
    resources = _check_resources_are_in_grid_and_format(resources, grid)
    _check_number_hours_to_analyze(scenario, hours)

    # Then calculate capacity value
    total_demand = scenario.state.get_demand().sum(axis=1)
    plant_groupby = grid.plant.groupby("type")
    plant_indices = sum(
        [plant_groupby.get_group(r).index.tolist() for r in resources], []
    )
    resource_generation = scenario.state.get_pg()[plant_indices].sum(axis=1)
    net_demand = total_demand - resource_generation
    top_hours = net_demand.sort_values(ascending=False).head(hours).index
    return resource_generation[top_hours].mean()


def get_capacity_by_resources(scenario, area, resources, area_type=None):
    """Get the total nameplate capacity for generator type(s) in an area

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str/list resources: one or a list of resources
    :param str area_type: one of *'loadzone'*, *'state'*, *'state_abbr'*,
        *'interconnect'*
    :return: (*pandas.Series*) -- index: resources, column: total nameplate Pmax
        capacity
    """
    plant_id = get_plant_id_for_resources_in_area(
        scenario, area, resources, area_type=area_type
    )
    grid = scenario.state.get_grid()

    return grid.plant.loc[plant_id].groupby("type")["Pmax"].sum()


def get_storage_capacity(scenario, area, area_type=None):
    """Get total storage nameplate capacity in an area.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str area_type: one of *'loadzone'*, *'state'*, *'state_abbr'*,
        *'interconnect'*
    :return: (*float*) -- total storage capacity value
    """
    grid = scenario.state.get_grid()
    storage_id = get_storage_id_in_area(scenario, area, area_type)

    return grid.storage["gen"].loc[storage_id].Pmax.sum()


def sum_capacity_by_type_zone(scenario):
    """Get total capacity for each generator type and load zone combination.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- index: generator type, column: load zone, value:
        total capacity.
    """
    grid = scenario.state.get_grid()
    plant = grid.plant

    return plant.groupby(["type", "zone_id"])["Pmax"].sum().unstack().fillna(0)


def get_capacity_factor_time_series(scenario, area, resources, area_type=None):
    """Get the hourly capacity factor of each generator fueled by resource(s) in an
    area.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str/list resources: one or a list of resources
    :param str area_type: one of *'loadzone'*, *'state'*, *'state_abbr'*,
        *'interconnect'*
    :return: (*pandas.DataFrame*) -- index: timestamps, column: plant ids,
        value: capacity factors
    """
    _check_scenario_is_in_analyze_state(scenario)
    plant_id = get_plant_id_for_resources_in_area(
        scenario, area, resources, area_type=area_type
    )
    pg = scenario.state.get_pg()[plant_id]
    capacity = scenario.state.get_grid().plant.loc[plant_id, "Pmax"]
    cf = (pg / capacity).replace(np.inf, 0).clip(0, 1)
    return cf
