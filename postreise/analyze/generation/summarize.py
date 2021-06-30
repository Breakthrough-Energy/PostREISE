import numpy as np
import pandas as pd
from powersimdata.input.check import _check_data_frame, _check_resources_and_format
from powersimdata.input.helpers import (
    get_plant_id_for_resources_in_area,
    get_storage_id_in_area,
)
from powersimdata.network.model import ModelImmutables
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state
from powersimdata.scenario.scenario import Scenario

from postreise.analyze.time import change_time_zone, slice_time_series


def sum_generation_by_type_zone(
    scenario: Scenario, time_range=None, time_zone=None
) -> pd.DataFrame:
    """Get total generation for each generator type and load zone combination.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :param tuple time_range: [start_timestamp, end_timestamp] where each time stamp
        is pandas.Timestamp/numpy.datetime64/datetime.datetime. If None, the entire
        time range is used for the given scenario.
    :param str time_zone: new time zone.
    :return: (*pandas.DataFrame*) -- total generation, indexed by {type, zone}.
    """
    _check_scenario_is_in_analyze_state(scenario)

    pg = scenario.state.get_pg()
    if time_zone:
        pg = change_time_zone(pg, time_zone)
    if time_range:
        pg = slice_time_series(pg, time_range[0], time_range[1])
    grid = scenario.state.get_grid()
    plant = grid.plant

    summed_gen_series = pg.sum().groupby([plant.type, plant.zone_id]).sum()
    summed_gen_dataframe = summed_gen_series.unstack().fillna(value=0)

    return summed_gen_dataframe


def sum_generation_by_state(scenario: Scenario) -> pd.DataFrame:
    """Get the total generation for each generator type and state combination, adding
    totals for the interconnects and for all states.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- total generation per resource, by area.
    """
    # Start with energy by type & zone name
    energy_by_type_zoneid = sum_generation_by_type_zone(scenario)
    grid = scenario.state.get_grid()
    zoneid2zonename = grid.id2zone
    energy_by_type_zonename = energy_by_type_zoneid.rename(zoneid2zonename, axis=1)
    # Build lists to use for groupbys
    zone_list = energy_by_type_zonename.columns
    zone_states = [
        grid.model_immutables.zones["loadzone2state"][zone] for zone in zone_list
    ]
    zone_interconnects = [
        grid.model_immutables.zones["loadzone2interconnect"][zone] for zone in zone_list
    ]
    # Run groupbys to aggregate by larger regions
    energy_by_type_state = energy_by_type_zonename.groupby(zone_states, axis=1).sum()
    energy_by_type_interconnect = energy_by_type_zonename.groupby(
        zone_interconnects, axis=1
    ).sum()
    duplicates = set(energy_by_type_interconnect.columns) & set(zone_states)
    energy_by_type_interconnect.drop(columns=duplicates, inplace=True)
    energy_by_type = energy_by_type_state.sum(axis=1).to_frame(name="all")
    # Combine groupbys and format for final output (GWh, index=zone, columns=types)
    energy_by_type_state = pd.concat(
        [energy_by_type_state, energy_by_type_interconnect, energy_by_type], axis=1
    )
    # Units in GWh
    energy_by_type_state /= 1000
    energy_by_type_state = energy_by_type_state.transpose()

    return energy_by_type_state


def summarize_hist_gen(
    hist_gen_raw: pd.DataFrame, all_resources: list, grid_model="usa_tamu"
) -> pd.DataFrame:
    """Get the total historical generation for each generator type and state
    combination, adding totals for interconnects and for all states.

    :param pandas.DataFrame hist_gen_raw: historical generation data frame. Columns
        are resources and indices are either state or load zone.
    :param list all_resources: list of resources.
    :param str grid_model: grid_model
    :return: (*pandas.DataFrame*) -- historical generation per resource.
    """
    _check_data_frame(hist_gen_raw, "PG")
    filtered_colnames = _check_resources_and_format(
        all_resources, grid_model=grid_model
    )
    mi = ModelImmutables(grid_model)

    result = hist_gen_raw.copy()

    # Interconnection
    eastern_areas = (
        set([mi.zones["abv2state"][s] for s in mi.zones["interconnect2abv"]["Eastern"]])
        | mi.zones["interconnect2loadzone"]["Eastern"]
    )
    eastern = result.loc[result.index.isin(eastern_areas)].sum()

    ercot_areas = mi.zones["interconnect2loadzone"]["Texas"]
    ercot = result.loc[result.index.isin(ercot_areas)].sum()

    western_areas = (
        set([mi.zones["abv2state"][s] for s in mi.zones["interconnect2abv"]["Western"]])
        | mi.zones["interconnect2loadzone"]["Western"]
    )
    western = result.loc[result.index.isin(western_areas)].sum()

    # State
    def _groupby_state(index: str) -> str:
        """Use state as a dict key if index is a smaller region (e.g. Texas East),
        otherwise use the given index.

        :param str index: either a state name or region within a state.
        :return: (*str*) -- the corresponding state name.
        """
        return (
            mi.zones["loadzone2state"][index]
            if index in mi.zones["loadzone2state"]
            else index
        )

    result = result.groupby(by=_groupby_state).aggregate(np.sum)

    # Summary
    all = result.sum()

    result.loc["Eastern interconnection"] = eastern
    result.loc["Western interconnection"] = western
    result.loc["Texas interconnection"] = ercot
    result.loc["All"] = all

    result = result.loc[:, filtered_colnames]
    result.rename(columns=mi.plants["type2label"], inplace=True)

    return result


def get_generation_time_series_by_resources(scenario, area, resources, area_type=None):
    """Get hourly total generation for generator type(s) in an area.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str/list resources: one or a list of resources
    :param str area_type: one of *'loadzone'*, *'state'*, *'state_abbr'*,
        *'interconnect'*
    :return: (*pandas.DataFrame*) -- times series of generation for each resource,
        index: timestamps, columns: resources
    """
    _check_scenario_is_in_analyze_state(scenario)
    plant_id = get_plant_id_for_resources_in_area(
        scenario, area, resources, area_type=area_type
    )
    pg = scenario.state.get_pg()[plant_id]
    grid = scenario.state.get_grid()

    return pg.groupby(grid.plant.loc[plant_id, "type"].values, axis=1).sum()


def get_storage_time_series(scenario, area, area_type=None, storage_e=False):
    """Get hourly total storage power generation in an area

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str area_type: one of *'loadzone'*, *'state'*, *'state_abbr'*,
        *'interconnect'*
    :param bool storage_e: if set, return time series energy of storage devices
        instead of power generation. Default to False.
    :return: (*pandas.Series*) -- time series of total storage power generation,
        if ``storage_e`` is not set, otherwise, time series of total storage energy,
        index: timestamps, values: storage power/storage energy
    """
    _check_scenario_is_in_analyze_state(scenario)
    storage_id = get_storage_id_in_area(scenario, area, area_type)

    if storage_e:
        return scenario.state.get_storage_e()[storage_id].sum(axis=1)
    else:
        return scenario.state.get_storage_pg()[storage_id].sum(axis=1)
