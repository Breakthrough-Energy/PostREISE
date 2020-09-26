from postreise.analyze.check import (
    _check_scenario_is_in_analyze_state,
    _check_resources_are_in_grid_and_format,
    _check_number_hours_to_analyze,
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
