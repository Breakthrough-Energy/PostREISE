import datetime as dt

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from powersimdata.input.check import _check_time_series

from postreise.analyze.time import change_time_zone


def plot_heatmap(
    series,
    time_zone=None,
    time_zone_label=None,
    title=None,
    cmap="PiYG",
    scale=None,
    save_filename=None,
    origin="upper",
    vmin=None,
    vmax=None,
    cbar_format=None,
    cbar_tick_values=None,
    cbar_label=None,
    cbar_tick_labels=None,
    contour_levels=None,
    figsize=(16, 8),
):
    """Show time-series values via an imshow where each column is one color-coded day.

    :param pandas.Series series: a time-series of values to be color-coded.
    :param str time_zone: a time zone to be passed as `tz` kwarg to
        :func:`postreise.analyze.time.change_time_zone`.
    :param str time_zone_label: a time zone label to be added to the y axis label.
    :param str title: a title to be added to the figure.
    :param str/matplotlib.colors.Colormap cmap: colormap specification to be passed
        as `cmap` kwarg to :func:`matplotlib.pyplot.imshow`.
    :param int/float scale: a scaling factor to be applied to the series values.
    :param str save_filename: a path to save the figure to.
    :param str origin: the vertical location of the origin, either "upper" or "lower".
    :param int/float vmin: Minimum value for coloring, to be passed as `vmin` kwarg to
        :func:`matplotlib.pyplot.imshow`.
    :param int/float vmax: Maximum value for coloring, to be passed as `vmax` kwarg to
        :func:`matplotlib.pyplot.imshow`.
    :param str/matplotlib.ticker.Formatter cbar_format: a formatter for colorbar labels,
        to be passed as `format` kwarg to :func:`matplotlib.pyplot.colorbar`.
    :param iterable cbar_tick_values: colorbar tick locations, to be passed as
        `ticks` kwarg to :func:`matplotlib.pyplot.colorbar`.
    :param str cbar_label: axis label for colorbar.
    :param iterable cbar_tick_labels: colorbar tick labels.
    :param iterable contour_levels: values at which to draw contours, passed as `levels`
        kwarg to :func:`matplotlib.pyplot.contour`.
    :param tuple(int/float, int/float) figsize: size of figure.
    """
    _check_time_series(series, "series")
    df = series.to_frame(name="values").asfreq("H")
    year = df.index[0].year
    if time_zone is not None:
        df = change_time_zone(df, time_zone)
    df["date"] = df.index.date
    df["hour"] = df.index.hour
    df_reshaped = pd.pivot(
        df,
        index="date",
        columns="hour",
        values="values",
    )
    xlims = mdates.date2num([df_reshaped.index[0], df_reshaped.index[-1]])
    ylims = mdates.date2num([dt.datetime(year, 1, 1, 0), dt.datetime(year, 1, 1, 23)])

    if scale is not None:
        df_reshaped *= scale

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot()

    # if necessary, flip ylims so labels follow data from top to bottom
    extent = [*xlims, *ylims] if origin == "lower" else [*xlims, ylims[1], ylims[0]]
    im = plt.imshow(
        df_reshaped.T,
        cmap=cmap,
        aspect="auto",
        extent=extent,
        origin=origin,
        vmin=vmin,
        vmax=vmax,
    )
    if contour_levels is not None:
        ax.contour(df_reshaped.T, extent=extent, levels=contour_levels, origin=origin)

    date_format = mdates.DateFormatter("%m/%d")
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(date_format)
    ax.set_xlabel("Date")
    time_format = mdates.DateFormatter("%H:%M")
    ax.yaxis_date()
    ax.yaxis.set_major_formatter(time_format)
    y_axis_label = "Time" if time_zone_label is None else f"Time {time_zone_label}"
    ax.set_ylabel(y_axis_label)

    cbar = fig.colorbar(im, format=cbar_format, ticks=cbar_tick_values)
    if cbar_label is not None:
        cbar.set_label(cbar_label)
    if title is not None:
        plt.title(title)
    if cbar_tick_labels is not None:
        cbar.ax.set_yticklabels(cbar_tick_labels)

    if save_filename is not None:
        plt.savefig(save_filename, bbox_inches="tight")
