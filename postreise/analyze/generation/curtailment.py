import pandas as pd
from powersimdata.network.usa_tamu.constants.plants import renewable_resources

from postreise.analyze.check import (
    _check_areas_are_in_grid_and_format,
    _check_resources_are_renewable_and_format,
    _check_scenario_is_in_analyze_state,
)
from postreise.analyze.generation.summarize import (
    get_generation_time_series_by_resources,
)
from postreise.analyze.helpers import (
    decompose_plant_data_frame_into_areas,
    decompose_plant_data_frame_into_areas_and_resources,
    decompose_plant_data_frame_into_resources,
    decompose_plant_data_frame_into_resources_and_areas,
    get_plant_id_for_resources,
    get_plant_id_for_resources_in_area,
    summarize_plant_to_bus,
    summarize_plant_to_location,
)


def calculate_curtailment_time_series(scenario):
    """Calculate a time series of curtailment for renewable resources.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- time series of curtailment
    """
    _check_scenario_is_in_analyze_state(scenario)
    grid = scenario.state.get_grid()
    pg = scenario.state.get_pg()

    plant_id = get_plant_id_for_resources(
        renewable_resources.intersection(set(grid.plant.type)), grid
    )
    profiles = pd.concat(
        [scenario.state.get_solar(), scenario.state.get_wind()], axis=1
    )

    curtailment = (profiles[plant_id] - pg[plant_id]).clip(lower=0).round(6)
    return curtailment


def calculate_curtailment_time_series_by_resources(scenario, resources=None):
    """Calculate a time series of curtailment for a set of valid resources.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str/tuple/list/set resources: names of resources to analyze. Default is
        all renewable esources.
    :return: (*dict*) -- keys are resources, values are data frames indexed by
        (datetime, plant) where plant is only plants of matching type.
    """
    curtailment = calculate_curtailment_time_series(scenario)
    grid = scenario.state.get_grid()

    if resources is None:
        resources = renewable_resources.intersection(set(grid.plant.type))
    else:
        resources = _check_resources_are_renewable_and_format(resources)

    curtailment_by_resources = decompose_plant_data_frame_into_resources(
        curtailment, resources, grid
    )

    return curtailment_by_resources


def calculate_curtailment_time_series_by_areas(scenario, areas=None):
    """Calculate a time series of curtailment for a set of valid areas.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param dict areas: keys are area types ('*loadzone*', '*state*' or
        '*interconnect*'), values are a list of areas. Default is the interconnect of
        the scenario. Default is the scenario interconnect.
    :return: (*dict*) -- keys are areas, values are data frames indexed by
        (datetime, plant) where plant is only renewable plants in specified area.
    """
    curtailment = calculate_curtailment_time_series(scenario)
    grid = scenario.state.get_grid()

    areas = (
        _check_areas_are_in_grid_and_format(areas, grid)
        if areas is not None
        else {"interconnect": grid.interconnect}
    )

    curtailment_by_areas = decompose_plant_data_frame_into_areas(
        curtailment, areas, grid
    )

    return curtailment_by_areas


def calculate_curtailment_percentage_by_resources(scenario, resources=None):
    """Calculate scenario-long average curtailment for selected resources.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str/tuple/list/set resources: names of resources to analyze. Default is
        all renewable resources.
    :return: (*float*) -- Average curtailment fraction over the scenario.
    """
    curtailment = calculate_curtailment_time_series_by_resources(scenario, resources)
    resources = set(curtailment.keys())
    grid = scenario.state.get_grid()

    total_curtailment = {r: curtailment[r].sum().sum() for r in resources}

    profiles = pd.concat(
        [scenario.state.get_solar(), scenario.state.get_wind()], axis=1
    )
    total_potential = profiles.groupby(grid.plant.type, axis=1).sum().sum()

    curtailment_percentage = (
        sum(v for v in total_curtailment.values())
        / total_potential.loc[resources].sum()
    )

    return curtailment_percentage


