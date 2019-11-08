from matplotlib import pyplot as plt
import numpy as np


def plot_carbon_bar(emitter1, emitter2, name1, name2):
    """Makes bar chart of carbon emissions by fuel type for two scenarios.\
    :param dict emitter1: carbon emissions by type and bus for first scenario.
    :param dict emitter2: carbon emissions by type and bus, for second scenario.
    :param str name1: name of first scenario, for labeling plot.
    :param str name2: name of second scenario, for labeling plot.
    """
    plt.rcParams.update({'font.size': 22})
    objects = (name1, name2)
    y_pos = np.arange(len(objects))
    carbon_val = [sum(emitter1['coal'].values()),
                  sum(emitter2['coal'].values())]

    plt.barh(y_pos, carbon_val, align='center', alpha=0.25, color=['black'])

    plt.yticks(y_pos, objects)
    plt.xticks(np.arange(0, 2.1e8, .5e8))
    plt.xlabel('Tons')
    plt.title('Coal: C$O_2$  Emissions', y=1.04)
    plt.show()

    objects = ('2030 all match CA', '2016 base')
    y_pos = np.arange(len(objects))
    carbon_val = [sum(emitter1['ng'].values()), sum(emitter2['ng'].values())]

    plt.barh(y_pos, carbon_val, align='center', alpha=0.25, color=['purple'])

    plt.yticks(y_pos, objects)
    plt.xticks(np.arange(0, 2.1e8, .5e8))
    plt.xlabel('Tons')
    plt.title('Natural Gas: C$O_2$ Emissions', y=1.04)
    plt.show()


def print_carbon_diff(emitter1, emitter2):
    """Prints percentage change in carbon emissions of two scenarios.

    :param dict emitter1: carbon emissions by type and bus for first scenario.
    :param dict emitter2: carbon emissions by type and bus for second scenario.
    """
    sum1 = sum(emitter1['coal'].values()) + sum(emitter1['ng'].values())
    sum2 = sum(emitter2['coal'].values()) + sum(emitter2['ng'].values())
    print("%d%%" % round(100*(1 - sum2/sum1), 2))
