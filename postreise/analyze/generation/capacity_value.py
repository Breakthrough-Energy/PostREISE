from postreise.analyze.check import (
    _check_number_hours_to_analyze,
    _check_resources_are_in_grid_and_format,
    _check_scenario_is_in_analyze_state,
)
from postreise.analyze.helpers import (
    get_plant_id_for_resources_in_area,
    get_storage_id_in_area,
)


def calculate_NLDC(scenario, resources, hours=100):
    """Calculate the capacity value of a class of resources by comparing the
    mean of the top N hour of absolute demand to the mean of the top N hours of
    net demand. NLDC = 'Net Load Duration Curve'.

    :param powersimdata.scenario.scenario.Scenario scenario: analyzed scenario.
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

    :param powersimdata.scenario.scenario.Scenario scenario: analyzed scenario.
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
    """Get total capacity value of certain resources in the specific area of a
    scenario.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of: *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str/list resources: one or a list of resources
    :param str area_type: one of: *'loadzone'*, *'state'*,
        *'state_abbr'*, *'interconnect'*
    :return: (*pandas.Series*) -- index: resources, column: total capacity values
    """
    plant_id = get_plant_id_for_resources_in_area(
        scenario, area, resources, area_type=area_type
    )
    grid = scenario.state.get_grid()

    return grid.plant.loc[plant_id].groupby("type")["Pmax"].sum()


def get_storage_capacity(scenario, area, area_type=None):
    """Get total storage capacity value in the specific area of a scenario.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of: *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str area_type: one of: *'loadzone'*, *'state'*,
        *'state_abbr'*, *'interconnect'*
    :return: (*float*) -- total storage capacity value
    """
    grid = scenario.state.get_grid()
    storage_id = get_storage_id_in_area(scenario, area, area_type)

    return sum(grid.storage["gen"].loc[storage_id].Pmax.values)
