import numpy as np
import pandas as pd
from powersimdata.network.usa_tamu.constants.plants import type2label
from powersimdata.network.usa_tamu.constants.zones import (
    abv2state,
    interconnect2abv,
    interconnect2loadzone,
    loadzone2interconnect,
    loadzone2state,
    state2loadzone,
)
from powersimdata.scenario.scenario import Scenario

from postreise.analyze.check import (
    _check_data_frame,
    _check_resources_and_format,
    _check_scenario_is_in_analyze_state,
)
from postreise.analyze.helpers import (
    get_plant_id_for_resources_in_area,
    get_storage_id_in_area,
)


def sum_generation_by_type_zone(scenario: Scenario) -> pd.DataFrame:
    """Sum generation for a Scenario in Analyze state by {type, zone}.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- total generation, indexed by {type, zone}.
    """
    _check_scenario_is_in_analyze_state(scenario)

    pg = scenario.state.get_pg()
    grid = scenario.state.get_grid()
    plant = grid.plant

    summed_gen_series = pg.sum().groupby([plant.type, plant.zone_id]).sum()
    summed_gen_dataframe = summed_gen_series.unstack().fillna(value=0)

    return summed_gen_dataframe


def sum_generation_by_state(scenario: Scenario) -> pd.DataFrame:
    """Get the generation of each resource from the scenario by state, including
    totals for the given interconnects and for all states.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- total generation per resource, by area.
    """
    # Start with energy by type & zone name
    energy_by_type_zoneid = sum_generation_by_type_zone(scenario)
    zoneid2zonename = scenario.state.get_grid().id2zone
    energy_by_type_zonename = energy_by_type_zoneid.rename(zoneid2zonename, axis=1)
    # Build lists to use for groupbys
    zone_list = energy_by_type_zonename.columns
    zone_states = [loadzone2state[zone] for zone in zone_list]
    zone_interconnects = [loadzone2interconnect[zone] for zone in zone_list]
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


def _groupby_state(index: str) -> str:
    """Use state as a dict key if index is a smaller region (e.g. Texas East),
    otherwise use the given index.

    :param str index: either a state name or region within a state.
    :return: (*str*) -- the corresponding state name.
    """
    interconnect_spanning_states = ("Texas", "New Mexico", "Montana")
    for state in interconnect_spanning_states:
        if index in state2loadzone[state]:
            return state
    return index


def summarize_hist_gen(hist_gen_raw: pd.DataFrame, all_resources: list) -> pd.DataFrame:
    """Sum generation by state for the given resources from a scenario, adding
    totals for interconnects and for all states.

    :param pandas.DataFrame hist_gen_raw: historical generation data frame. Columns
        are resources and indices are either state or load zone.
    :param list all_resources: list of resources.
    :return: (*pandas.DataFrame*) -- historical generation per resource.
    """
    _check_data_frame(hist_gen_raw, "PG")
    filtered_colnames = _check_resources_and_format(all_resources)

    result = hist_gen_raw.copy()

    # Interconnection
    eastern_areas = (
        set([abv2state[s] for s in interconnect2abv["Eastern"]])
        | interconnect2loadzone["Eastern"]
    )
    eastern = result.loc[result.index.isin(eastern_areas)].sum()

    ercot_areas = interconnect2loadzone["Texas"]
    ercot = result.loc[result.index.isin(ercot_areas)].sum()

    western_areas = (
        set([abv2state[s] for s in interconnect2abv["Western"]])
        | interconnect2loadzone["Western"]
    )
    western = result.loc[result.index.isin(western_areas)].sum()

    # State
    result = result.groupby(by=_groupby_state).aggregate(np.sum)

    # Summary
    all = result.sum()

    result.loc["Eastern interconnection"] = eastern
    result.loc["Western interconnection"] = western
    result.loc["Texas interconnection"] = ercot
    result.loc["All"] = all

    result = result.loc[:, filtered_colnames]
    result.rename(columns=type2label, inplace=True)

    return result


def get_generation_time_series_by_resources(scenario, area, resources, area_type=None):
    """Get time series generation for each resource in certain area of a scenario

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of: *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str/list resources: one or a list of resources
    :param str area_type: one of: *'loadzone'*, *'state'*,
        *'state_abbr'*, *'interconnect'*
    :return: (*pandas.DataFrame*) -- data frame of time series generation for each
        resource, index: time stamps, columns: resources
    """
    _check_scenario_is_in_analyze_state(scenario)
    plant_id = get_plant_id_for_resources_in_area(
        scenario, area, resources, area_type=area_type
    )
    pg = scenario.state.get_pg()[plant_id]
    grid = scenario.state.get_grid()

    return pg.T.groupby(grid.plant["type"]).agg(sum).T


def get_storage_time_series(scenario, area, area_type=None):
    """Get time series total storage energy in certain area of a scenario.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of: *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str area_type: one of: *'loadzone'*, *'state'*,
        *'state_abbr'*, *'interconnect'*
    :return: (*pandas.Series*) -- time series of total storage energy, index: time
        stamps, column: storage energy
    """
    _check_scenario_is_in_analyze_state(scenario)
    storage_id = get_storage_id_in_area(scenario, area, area_type)

    return scenario.state.get_storage_pg()[storage_id].sum(axis=1)
