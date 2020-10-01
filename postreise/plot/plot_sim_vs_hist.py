import warnings

import matplotlib.pyplot as plt
import numpy as np


class PlotSettings:
    width = 0.3  # width of bars
    fontsize = 15
    size_inches = (20, 10)


def plot_generation_sim_vs_hist(sim_gen, hist_gen, s_info, state, showmax=True):
    """
    Plot simulated vs historical generation of each resource in the scenario
    for the given state. Optionally include max generation.

    :param pandas.DataFrame sim_gen: simulated generation dataframe
    :param pandas.DataFrame hist_gen: historical generation dataframe
    :param powersimdata.design.ScenarioInfo s_info: scenario info instance.
    :param str state: the US state
    :param bool showmax: determine whether to additionally plot max generation of each resource
    """
    labels = list(sim_gen.columns)
    all_resources = s_info.get_available_resource("all")

    sim = [int(round(sim_gen.loc[state, res])) for res in all_resources]
    hist = [int(round(hist_gen.loc[state, res])) for res in all_resources]

    def calc_max(gen_type):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return int(
                s_info.get_capacity(gen_type, state) * len(s_info.pg.index) / 1000
            )

    max_gen = []
    if showmax:
        max_gen = [calc_max(res) for res in all_resources]

    x = np.arange(len(labels))  # the label locations
    width = PlotSettings.width
    fontsize = PlotSettings.fontsize
    size_inches_x, size_inches_y = PlotSettings.size_inches

    fig, ax = plt.subplots()
    if showmax:
        rects1 = ax.bar(x - width, hist, width, label="Historical")
        rects2 = ax.bar(x, sim, width, label="Simulated")
        rects3 = ax.bar(x + width, max_gen, width, label="Max Generation")
    else:
        rects1 = ax.bar(x - width / 2, hist, width, label="Historical")
        rects2 = ax.bar(x + width / 2, sim, width, label="Simulated")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("GWh", fontsize=fontsize)
    ax.set_title(state, fontsize=fontsize)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=fontsize)
    ax.legend(fontsize=fontsize)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                str(height),
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    autolabel(rects1)
    autolabel(rects2)
    if showmax:
        autolabel(rects3)
    fig.tight_layout()
    fig.set_size_inches(size_inches_x, size_inches_y)
    plt.show()
