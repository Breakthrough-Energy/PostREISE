import matplotlib.pyplot as plt
import pandas as pd


def plot_tornado(title, data, sorted=False):
    """
    Plots a tornado graph (horizontal bar with both positive and neg values)

    :param str title: Title of the plot
    :param dict data: dictionary of data to be plotted
    :param bool sorted: whether the values should be sorted smallest to largest
    """
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

    for (p, resource) in zip(ax.patches, list(df.index)):
        b = p.get_bbox()
        x_pos = b.x1 if b.x1 >= 0 else b.x0
        val = "%.2e" % b.x1
        ax.annotate(
            f" {resource}: {val} ", (x_pos, b.y1), fontsize=12, verticalalignment="top"
        )
    plt.show()
