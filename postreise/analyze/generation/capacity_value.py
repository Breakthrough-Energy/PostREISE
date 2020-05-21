from powersimdata.scenario.scenario import Scenario
from powersimdata.scenario.analyze import Analyze


def calculate_capacity_value(scenario, resources, hours=100):
    """Calculate the contribution of a class or resources to reducing mean net
    demand in N hours of highest net demand.
    
    :param powersimdata.scenario.scenario.Scenario scenario: analyzed scenario.
    :param (str/list/tuple/set) resources: one or more resources to analyze.
    :param int hours: number of hours to analyze.
    :raises TypeError: if scenario is not a Scenario, resources is not one of
        str or list/tuple/set of str's, or hours is not an int.
    :raises ValueError: if scenario is not in Analyze state, if hours is
        non-positive or greater than the length of the scenario, if resources
        is empty, or not all resources are present in the grid.
    :return: (*float*) -- difference between peak demand and peak net demand.
    """
    # Check scenario
    if not isinstance(scenario, Scenario):
        raise TypeError('scenario must be a Scenario object')
    if not isinstance(scenario.state, Analyze):
        raise ValueError('scenario must be in Analyze state')
    # Check resources
    if isinstance(resources, str):
        resources = {resources}
    elif isinstance(resources, (list, set, tuple)):
        if not all([isinstance(r, str) for r in resources]):
            raise TypeError('all resources must be str')
        resources = set(resources)
    else:
        raise TypeError('resources must be str or list/tuple/set of str')
    if len(resources) == 0:
        raise ValueError('resources must be nonempty')
    grid = scenario.state.get_grid()
    valid_resources = set(grid.plant.type.unique())
    if not resources <= valid_resources:
        difference = resources - valid_resources
        raise ValueError('Invalid resource(s): %s' % ' | '.join(difference))
    # Check hours
    if not isinstance(hours, int):
        raise TypeError('hours must be an int')
    if hours < 1:
        raise ValueError('hours must be positive')
    total_demand = scenario.state.get_demand().sum(axis=1)
    if hours > len(total_demand):
        raise ValueError('hours must not be greater than simulation length')

    # Then calculate capacity value
    plant_groupby = grid.plant.groupby('type')
    plant_indices = sum(
        [plant_groupby.get_group(r).index.tolist() for r in resources], [])
    resource_generation = scenario.state.get_pg()[plant_indices].sum(axis=1)
    prev_peak = total_demand.sort_values(ascending=False).head(hours).mean()
    net_demand = total_demand - resource_generation
    net_peak = net_demand.sort_values(ascending=False).head(hours).mean()
    return prev_peak - net_peak
