import pandas as pd
from powersimdata.input.check import (
    _check_areas_are_in_grid_and_format,
    _check_resources_are_renewable_and_format,
)
from powersimdata.input.helpers import (
    decompose_plant_data_frame_into_areas,
    decompose_plant_data_frame_into_areas_and_resources,
    decompose_plant_data_frame_into_resources,
    decompose_plant_data_frame_into_resources_and_areas,
    get_plant_id_for_resources,
    get_plant_id_for_resources_in_area,
    summarize_plant_to_bus,
    summarize_plant_to_location,
)
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state

from postreise.analyze.generation.summarize import (
    get_generation_time_series_by_resources,
)


def calculate_curtailment_time_series(scenario):
    """Calculate hourly curtailment for each renewable generator.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- time series of curtailment.
    """
    _check_scenario_is_in_analyze_state(scenario)
    grid = scenario.state.get_grid()
    pg = scenario.state.get_pg()

    plant_id = get_plant_id_for_resources(
        grid.model_immutables.plants["renewable_resources"].intersection(
            set(grid.plant.type)
        ),
        grid,
    )
    profiles = pd.concat(
        [scenario.state.get_solar(), scenario.state.get_wind()], axis=1
    )

    curtailment = (profiles[plant_id] - pg[plant_id]).clip(lower=0).round(6)
    return curtailment


def calculate_curtailment_time_series_by_resources(scenario, resources=None):
    """Calculate hourly curtailment by generator type(s).

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str/tuple/list/set resources: names of resources to analyze. Default is
        all renewable esources.
    :return: (*dict*) -- keys are resources, values are data frames indexed by
        (datetime, plant id).
    """
    curtailment = calculate_curtailment_time_series(scenario)
    grid = scenario.state.get_grid()

    if resources is None:
        resources = grid.model_immutables.plants["renewable_resources"].intersection(
            set(grid.plant.type)
        )
    else:
        resources = _check_resources_are_renewable_and_format(
            resources, grid_model=scenario.info["grid_model"]
        )

    curtailment_by_resources = decompose_plant_data_frame_into_resources(
        curtailment, resources, grid
    )

    return curtailment_by_resources


def calculate_curtailment_time_series_by_areas(scenario, areas=None):
    """Calculate hourly curtailment by area(s).

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param dict areas: keys are area types ('*loadzone*', '*state*' or
        '*interconnect*'), values are a list of areas. Default is the interconnect of
        the scenario. Default is the scenario interconnect.
    :return: (*dict*) -- keys are areas, values are data frames indexed by
        (datetime, plant id).
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
    """Calculate scenario-long average curtailment fraction for a set of generator
    type(s).

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str/tuple/list/set resources: names of resources to analyze. Default is
        all renewable resources.
    :return: (*float*) -- average curtailment fraction over the scenario.
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
    """Calculate hourly curtailment of each generator located in area(s) area and
    fueled by resource(s).

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param dict areas: keys are area types ('*loadzone*', '*state*' or
        '*interconnect*'), values are a list of areas. Default is the scenario
        interconnect(s).
    :param str/tuple/list/set resources: names of resources to analyze. Default is
        all renewable resources.
    :return: (*dict*) -- keys are areas, values are dictionaries whose keys are
        resources and values are data frames indexed by (datetime, plant id).
    """
    curtailment = calculate_curtailment_time_series(scenario)
    grid = scenario.state.get_grid()

    areas = (
        _check_areas_are_in_grid_and_format(areas, grid)
        if areas is not None
        else {"interconnect": grid.interconnect}
    )

    if resources is None:
        resources = grid.model_immutables.plants["renewable_resources"].intersection(
            set(grid.plant.type)
        )
    else:
        resources = _check_resources_are_renewable_and_format(
            resources, grid_model=scenario.info["grid_model"]
        )

    curtailment_by_areas_and_resources = (
        decompose_plant_data_frame_into_areas_and_resources(
            curtailment, areas, resources, grid
        )
    )
    return curtailment_by_areas_and_resources


def calculate_curtailment_time_series_by_resources_and_areas(
    scenario, areas=None, resources=None
):
    """Calculate hourly curtailment of each generator fueled by resources and located
    in area(s).

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param str/tuple/list/set resources: names of resources. Default is all renewable
        resources.
    :param dict areas: keys are area types ('*loadzone*', '*state*' or
        '*interconnect*'), values are a list of areas. Default is the scenario
        interconnect(s).
    :return: (*dict*) -- keys are areas, values are dictionaries whose keys are
        resources and values are data frames indexed by (timestamp, plant id).
    """
    curtailment = calculate_curtailment_time_series(scenario)
    grid = scenario.state.get_grid()

    areas = (
        _check_areas_are_in_grid_and_format(areas, grid)
        if areas is not None
        else {"interconnect": grid.interconnect}
    )

    if resources is None:
        resources = grid.model_immutables.plants["renewable_resources"].intersection(
            set(grid.plant.type)
        )
    else:
        resources = _check_resources_are_renewable_and_format(
            resources, grid_model=scenario.info["grid_model"]
        )

    curtailment_by_resources_and_areas = (
        decompose_plant_data_frame_into_resources_and_areas(
            curtailment, resources, areas, grid
        )
    )
    return curtailment_by_resources_and_areas


def summarize_curtailment_by_bus(scenario):
    """Calculate total curtailment by bus.

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
    """Calculate total curtailment by location.

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
    """Get hourly curtailment for each available resource(s) in area.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str area_type: one of *'loadzone'*, *'state'*, *'state_abbr'*,
        *'interconnect'*
    :return: (*pandas.DataFrame*) -- index: timestamps, columns: available renewable
        resource(s).
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
