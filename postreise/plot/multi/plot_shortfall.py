import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from postreise.plot.multi.plot_helpers import handle_shortfall_inputs


def plot_shortfall(interconnect, scenario_ids=None, custom_data=None, is_match_CA=False, has_collaborative_scenarios=None, baselines=None, targets=None, demand=None):
    """Plots a stacked bar chart of generation shortfall for any number of scenarios

    :param interconnect: either 'Western' or 'Texas'
    :type interconnect: string
    :param scenario_ids: list of scenario ids, defaults to None
    :type scenario_ids: list(string), optional
    :param custom_data: hand-generated data, defaults to None
    :type custom_data: dict {'scenario_id': {
        'label': 'scenario_name',
        'gen': {'label': 'Generation', 'unit': 'TWh', 'data': {'zone_name': {'resource_type': float value(s), ...}, ...}},
        'cap': {'label': 'Capacity', 'unit': 'GW', 'data': {'zone_name': {'resource_type': float value(s), ...}, ...}}},
        ...}, optional
    NOTE: If you want to plot scenario data and custom data together, custom data MUST be in TWh for generation and GW for capacity.
        We may add a feature to check for and convert to equal units but it's not currently a priority
    :param is_match_CA: calculate shortfall using special rules that apply when all zones match California goals, defaults to False
    :type is_match_CA: bool, optional
    :param has_collaborative_scenarios: list of scenario ids where all zones collaborate to meet goals. Affects results for interconnect, defaults to None
    :type has_collaborative_scenarios: list(string), optional
    :param baselines: baseline renewables generation for each zone, defaults to None
    :type baselines: dict {zone: float generation in TWh}, optional
    :param targets: target renewables renewable generation for each zone, defaults to None
    :type targets: dict {zone: float generation in TWh}, optional
    :param demand: total demand for each zone, defaults to None
    :type demand: dict {zone: float generation in TWh}, optional
    """
    zone_list, graph_data, baselines, targets, demand = handle_shortfall_inputs(
        interconnect, scenario_ids, custom_data, is_match_CA, baselines, targets, demand)

    for zone in zone_list:
        if zone == 'Western':
            ax_data, shortfall_pct_list = _construct_shortfall_data_for_western(
                graph_data, is_match_CA, has_collaborative_scenarios, baselines[zone], targets, demand[zone])
        else:
            ax_data, shortfall_pct_list = _construct_shortfall_ax_data(
                zone, graph_data, is_match_CA, baselines[zone], targets[zone], demand[zone])
        _construct_shortfall_visuals(
            zone, ax_data, shortfall_pct_list, is_match_CA, targets[zone], demand[zone])
    print(f'\nDone\n')


def _construct_shortfall_ax_data(zone, scenarios, is_match_CA, baseline, target, demand):
    """Formats scenario data into something we can plot

    :param zone: the zone name
    :type zone: string
    :param scenarios: the scenario data to format
    :type scenarios: dict {'scenario_id': {
        'label': 'scenario_name',
        'gen': {'label': 'Generation', 'unit': 'TWh', 'data': {'zone_name': {'resource_type': float value(s), ...}, ...}},
        'cap': {'label': 'Capacity', 'unit': 'GW', 'data': {'zone_name': {'resource_type': float value(s), ...}, ...}}},
        ...}
    :param is_match_CA: calculate shortfall using special rules that apply when all zones match California goals
    :type is_match_CA: bool
    :param baseline: baseline renewables generation for this zone
    :type baseline: float
    :param target: target renewables renewable generation for this zone
    :type target: float
    :param demand: total demand for this zone
    :type demand: float
    :return: dictionary of data to visualize 
    :rtype: dict { 'scenario_name': {'2016 Renewables': float value, 'Simulated increase in renewables': float value, 'Missed target': float value }, ...}
    """
    ax_data = {}
    shortfall_pct_list = []

    for scenario in scenarios.values():
        total_renewables = _get_total_generated_renewables(
            zone, scenario['gen']['data'][zone], is_match_CA)

        shortfall = max(0, round(target - total_renewables, 2))
        shortfall_pct = round(shortfall/demand*100, 1) if target != 0 else 0
        shortfall_pct_list.append(shortfall_pct)

        # TODO this breaks the visuals if renewables decrease - decide with team on how to show
        print(f'\n\n{zone}\n')
        print(baseline, '|', total_renewables, '|', target, '|', shortfall)
        ax_data.update({scenario['label']: {
            '2016 Renewables': baseline,
            'Simulated increase in renewables': max(0, round(total_renewables - baseline, 2)),
            'Missed target': shortfall}})

    return ax_data, shortfall_pct_list


