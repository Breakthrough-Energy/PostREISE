import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from collections import OrderedDict

from postreise.plot.multi.constants import ALL_RESOURCE_TYPES, RESOURCE_LABELS, RESOURCE_COLORS
from postreise.plot.multi.plot_helpers import handle_plot_inputs

# plot_pie: Plots any number of scenarios with two columns per scenario
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
# min_percentage: roll up small pie pieces
def plot_pie(interconnect, scenario_ids=None, custom_data=None, min_percentage=0):
    zone_list, graph_data = handle_plot_inputs(interconnect, scenario_ids, custom_data)
    for zone in zone_list:
        ax_data_list = _construct_pie_ax_data(zone, graph_data, min_percentage)
        _construct_pie_visuals(zone, ax_data_list)
    print(f'\nDone\n')

# Creates a list of labels, values, and colors for each axis of the plot
# returns a list of dicts: [{title, labels, values, colors, unit}, ...]
def _construct_pie_ax_data(zone, scenarios, min_percentage):
    ax_data_list = []
    for scenario in scenarios.values():
        for side in ['gen', 'cap']:  
            ax_data, labels = _roll_up_small_pie_wedges(scenario[side]['data'][zone], min_percentage) 

            ax_data_list.append({
                'title': scenario[side]['label'], 
                'labels': labels,
                'values': list(ax_data.values()),
                'colors': [RESOURCE_COLORS[resource] for resource in ax_data.keys()],
                'unit': scenario[side]['unit']})
    return ax_data_list

# For pie charts
# Combines small wedges into an "other" category
# Removes wedges with value 0.
# Returns updated axis data and a list of labels that includes the other category label if it exists
def _roll_up_small_pie_wedges(ax_data, min_percentage):
    resource_list = list(ax_data.keys())
    total_resources = sum(ax_data.values())

    small_categories = []
    other_category_value = 0
    other_category_label = ''
    for resource in resource_list:
        percentage = round(ax_data[resource]/total_resources*100, 1)
        if percentage == 0.0:
            ax_data.pop(resource)
        elif percentage <= min_percentage:
            small_categories.append(resource)
            other_category_label += '{0} {1}%\n'.format(RESOURCE_LABELS[resource], percentage)
            other_category_value += ax_data[resource]
    
    if len(small_categories) > 1:
        for resource in small_categories:
            ax_data.pop(resource)

    labels = [RESOURCE_LABELS[resource] for resource in ax_data.keys()]
    
    if len(small_categories) > 1:
        ax_data['other'] = other_category_value
        labels.append(other_category_label)

    return ax_data, labels

def _construct_pie_visuals(zone, ax_data_list):
    rows = int(len(ax_data_list)/2)
    fig, axes = plt.subplots(rows, 2, figsize=(20, 12*rows))
    if rows > 1:
        axes = np.concatenate(axes)
    plt.suptitle(zone, fontsize=36, verticalalignment="bottom")

    for ax_data, ax in zip(ax_data_list, axes):
        df = pd.DataFrame({'': ax_data['values']}, index=ax_data['labels']) 
        df.plot(kind='pie', ax=ax, subplots=True, fontsize=18, autopct='%1.1f%%', startangle=180, pctdistance=.55, colors=ax_data['colors'], wedgeprops={'edgecolor':'white', 'linewidth': 6})
        ax.set_title(ax_data['title'], fontsize=30)
        ax.get_legend().remove()
        ax.tick_params(axis='y', which='both', left=False)
        ax.add_artist(plt.Circle((0,0),0.70,fc='white'))
        ax.text(0,0, '{0}\n{1}'.format(round(sum(ax_data['values']), 1), ax_data['unit']), fontsize=22, verticalalignment='center', horizontalalignment='center', weight="bold", color='lightgray')

    plt.tight_layout()
    fig.subplots_adjust(hspace = -.2)