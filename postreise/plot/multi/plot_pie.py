import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from postreise.plot.multi.constants import (ALL_RESOURCE_TYPES,
                                            RESOURCE_COLORS, RESOURCE_LABELS)
from postreise.plot.multi.plot_helpers import handle_plot_inputs


def plot_pie(interconnect, scenario_ids=None, custom_data=None, min_percentage=0):
    """Plots any number of scenarios as pie charts with two columns per scenario - defaults to generation and capacity

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
    :param min_percentage: roll up small pie pieces into an Other category, defaults to 0
    :type min_percentage: float, optional
    """
    zone_list, graph_data = handle_plot_inputs(
        interconnect, scenario_ids, custom_data)
    for zone in zone_list:
        ax_data_list = _construct_pie_ax_data(zone, graph_data, min_percentage)
        _construct_pie_visuals(zone, ax_data_list)
    print(f'\nDone\n')


def _construct_pie_ax_data(zone, scenarios, min_percentage):
    """Creates a list of labels, values, and colors for each axis of the plot

    :param zone: the zone name
    :type zone: string
    :param scenarios: the scenario data to format
    :type scenarios: dict {'scenario_id': {
        'label': 'scenario_name',
        'gen': {'label': 'Generation', 'unit': 'TWh', 'data': {'zone_name': {'resource_type': float value(s), ...}, ...}},
        'cap': {'label': 'Capacity', 'unit': 'GW', 'data': {'zone_name': {'resource_type': float value(s), ...}, ...}}},
        ...}
    :param min_percentage: roll up small pie pieces into an Other category
    :type min_percentage: float
    :return: a list of labels, values, and colors for each axis of the plot
    :rtype: list(dict) [{title, labels, values, colors, unit}, ...]
    """
    ax_data_list = []
    for scenario in scenarios.values():
        for side in ['gen', 'cap']:
            ax_data, labels = _roll_up_small_pie_wedges(
                scenario[side]['data'][zone], min_percentage)

            ax_data_list.append({
                'title': '{0}\n{1}'.format(scenario['label'], scenario[side]['label']),
                'labels': labels,
                'values': list(ax_data.values()),
                'colors': [RESOURCE_COLORS[resource] for resource in ax_data.keys()],
                'unit': scenario[side]['unit']})
    return ax_data_list


def _roll_up_small_pie_wedges(resource_data, min_percentage):
    """Combines small wedges into an "other" category
        Removes wedges with value 0

    :param resource_data: values for each resource type
    :type resource_data: dict {'resource_type': float value, ...}
    :param min_percentage: roll up small pie pieces into an Other category
    :type min_percentage: float
    :return: Returns updated axis data and a list of labels that includes the other category label if it exists
    :rtype: dict {'resource_type': float value, ...}
    """
    resource_list = list(resource_data.keys())
    total_resources = sum(resource_data.values())

    small_categories = []
    other_category_value = 0
    other_category_label = ''
    for resource in resource_list:
        percentage = round(resource_data[resource]/total_resources*100, 1)
        if percentage == 0.0:
            resource_data.pop(resource)
        elif percentage <= min_percentage:
            small_categories.append(resource)
            other_category_label += '{0} {1}%\n'.format(
                RESOURCE_LABELS[resource], percentage)
            other_category_value += resource_data[resource]

    if len(small_categories) > 1:
        for resource in small_categories:
            resource_data.pop(resource)

    labels = [RESOURCE_LABELS[resource] for resource in resource_data.keys()]

    if len(small_categories) > 1:
        resource_data['other'] = other_category_value
        labels.append(other_category_label)

    return resource_data, labels


def _construct_pie_visuals(zone, ax_data_list):
    """Use matplot lib to plot formatted data

    :param zone: the zone name
    :type zone: string
    :param ax_data: a list of labels, values, and colors for each axis of the plot
    :type ax_data: list(dict) [{title, labels, values, colors, unit}, ...]
    """
    rows = int(len(ax_data_list)/2)
    fig, axes = plt.subplots(rows, 2, figsize=(20, 12*rows))
    if rows > 1:
        axes = np.concatenate(axes)
    plt.suptitle(zone, fontsize=36, verticalalignment="bottom")

    for ax_data, ax in zip(ax_data_list, axes):
        df = pd.DataFrame({'': ax_data['values']}, index=ax_data['labels'])
        df.plot(kind='pie', ax=ax, subplots=True, fontsize=18, autopct='%1.1f%%', startangle=180,
                pctdistance=.55, colors=ax_data['colors'], wedgeprops={'edgecolor': 'white', 'linewidth': 6})
        ax.set_title(ax_data['title'], fontsize=30)
        ax.get_legend().remove()
        ax.tick_params(axis='y', which='both', left=False)
        ax.add_artist(plt.Circle((0, 0), 0.70, fc='white'))
        ax.text(0, 0, '{0}\n{1}'.format(round(sum(ax_data['values']), 1), ax_data['unit']), fontsize=22,
                verticalalignment='center', horizontalalignment='center', weight="bold", color='lightgray')

    plt.tight_layout()
    fig.subplots_adjust(hspace=-.2)
