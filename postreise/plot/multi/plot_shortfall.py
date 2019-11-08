import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from postreise.plot.multi.plot_helpers import handle_shortfall_inputs

# plot_shortfall: Plots any number of scenarios with two columns per scenario
# interconnect: 'Western' or 'Texas'
# scenario_ids: list of scenario ids
# TODO: might want to make a class for custom_data. Waiting until larger refactor
# custom_data: optional hand-generated data, formatted as thus:
# {'historical_texas': {
#   'label': 'Historical Texas 2016 Data',
#   'gen': {'label': 'Generation', 'unit': 'TWh', 'data': {'Far West': {'coal': 45.7, 'ng': 80.2, ...}, ...}}
#   'cap': { same as gen }}}
# NOTE: If you want to plot scenario data and custom data together, custom data MUST be in TWh for generation and GW for capacity.
#       We may add a feature to check for and convert to equal units but it's not currently a priority
# is_match_CA (optional): bool: calculate shortfall using special rules that apply when all zones match California goals
# has_collaborative_scenarios: list(string): list of scenario ids where all zones collaborate to meet goals. Affects results for interconnect
# baselines (optional): dict {zone: int generation in TWh} baseline renewables generation for each zone
# targets (optional): dict {zone: int generation in TWh} target renewables renewable generation for each zone
# demand (optional): dict {zone: int demand in TWh} total demand for each zone


def plot_shortfall(interconnect, scenario_ids=None, custom_data=None, is_match_CA=False, has_collaborative_scenarios=None, baselines=None, targets=None, demand=None):
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

# returns: dictionary of data to visualize { '2016 NREL': {'2016 Renewables': 100, 'Simulated increase in renewables': 30, 'Missed target': 10 }, ...}
#          and a list of shortfall percentages to show on the graph


def _construct_shortfall_ax_data(zone, scenarios, is_match_CA, baseline, target, demand):
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

# Western has unique needs for data construction
# there are special rules around calculating shortfall when a scenario is collaborative vs. when it's independent.
# returns: dictionary of data to visualize { '2016 NREL': {'2016 Renewables': 100, 'Simulated increase in renewables': 30, 'Missed target': 10 }, ...}
#          and a list of shortfall percentages to show on the graph


def _construct_shortfall_data_for_western(scenarios, is_match_CA, has_collaborative_scenarios, baseline, targets, demand):
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

# returns the sum of all the renewable energy generated in a zone


def _get_total_generated_renewables(zone, resource_data, is_match_CA):
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
