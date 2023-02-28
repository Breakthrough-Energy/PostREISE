import pandas as pd
from matplotlib import pyplot as plt


def plot_tornado(title, data, sorted=False, plot_show=True):
    """Plots a tornado graph (horizontal bar with both positive and neg values)

    :param str title: title of the plot
    :param dict data: dictionary of data to be plotted
    :param bool sorted: whether the values should be sorted smallest to largest
    :param bool plot_show: show the plot or not, default to True.
    :return: (*matplotlib.axes.Axes*) -- axes object of the plot.
    :raises TypeError:
        if ``title`` is not a str.
        if ``data`` is not a dict, keys are not str and values are not int or float.
        if ``sorted`` is not a bool.
        if ``plot_show`` is not a bool.
    """
    if not isinstance(title, str):
        raise TypeError("title must be a str")
    if not isinstance(data, dict):
        raise TypeError("data must be a dict")
    if not all(isinstance(k, str) for k in data):
        raise TypeError("all keys of data must be str")
    if not all(isinstance(v, (int, float)) for v in data.values()):
        raise TypeError("all values of data must be int or float")
    if not isinstance(sorted, bool):
        raise TypeError("sorted must be a bool")
    if not isinstance(plot_show, bool):
        raise TypeError("plot_show must be a bool")

    df = pd.Series(data).to_frame()

    if sorted is True:
        df = df.sort_values(by=0, ascending=True)

    # Horizontal bar charts start at the bottom
    # so we reverse the row order before plotting
    df = df.iloc[::-1]
    ax = df.plot.barh(figsize=(10, len(df.index) * 0.4), legend=False)
    ax.set_title(title, fontsize=18)

    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axvline(x=0, color="black", lw=0.8)

    for p, resource in zip(ax.patches, list(df.index)):
        b = p.get_bbox()
        x_pos = b.x1 if b.x1 >= 0 else b.x0
        val = "%.2e" % b.x1
        ax.annotate(
            f" {resource}: {val} ", (x_pos, b.y1), fontsize=12, verticalalignment="top"
        )

    if plot_show:
        plt.show()

    return ax