def _construct_shortfall_data_for_western(scenarios, is_match_CA, has_collaborative_scenarios, baseline, targets, demand):
    """Formats scenario data into something we can plot. Western has unique needs for data construction
        there are special rules around calculating shortfall when a scenario is collaborative vs. when it's independent.

    :param scenarios: the scenario data to format
    :type scenarios: dict {'scenario_id': {
        'label': 'scenario_name',
        'gen': {'label': 'Generation', 'unit': 'TWh', 'data': {'zone_name': {'resource_type': float value(s), ...}, ...}},
        'cap': {'label': 'Capacity', 'unit': 'GW', 'data': {'zone_name': {'resource_type': float value(s), ...}, ...}}},
        ...}
    :param is_match_CA: calculate shortfall using special rules that apply when all zones match California goals
    :type is_match_CA: bool
    :param has_collaborative_scenarios: list of scenario ids where all zones collaborate to meet goals. Affects results for interconnect
    :type has_collaborative_scenarios: list(string)
    :param baseline: baseline renewables generation for this zone
    :type baseline: float
    :param targets: target renewables renewable generation for each zone, defaults to None
    :type targets: dict {zone: float generation in TWh}, optional
    :param demand: total demand for this zone
    :type demand: float
    :return: dictionary of data to visualize 
    :rtype: dict { 'scenario_name': {'2016 Renewables': float value, 'Simulated increase in renewables': float value, 'Missed target': float value }, ...}
    """
    ax_data = {}
    shortfall_pct_list = []

    for s_id, scenario in scenarios.items():
        zone_list = list(scenario['gen']['data'].keys())
        if 'Western' in zone_list:
            zone_list.remove('Western')
        renewables_by_zone = {zone: _get_total_generated_renewables(
            zone, scenario['gen']['data'][zone], is_match_CA) for zone in zone_list}

        # When states can collaborate they make up for each other's shortfall
        if has_collaborative_scenarios is not None and s_id in has_collaborative_scenarios:
            total_renewables = sum(renewables_by_zone.values())
            shortfall = shortfall = max(
                0, round(targets['Western'] - total_renewables, 2))
        else:
            # When the zones do not collaborate, zones with extra renewables can't help zones with shortfall
            # thus the shortfall is the sum of the shortfall from every state
            shortfall = sum(
                [max(0, round(targets[zone] - renewables_by_zone[zone], 2)) for zone in zone_list])
            # total_renewables here is meaningless in terms of the shortfall so we fudge it to match the target line
            total_renewables = targets['Western'] - shortfall

        shortfall_pct_list.append(round(shortfall/demand*100, 1))

        # If increase in renewables is 0 we have a base case scenario and thus the baseline is used as the source of truth
        shortfall = max(
            0, targets['Western'] - baseline) if total_renewables <= baseline else shortfall
        print(f'\n\nWestern\n')
        print(baseline, '|', total_renewables, '|',
              targets['Western'], '|', shortfall)
        ax_data.update({scenario['label']: {
            '2016 Renewables': baseline,
            'Simulated increase in renewables': max(0, round(total_renewables - baseline, 2)),
            'Missed target': shortfall}})

    return ax_data, shortfall_pct_list


def _get_total_generated_renewables(zone, resource_data, is_match_CA):
    """ Calculates the sum of all the renewable energy generated in a zone

    :param zone: the zone name
    :type zone: string
    :param resource_data: dict of values for each resource type
    :type resource_data: dict {'resource_type': float value, ...}
    :param is_match_CA: calculate generation using special rules that apply when all zones match California goals
    :type is_match_CA: bool
    :return: the sum of all the renewable energy generated in a zone
    :rtype: float
    """
    CA_extras = 32.045472

    resource_types = ['wind', 'solar', 'geothermal']
    total_renewables = sum([resource_data[resource] if resource in resource_data.keys(
    ) else 0 for resource in resource_types])

    # Scenario data does not include Extras for California so we add them back in
    if zone == 'California':
        total_renewables += CA_extras
    # Washington's goals also include "clean energy", i.e. nuclear and hydro
    if zone == 'Washington' and not is_match_CA:
        resource_types = ['hydro', 'nuclear']
        total_renewables += sum([resource_data[resource]
                                 if resource in resource_data.keys() else 0 for resource in resource_types])

    return total_renewables


def _construct_shortfall_visuals(zone, ax_data, shortfall_pct_list, is_match_CA, target, demand):
    """Use matplot lib to plot formatted data

    :param zone: the zone name
    :type zone: string
    :param ax_data: the formatted data to plot
    :type ax_data: dict { 'scenario_name': {'2016 Renewables': float value, 'Simulated increase in renewables': float value, 'Missed target': float value }, ...}
    :param shortfall_pct_list: list of percent shortfall in terms of total demand
    :type shortfall_pct_list: list(string)
    :param is_match_CA: calculate shortfall using special rules that apply when all zones match California goals
    :type is_match_CA: bool
    :param target: target renewables renewable generation for this zone
    :type target: float
    :param demand: total demand for this zone
    :type demand: float
    """
    df = pd.DataFrame(ax_data).T
    ax = df.plot.bar(stacked=True, color=[
                     'darkgreen', 'yellowgreen', 'salmon'], figsize=(10, 8), fontsize=16)
    ax.set_title(zone, fontsize=26)
    ax.set_ylim(top=1.33*ax.get_ylim()[1])
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45,
                       horizontalalignment='right')

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed(labels),
              bbox_to_anchor=(1.556, 1.015), fontsize=14)

    # Add target line
    if target > 0:
        ax_text = f'Target {int(round(target/demand*100, 0))}% of\n2030 demand'
        if is_match_CA and zone != 'California':
            ax_text = 'CA ' + ax_text

        ax.plot([-.5, 2.5], [target, target], "k--")
        ax.text(len(ax_data)-0.45, target, ax_text,
                verticalalignment='center', fontsize=16)

    # Percent numbers
    patch_indices = list(range(len(ax_data)*3))[-1*len(ax_data):]
    for (i, shortfall_pct) in zip(patch_indices, shortfall_pct_list):
        if shortfall_pct != 0:
            b = ax.patches[i].get_bbox()
            ax.annotate(f'{shortfall_pct}%\nshortfall',
                        (b.x1 - 0.5, b.y1*1.02), fontsize=16)