def calculate_curtailment_time_series_by_areas_and_resources(
    scenario, areas=None, resources=None
):
    """Calculate a time series of curtailment for a set of valid areas and resources.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param dict areas: keys are area types ('*loadzone*', '*state*' or
        '*interconnect*'), values are a list of areas. Default is the interconnect of
        the scenario. Default is the scenario interconnect.
    :param str/tuple/list/set resources: names of resources to analyze. Default is
        all renewable resources.
    :return: (*dict*) -- keys are areas, values are dictionaries whose keys are
        resources and values are data frames indexed by (datetime, plant) where plant
        is only plants of matching type and located in area.
    """
    curtailment = calculate_curtailment_time_series(scenario)
    grid = scenario.state.get_grid()

    areas = (
        _check_areas_are_in_grid_and_format(areas, grid)
        if areas is not None
        else {"interconnect": grid.interconnect}
    )

    if resources is None:
        resources = renewable_resources.intersection(set(grid.plant.type))
    else:
        resources = _check_resources_are_renewable_and_format(resources)

    curtailment_by_areas_and_resources = (
        decompose_plant_data_frame_into_areas_and_resources(
            curtailment, areas, resources, grid
        )
    )
    return curtailment_by_areas_and_resources


def calculate_curtailment_time_series_by_resources_and_areas(
    scenario, areas=None, resources=None
):
    """Calculate a time series of curtailment for a set of valid resources and areas.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str/tuple/list/set resources: names of resources to analyze. Default is
        all renewable resources.
    :param dict areas: keys are area types ('*loadzone*', '*state*' or
        '*interconnect*'), values are a list of areas. Default is the interconnect of
        the scenario. Default is the scenario interconnect.
    :return: (*dict*) -- keys are areas, values are dictionaries whose keys are
        resources and values are data frames indexed by (datetime, plant) where plant
        is only plants of matching type and located in area.
    """
    curtailment = calculate_curtailment_time_series(scenario)
    grid = scenario.state.get_grid()

    areas = (
        _check_areas_are_in_grid_and_format(areas, grid)
        if areas is not None
        else {"interconnect": grid.interconnect}
    )

    if resources is None:
        resources = renewable_resources.intersection(set(grid.plant.type))
    else:
        resources = _check_resources_are_renewable_and_format(resources)

    curtailment_by_resources_and_areas = (
        decompose_plant_data_frame_into_resources_and_areas(
            curtailment, resources, areas, grid
        )
    )
    return curtailment_by_resources_and_areas


def summarize_curtailment_by_bus(scenario):
    """Calculate total curtailment for selected resources, by bus.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*dict*) -- keys are resources, values are dict of
        (bus: curtailment vector).
    """
    curtailment = calculate_curtailment_time_series_by_resources(scenario)
    grid = scenario.state.get_grid()

    bus_curtailment = {
        ren_type: summarize_plant_to_bus(curtailment_df, grid).sum().to_dict()
        for ren_type, curtailment_df in curtailment.items()
    }

    return bus_curtailment


def summarize_curtailment_by_location(scenario):
    """Calculate total curtailment for selected resources, by location.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*dict*) -- keys are resources, values are dict of
        ((lat, lon): curtailment vector).
    """
    curtailment = calculate_curtailment_time_series_by_resources(scenario)
    grid = scenario.state.get_grid()

    location_curtailment = {
        ren_type: summarize_plant_to_location(curtailment_df, grid).sum().to_dict()
        for ren_type, curtailment_df in curtailment.items()
    }

    return location_curtailment


def get_curtailment_time_series(scenario, area, area_type=None):
    """Get time series curtailments for each available resource in a certain area of
    a scenario

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str area_type: one of *'loadzone'*, *'state'*, *'state_abbr'*,
        *'interconnect'*
    :return: (*pandas.DataFrame*) -- index: time stamps, columns: available resources
    """
    renewables = ["wind", "wind_offshore", "solar"]
    curtailment = get_generation_time_series_by_resources(
        scenario, area, renewables, area_type=area_type
    )
    renewable_profiles = pd.concat(
        [scenario.state.get_wind(), scenario.state.get_solar()], axis=1
    )
    for r in renewables:
        if r in curtailment.columns:
            plant_id = get_plant_id_for_resources_in_area(
                scenario, area, r, area_type=area_type
            )
            curtailment[r] = renewable_profiles[plant_id].sum(axis=1) - curtailment[r]
    curtailment.rename(lambda x: x + "_curtailment", axis="columns", inplace=True)

    return curtailment.clip(lower=0)
