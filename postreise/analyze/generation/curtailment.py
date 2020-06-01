import pandas as pd

from postreise.analyze.helpers import \
    summarize_plant_to_bus, summarize_plant_to_location
from powersimdata.scenario.scenario import Scenario
from powersimdata.scenario.analyze import Analyze


# What is the name of the function in scenario.state to get the profiles?
_resource_func = {
    'solar': 'get_solar',
    'wind': 'get_wind',
    'wind_offshore': 'get_wind',
    }


def _check_scenario(scenario):
    """Ensure that the input is a Scenario in Analyze state.
    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    """
    if not isinstance(scenario, Scenario):
        raise TypeError('scenario must be a Scenario object')
    if not isinstance(scenario.state, Analyze):
        raise ValueError('scenario.state must be Analyze')


def _check_resources(resources):
    """Ensure that the input is a tuple/list/set of strs in _resource_func.
    :param tuple/list/set resources: list of resources to analyze.
    """
    if not isinstance(resources, (tuple, list, set)):
        raise TypeError('resources must be iterable (tuple, list, set)')
    for r in resources:
        if not isinstance(r, str):
            raise TypeError('each resource must be a str')
        if r not in _resource_func.keys():
            err_msg = 'resource {0} not found in list of resource functions.'
            err_msg += ' Allowable: ' + ', '.join(_resource_func.keys())
            raise ValueError(err_msg)


def _check_resource_in_scenario(resources, scenario):
    """Ensure that each item in resources is represented in at least one
    generator in scenario grid.
    :param tuple/list/set resources: list of resources to analyze.
    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*None*).
    """
    gentypes_in_grid = set(scenario.state.get_grid().plant['type'].unique())
    if not set(resources) <= gentypes_in_grid:
        err_msg = 'Curtailment requested for resources not in scenario.'
        err_msg += ' Requested: ' + ', '.join(resources)
        err_msg += '. Scenario: ' + ', '.join(gentypes_in_grid)
        raise ValueError(err_msg)


def _check_curtailment_in_grid(curtailment, grid):
    """Ensure that curtailment is a dict of dataframes, and that each key is
    represented in at least one generator in grid.
    :param dict curtailment: keys are resources, values are pandas.DataFrame.
    :param powersimdata.input.grid.Grid grid: Grid instance.
    :return: (*None*).
    """
    if not isinstance(curtailment, dict):
        raise TypeError('curtailment must be a dict')
    for k, v in curtailment.items():
        if not isinstance(k, str):
            raise TypeError('curtailment keys must be str')
        if not isinstance(v, pd.DataFrame):
            raise TypeError('curtailment values must be pandas.DataFrame')
    gentypes_in_grid = grid.plant['type'].unique()
    if list(curtailment.keys()) not in gentypes_in_grid:
        err_msg = 'Curtailment has types not present in grid.plant DataFrame.'
        err_msg += ' Curtailment: ' + ', '.join(curtailment.keys())
        err_msg += '. Plant: ' + ', '.join(gentypes_in_grid)
        raise ValueError(err_msg)


def calculate_curtailment_time_series(scenario, resources=None):
    """Calculate a time series of curtailment for a set of valid resources.
    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param tuple/list/set resources: names of resources to analyze.
    :return: (*dict*) -- keys are resources, values are pandas.DataFrames
    indexed by (datetime, plant) where plant is only plants of matching type.
    """
    if resources is None:
        resources = ('solar', 'wind', 'wind_offshore')
    _check_scenario(scenario)
    _check_resources(resources)
    _check_resource_in_scenario(resources, scenario)

    # Get input dataframes from scenario object
    pg = scenario.state.get_pg()
    grid = scenario.state.get_grid()
    profile_functions = {_resource_func[r] for r in resources}
    relevant_profiles = pd.concat(
        [getattr(scenario.state, p)() for p in profile_functions], axis=1)

    # Calculate differences for each resource
    curtailment = {}
    for r in resources:
        ren_plants = grid.plant.groupby('type').get_group(r).index
        curtailment[r] = relevant_profiles[ren_plants] - pg[ren_plants]

    return curtailment


def calculate_curtailment_percentage(scenario, resources=('solar', 'wind')):
    """Calculate scenario-long average curtailment for selected resources.
    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param tuple/list/set resources: names of resources to analyze.
    :return: (*float*) -- Average curtailment fraction over the scenario.
    """
    _check_scenario(scenario)
    _check_resources(resources)
    _check_resource_in_scenario(resources, scenario)

    curtailment = calculate_curtailment_time_series(scenario)
    rentype_total_curtailment = {
        r: curtailment[r].sum().sum() for r in resources}

    rentype_total_potential = {
        r: getattr(scenario.state, _resource_func[r])().sum().sum()
        for r in resources}

    total_curtailment = (
        sum(v for v in rentype_total_curtailment.values())
        / sum(v for v in rentype_total_potential.values()))

    return total_curtailment


def summarize_curtailment_by_bus(curtailment, grid):
    """Calculate total curtailment for selected resources, by bus.
    :param dict curtailment: keys are resources, values are pandas.DataFrame.
    :param powersimdata.input.grid.Grid grid: Grid instance.
    :return: (*dict*) -- keys are resources, values are dict of
        (bus: curtailment vector).
    """
    _check_curtailment_in_grid(curtailment, grid)

    bus_curtailment = {
        ren_type: summarize_plant_to_bus(curtailment_df, grid).sum().to_dict()
        for ren_type, curtailment_df in curtailment.items()}

    return bus_curtailment


def summarize_curtailment_by_location(curtailment, grid):
    """Calculate total curtailment for selected resources, by location.
    :param dict curtailment: keys are resources, values are pandas.DataFrame.
    :param powersimdata.input.grid.Grid grid: Grid instance.
    :return: (*dict*) -- keys are resources, values are dict of
        ((lat, lon): curtailment vector).
    """
    _check_curtailment_in_grid(curtailment, grid)

    location_curtailment = {
        ren_type: summarize_plant_to_location(
            curtailment_df, grid).sum().to_dict()
        for ren_type, curtailment_df in curtailment.items()}

    return location_curtailment
