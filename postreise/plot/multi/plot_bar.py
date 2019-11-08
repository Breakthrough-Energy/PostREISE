import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from postreise.plot.multi.constants import ALL_RESOURCE_TYPES, RESOURCE_LABELS
from postreise.plot.multi.plot_helpers import handle_plot_inputs

# plot_bar: Plots any number of scenarios with two columns per scenario
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
# resource_types: optional. display only these resources


def plot_bar(interconnect, scenario_ids=None, custom_data=None, resource_types=None):
    zone_list, graph_data = handle_plot_inputs(
        interconnect, scenario_ids, custom_data)
    for zone in zone_list:
        ax_data_list = _construct_bar_ax_data(zone, graph_data, resource_types)
        _construct_bar_visuals(zone, ax_data_list)
    print(f'\nDone\n')

# plot_hbar: Plots any number of scenarios with two columns per scenario
# zone_name: 'Western' or 'Texas'
# scenario_ids: list of scenario ids
# TODO: might want to make a class for this. Waiting until larger refactor
# data: optional hand-generated data, formatted as thus:
# {'historical_texas': {
#   'label': 'Historical Texas 2016 Data',
#   'gen': {'label': 'Generation', 'unit': 'TWh', 'data': {'Far West': {'coal': 45.7, 'ng': 80.2, ...}, ...}}
#   'cap': { same as gen }}}
# resource_types: optional. display only these resources


def plot_hbar(zone_name, scenario_ids=None, custom_data=None, resource_types=None):
    zone_list, graph_data = handle_plot_inputs(
        zone_name, scenario_ids, custom_data)
    for zone in zone_list:
        ax_data_list = _construct_bar_ax_data(zone, graph_data, resource_types)
        _construct_hbar_visuals(zone, ax_data_list)
    print(f'\nDone\n')

# Creates a list of labels, values, and colors for each axis of the plot
# returns a list of dicts: [{title, labels, values, unit}, ...]


def _construct_bar_ax_data(zone, scenarios, user_set_resource_types):
    resource_types = user_set_resource_types if user_set_resource_types is not None else _get_bar_resource_types(
        zone, scenarios)

    ax_data_list = []
    for side in ['gen', 'cap']:
        ax_data = {}
        for scenario in scenarios.values():
            label = scenario['label']
            # If we don't have data for a resource type, set it to 0
            data_for_zone = scenario[side]['data'][zone]
            ax_data[label] = [data_for_zone[resource] if resource in data_for_zone.keys(
            ) else 0 for resource in resource_types]

        # Get title and unit from the first scenario
        scenario = list(scenarios.values())[0]
        ax_data_list.append({
            'title': '{0} ({1})'.format(scenario[side]['label'], scenario[side]['unit']),
            'labels': [RESOURCE_LABELS[resource] if resource in RESOURCE_LABELS else resource for resource in resource_types],
            'values': ax_data,
            'unit': scenario[side]['unit']
        })

    return ax_data_list

# Some scenarios might have extra data for resources like biofuel
# So we join the set of resource types from each scenario


def _get_bar_resource_types(zone, scenarios):
    resource_type_set = set()
    for scenario in scenarios.values():
        for side in ['gen', 'cap']:
            resource_type_set.update(scenario[side]['data'][zone].keys())

    # sort alphabetically first to consistently handle resource types not in ALL_RESOURCE_TYPES
    resource_types = sorted(list(resource_type_set))
    return sorted(resource_types, key=lambda resource: ALL_RESOURCE_TYPES.index(resource) if resource in ALL_RESOURCE_TYPES else float('inf'))


# Uses matplotlib to create a bar graph
# param: ax_data_list: a list of dicts. Each dict represents data for one graph
# dict structure: {title, labels, values, unit}
def _construct_bar_visuals(zone, ax_data_list):
    num_scenarios = len(ax_data_list[0]['values'].keys())
    num_resource_types = len(ax_data_list[0]['labels'])

    fig, axes = plt.subplots(1, 2, figsize=(
        1.5*num_scenarios*num_resource_types, 6))
    plt.suptitle(zone, fontsize=30, verticalalignment="bottom")

    for ax_data, ax in zip(ax_data_list, axes):
        df = pd.DataFrame(ax_data['values'], index=ax_data['labels'])
        df.plot(kind='bar', ax=ax, edgecolor='white', linewidth=2)
        ax.set_title(ax_data['title'], fontsize=25)

        ax.tick_params(axis='both', which='both', labelsize=20)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.set_xlabel('')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45,
                           horizontalalignment='right')
        ax.set_yticks([])
        ax.set_ylim(top=1.3*ax.get_ylim()[1])

        ax.legend(bbox_to_anchor=(-.03, -.67), loc='upper left', fontsize=16)

        for p in ax.patches:
            b = p.get_bbox()
            ax.annotate(_get_bar_display_val(b.y1), ((b.x1 + b.x0)/2, b.y1 + 0.02*ax.get_ylim()
                                                     [1]), fontsize=10, rotation='horizontal', horizontalalignment='center')


def _construct_hbar_visuals(zone, ax_data_list):
    num_scenarios = len(ax_data_list[0]['values'].keys())
    num_resource_types = len(ax_data_list[0]['labels'])

    fig, axes = plt.subplots(1, 2, figsize=(
        20, 0.7*num_scenarios*num_resource_types))
    plt.suptitle(zone, fontsize=30, verticalalignment="bottom")
    plt.subplots_adjust(wspace=1)

    for ax_data, ax in zip(ax_data_list, axes):
        df = pd.DataFrame(ax_data['values'], index=ax_data['labels'])
        df.plot(kind='barh', ax=ax, edgecolor='white', linewidth=2)
        ax.set_title(ax_data['title'], fontsize=25)

        ax.tick_params(axis='y', which='both', labelsize=20)
        ax.set_xticklabels('')
        ax.set_ylabel('')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.set_xticks([])

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(reversed(handles), reversed(labels),
                  bbox_to_anchor=(-.03, 0), loc='upper left', fontsize=16)

        for p in ax.patches:
            b = p.get_bbox()
            ax.annotate(_get_bar_display_val(b.x1), (b.x1, b.y1-.02),
                        fontsize=14, verticalalignment='top')

# Get bar display val:
# :param val: int: the value to change
# return an int if value is 0 or greater than 10, and round to one decimal otherwise


def _get_bar_display_val(val):
    if val >= 10:
        return int(round(val, 0))

    rounded = round(val, 1)
    return rounded if rounded > 0 else 0
