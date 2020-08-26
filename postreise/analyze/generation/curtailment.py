import pandas as pd

from postreise.analyze.check import (
    _check_scenario_is_in_analyze_state,
    _check_grid,
    _check_resources_are_renewable_and_format,
    _check_resources_are_in_grid,
    _check_curtailment,
)
from postreise.analyze.helpers import (
    summarize_plant_to_bus,
    summarize_plant_to_location,
)
from powersimdata.network.usa_tamu.constants.plants import renewable_resources


# What is the name of the function in scenario.state to get the profiles?
# The set of keys to in dict defines the set of possible curtailment resources.
_resource_func = {
    "solar": "get_solar",
    "wind": "get_wind",
    "wind_offshore": "get_wind",
}


def calculate_curtailment_time_series(scenario, resources=None):
    """Calculate a time series of curtailment for a set of valid resources.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str/tuple/list/set resources: names of resources to analyze. Default is
        all resources which can be curtailed, defined in _resource_func.
    :return: (*dict*) -- keys are resources, values are pandas.DataFrames
    indexed by (datetime, plant) where plant is only plants of matching type.
    """
    _check_scenario_is_in_analyze_state(scenario)
    grid = scenario.state.get_grid()
    if resources is None:
        resources = renewable_resources
    else:
        resources = _check_resources_are_renewable_and_format(resources)
    _check_resources_are_in_grid(resources, grid)

    # Get input dataframes from scenario object
    pg = scenario.state.get_pg()
    profile_functions = {_resource_func[r] for r in resources}
    relevant_profiles = pd.concat(
        [getattr(scenario.state, p)() for p in profile_functions], axis=1
    )

    # Calculate differences for each resource
    curtailment = {}
    for r in resources:
        ren_plants = grid.plant.groupby("type").get_group(r).index
        curtailment[r] = relevant_profiles[ren_plants] - pg[ren_plants]

    return curtailment


def calculate_curtailment_percentage(scenario, resources=None):
    """Calculate scenario-long average curtailment for selected resources.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str/tuple/list/set resources: names of resources to analyze. Default is
        all resources which can be curtailed.
    :return: (*float*) -- Average curtailment fraction over the scenario.
    """
    _check_scenario_is_in_analyze_state(scenario)
    grid = scenario.state.get_grid()
    if resources is None:
        resources = renewable_resources
    else:
        resources = _check_resources_are_renewable_and_format(resources)
    _check_resources_are_in_grid(resources, grid)

    curtailment = calculate_curtailment_time_series(scenario, resources)
    rentype_total_curtailment = {r: curtailment[r].sum().sum() for r in resources}

    # Build a set of the profile methods we will call
    profile_methods = {_resource_func[r] for r in resources}
    # Build one mega-profile dataframe that contains all profiles of interest
    mega_profile = pd.concat([getattr(scenario.state, p)() for p in profile_methods])
    # Calculate total energy for each resource
    rentype_total_potential = mega_profile.groupby(grid.plant.type, axis=1).sum().sum()

    # Calculate curtailment percentage by dividing total curtailment by total potential
    curtailment_percentage = (
        sum(v for v in rentype_total_curtailment.values())
        / rentype_total_potential.loc[list(resources)].sum()
    )

    return curtailment_percentage


def summarize_curtailment_by_bus(curtailment, grid):
    """Calculate total curtailment for selected resources, by bus.

    :param dict curtailment: keys are resources, values are data frame.
    :param powersimdata.input.grid.Grid grid: Grid instance.
    :return: (*dict*) -- keys are resources, values are dict of
        (bus: curtailment vector).
    """
    _check_curtailment(curtailment, grid)

    bus_curtailment = {
        ren_type: summarize_plant_to_bus(curtailment_df, grid).sum().to_dict()
        for ren_type, curtailment_df in curtailment.items()
    }

    return bus_curtailment


def summarize_curtailment_by_location(curtailment, grid):
    """Calculate total curtailment for selected resources, by location.

    :param dict curtailment: keys are resources, values are data frame.
    :param powersimdata.input.grid.Grid grid: Grid instance.
    :return: (*dict*) -- keys are resources, values are dict of
        ((lat, lon): curtailment vector).
    """
    _check_curtailment(curtailment, grid)

    location_curtailment = {
        ren_type: summarize_plant_to_location(curtailment_df, grid).sum().to_dict()
        for ren_type, curtailment_df in curtailment.items()
    }

    return location_curtailment
