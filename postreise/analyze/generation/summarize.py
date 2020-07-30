from collections import defaultdict
import pandas as pd
import numpy as np

from powersimdata.design.scenario_info import ScenarioInfo
from powersimdata.scenario.scenario import Scenario
from powersimdata.scenario.analyze import Analyze
from powersimdata.utility.constants import (
    interconnect2state,
    abv2state,
    loadzone2state,
    loadzone2interconnect,
)


colname_map = {
    "Coal": "coal",
    "DFO": "dfo",
    "Geo-thermal": "geothermal",
    "Hydro": "hydro",
    "Natural Gas": "ng",
    "Nuclear": "nuclear",
    "Solar": "solar",
    "Wind": "wind",
    "Storage": "storage",
    "Biomass": "biomass",
    "Other": "other",
}


def sum_generation_by_type_zone(scenario):
    """Sums generation for a Scenario in Analyze state by {type, zone}.
    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- total generation, indexed by {type, zone}.
    :raise Exception: if scenario is not a Scenario object in Analyze state.
    """
    if not isinstance(scenario, Scenario):
        raise TypeError("scenario must be a Scenario object")
    if not isinstance(scenario.state, Analyze):
        raise ValueError("scenario.state must be Analyze")

    pg = scenario.state.get_pg()
    grid = scenario.state.get_grid()
    plant = grid.plant

    summed_gen_series = pg.sum().groupby([plant.type, plant.zone_id]).sum()
    summed_gen_dataframe = summed_gen_series.unstack().fillna(value=0)

    return summed_gen_dataframe


def _modified_state_list(interconnects):
    """
    Get the list of states in the given interconnects, but include larger areas
    as well.
    :param list interconnects: list of interconnects
    :return: list -- list of states and interconnects
    """
    state_list = ["all"]
    for ic in interconnects:
        state_list += interconnect2state[ic]
    if "Western" in interconnects:
        state_list.append("Western")
    if "Eastern" in interconnects:
        state_list.append("Eastern")
    return state_list


def sum_generation_by_state(scenario):
    """
    Get the generation of each resource from the scenario by state, including
    totals for the given interconnects.
    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*pandas.DataFrame*) -- total generation per resource, by state
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
    energy_by_type = energy_by_type_state.sum(axis=1).to_frame(name="all")
    # Combine groupbys and format for final output (GWh, index=zone, columns=types)
    energy_by_type_state = pd.concat(
        [energy_by_type_state, energy_by_type_interconnect, energy_by_type], axis=1
    )
    energy_by_type_state /= 1000
    energy_by_type_state = energy_by_type_state.transpose()

    return energy_by_type_state


def _groupby_state(index):
    """
    Use state as a dict key if index is a smaller region (e.g. Texas East),
    otherwise use the given index.
    """
    for state in ("Texas", "New Mexico", "Montana"):
        if state in index:
            return state
    return index


def summarize_hist_gen(hist_gen_raw, all_resources):
    """
    Sum generation by state for the given resources from some scenario,
    adding additional rows for totals in each interconnect.
    """
    western = [abv2state[s] for s in interconnect2state["Western"]]
    eastern = [abv2state[s] for s in interconnect2state["Eastern"]]

    filtered_colnames = [
        k for k in colname_map.keys() if colname_map[k] in all_resources
    ]
    result = hist_gen_raw.copy()
    result = result.loc[:, filtered_colnames]
    result.rename(columns=colname_map, inplace=True)
    result = result.groupby(by=_groupby_state).aggregate(np.sum)
    result.loc["Western"] = result[result.index.isin(western)].sum()
    result.loc["Eastern"] = result[result.index.isin(eastern)].sum()
    result.loc["all"] = result[~result.index.isin(["Eastern", "Western"])].sum()
    return result
