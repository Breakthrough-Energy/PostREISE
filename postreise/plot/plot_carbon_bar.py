from matplotlib import pyplot as plt
import numpy as np


def plot_carbon_bar(carbon_by_bus_1, carbon_by_bus_2,
                    scenario_name_1, scenario_name_2):
    """Makes bar chart of carbon emissions by fuel type for two scenarios.

    :param dict carbon_by_bus_1: emission by type and bus for first scenario
        as returned by :func:`postreise.analyze.carbon.summarize_carbon_by_bus`.
    :param dict carbon_by_bus_2: emission by type and bus, for second scenario
        as returned by :func:`postreise.analyze.carbon.summarize_carbon_by_bus`.
    :param str scenario_name_1: name of first scenario, for labeling plot.
    :param str scenario_name_2: name of second scenario, for labeling plot.
    """
    plt.rcParams.update({'font.size': 22})
    objects = (scenario_name_1, scenario_name_2)
    y_pos = np.arange(len(objects))

    carbon_val = [sum(carbon_by_bus_1['coal'].values()),
                  sum(carbon_by_bus_2['coal'].values())]
    _ = plt.figure(figsize=(7, 2))
    plt.barh(y_pos, carbon_val, align='center', alpha=0.25, color=['black'])
    plt.yticks(y_pos, objects)
    plt.xticks(np.arange(0, 2.1e8, .5e8))
    plt.xlabel('Tons')
    plt.title('Coal: CO$_2$  Emissions', y=1.04)
    plt.show()

    ng_val = [sum(carbon_by_bus_1['ng'].values()),
              sum(carbon_by_bus_2['ng'].values())]

    _ = plt.figure(figsize=(7, 2))
    plt.barh(y_pos, ng_val, align='center', alpha=0.25, color=['purple'])
    plt.yticks(y_pos, objects)
    plt.xticks(np.arange(0, 2.1e8, .5e8))
    plt.xlabel('Tons')
    plt.title('Natural Gas: CO$_2$ Emissions', y=1.04)
    plt.show()


def print_carbon_diff(carbon_by_bus_1, carbon_by_bus_2):
    """Prints percentage change in carbon emissions of two scenarios.

    :param dict carbon_by_bus_1: emission by type and bus for first scenario as
        returned by :func:`postreise.analyze.carbon.summarize_carbon_by_bus`.
    :param dict carbon_by_bus_2: emission by type and bus for second scenario
        as returned by :func:`postreise.analyze.carbon.summarize_carbon_by_bus`.
    """
    sum_1 = sum(carbon_by_bus_1['coal'].values()) + \
        sum(carbon_by_bus_1['ng'].values())
    sum_2 = sum(carbon_by_bus_2['coal'].values()) + \
        sum(carbon_by_bus_2['ng'].values())

    print("%d%%" % round(100*(1 - sum_2/sum_1), 2))
