import os

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
from powersimdata.network.model import ModelImmutables
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state

from postreise.analyze.demand import get_demand_time_series, get_net_demand_time_series
from postreise.analyze.generation.capacity import (
    get_capacity_by_resources,
    get_storage_capacity,
)
from postreise.analyze.generation.curtailment import get_curtailment_time_series
from postreise.analyze.generation.summarize import (
    get_generation_time_series_by_resources,
    get_storage_time_series,
)
from postreise.analyze.time import (
    change_time_zone,
    resample_time_series,
    slice_time_series,
)


def plot_generation_time_series_stack(
    scenario,
    area,
    resources,
    area_type=None,
    time_range=None,
    time_zone="utc",
    time_freq="H",
    show_demand=True,
    show_net_demand=True,
    normalize=False,
    t2c=None,
    t2l=None,
    t2hc=None,
    title=None,
    label_fontsize=20,
    title_fontsize=22,
    tick_fontsize=15,
    legend_fontsize=18,
    save=False,
    filename=None,
    filepath=None,
):
    """Generate time series generation stack plot in a certain area of a scenario.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str/list resources: one or a list of resources. *'solar_curtailment'*,
        *'wind_curtailment'*, *'wind_offshore_curtailment'* are valid entries together
        with all available generator types in the area. The order of the resources
        determines the stack order in the figure.
    :param str area_type: one of *'loadzone'*, *'state'*, *'state_abbr'*,
        *'interconnect'*
    :param tuple time_range: [start_timestamp, end_timestamp] where each time stamp
        is pandas.Timestamp/numpy.datetime64/datetime.datetime. If None, the entire
        time range is used for the given scenario.
    :param str time_zone: new time zone.
    :param str time_freq: frequency. Either *'D'* (day), *'W'* (week), *'M'* (month).
    :param bool show_demand: show demand line in the plot or not, default is True.
    :param bool show_net_demand: show net demand line in the plot or not, default is
        True.
    :param bool normalize: normalize the generation based on capacity or not,
        default is False.
    :param dict t2c: user specified color of resource type to overwrite type2color
        default dict. key: resource type, value: color code.
    :param dict t2l: user specified label of resource type to overwrite type2label
        default dict. key: resource type, value: label.
    :param dict t2hc: user specified color of curtailable resource hatches to overwrite
        type2hatchcolor default dict. key: resource type, valid keys are
        *'wind_curtailment'*, *'solar_curtailment'*, *'wind_offshore_curtailment'*,
        value: color code.
    :param str title: user specified title of the figure, default is set to be area.
    :param float label_fontsize: user specified label fontsize, default is 20.
    :param float title_fontsize: user specified title fontsize, default is 22.
    :param float tick_fontsize: user specified ticks of axes fontsize, default is 15.
    :param float legend_fontsize: user specified legend fontsize, default is 18.
    :param bool save: save the generated figure or not, default is False.
    :param str filename: if save is True, user specified filename, use area if None.
    :param str filepath: if save is True, user specified filepath, use current
        directory if None.
    """
    _check_scenario_is_in_analyze_state(scenario)

    mi = ModelImmutables(scenario.info["grid_model"])
    type2color = mi.plants["type2color"]
    type2label = mi.plants["type2label"]
    type2hatchcolor = mi.plants["type2hatchcolor"]
    if t2c:
        type2color.update(t2c)
    if t2l:
        type2label.update(t2l)
    if t2hc:
        type2hatchcolor.update(t2hc)

    pg_stack = get_generation_time_series_by_resources(
        scenario, area, resources, area_type=area_type
    )
    capacity = get_capacity_by_resources(scenario, area, resources, area_type=area_type)
    demand = get_demand_time_series(scenario, area, area_type=area_type)
    net_demand = get_net_demand_time_series(scenario, area, area_type=area_type)
    capacity_ts = pd.Series(capacity.sum(), index=pg_stack.index)

    curtailable_resources = {
        "solar_curtailment",
        "wind_curtailment",
        "wind_offshore_curtailment",
    }
    if curtailable_resources & set(resources):
        curtailment = get_curtailment_time_series(scenario, area, area_type=area_type)
        for r in curtailable_resources:
            if r in resources and r in curtailment.columns:
                pg_stack[r] = curtailment[r]

    pg_stack = change_time_zone(pg_stack, time_zone)
    demand = change_time_zone(demand, time_zone)
    net_demand = change_time_zone(net_demand, time_zone)
    capacity_ts = change_time_zone(capacity_ts, time_zone)
    if not time_range:
        time_range = (
            pd.Timestamp(scenario.info["start_date"], tz="utc"),
            pd.Timestamp(scenario.info["end_date"], tz="utc"),
        )
    pg_stack = slice_time_series(pg_stack, time_range[0], time_range[1])
    demand = slice_time_series(demand, time_range[0], time_range[1])
    net_demand = slice_time_series(net_demand, time_range[0], time_range[1])
    capacity_ts = slice_time_series(capacity_ts, time_range[0], time_range[1])
    if time_freq != "H":
        pg_stack = resample_time_series(pg_stack, time_freq)
        demand = resample_time_series(demand, time_freq)
        net_demand = resample_time_series(net_demand, time_freq)
        capacity_ts = resample_time_series(capacity_ts, time_freq)

    if "storage" in resources:
        pg_storage = get_storage_time_series(scenario, area, area_type=area_type)
        capacity_storage = get_storage_capacity(scenario, area, area_type=area_type)
        capacity_storage_ts = pd.Series(capacity_storage, index=pg_storage.index)

        pg_storage = change_time_zone(pg_storage, time_zone)
        capacity_storage_ts = change_time_zone(capacity_storage_ts, time_zone)
        pg_storage = slice_time_series(pg_storage, time_range[0], time_range[1])
        capacity_storage_ts = slice_time_series(
            capacity_storage_ts, time_range[0], time_range[1]
        )
        if time_freq != "H":
            pg_storage = resample_time_series(pg_storage, time_freq)
            capacity_storage_ts = resample_time_series(capacity_storage_ts, time_freq)

        pg_stack["storage"] = pg_storage.clip(lower=0)
        capacity_ts += capacity_storage_ts

        fig, (ax, ax_storage) = plt.subplots(
            2,
            1,
            figsize=(20, 15),
            sharex="row",
            gridspec_kw={"height_ratios": [3, 1], "hspace": 0.02},
        )
        plt.subplots_adjust(wspace=0)
        if normalize:
            pg_storage = pg_storage.divide(capacity_storage_ts, axis="index")
            ax_storage.set_ylabel("Normalized Storage", fontsize=label_fontsize)
        else:
            ax_storage.set_ylabel("Energy Storage (MW)", fontsize=label_fontsize)

        pg_storage.plot(color=type2color["storage"], lw=4, ax=ax_storage)
        ax_storage.fill_between(
            pg_storage.index,
            0,
            pg_storage.values,
            color=type2color["storage"],
            alpha=0.5,
        )

        # Erase year in xticklabels
        xt_with_year = list(ax_storage.__dict__["date_axis_info"][0])
        xt_with_year[-1] = b"%b"
        ax_storage.__dict__["date_axis_info"][0] = tuple(xt_with_year)

        ax_storage.tick_params(axis="both", which="both", labelsize=tick_fontsize)
        ax_storage.set_xlabel("")
        for a in fig.get_axes():
            a.label_outer()
    else:
        fig = plt.figure(figsize=(20, 10))
        ax = fig.gca()

    if normalize:
        pg_stack = pg_stack.divide(capacity_ts, axis="index")
        demand = demand.divide(capacity_ts, axis="index")
        net_demand = net_demand.divide(capacity_ts, axis="index")
        ax.set_ylabel("Normalized Generation", fontsize=label_fontsize)
    else:
        pg_stack = pg_stack.divide(1e6, axis="index")
        demand = demand.divide(1e6, axis="index")
        net_demand = net_demand.divide(1e6, axis="index")
        ax.set_ylabel("Daily Energy TWh", fontsize=label_fontsize)

    available_resources = [r for r in resources if r in pg_stack.columns]
    pg_stack[available_resources].clip(0, None).plot.area(
        color=type2color, linewidth=0, alpha=0.7, ax=ax, sharex="row"
    )

    if show_demand:
        demand.plot(color="red", lw=4, ax=ax)
    if show_net_demand:
        net_demand.plot(color="red", ls="--", lw=2, ax=ax)

    if not title:
        title = area
    ax.set_title("%s" % title, fontsize=title_fontsize)
    ax.grid(color="black", axis="y")

    if "storage" not in resources:
        # Erase year in xticklabels
        xt_with_year = list(ax.__dict__["date_axis_info"][0])
        xt_with_year[-1] = b"%b"
        ax.__dict__["date_axis_info"][0] = tuple(xt_with_year)
        ax.set_xlabel("")

    ax.tick_params(which="both", labelsize=tick_fontsize)
    ax.set_ylim(
        [
            min(0, 1.1 * net_demand.min()),
            max(ax.get_ylim()[1], 1.1 * demand.max()),
        ]
    )

    handles, labels = ax.get_legend_handles_labels()
    if show_demand:
        labels[0] = "Demand"
    if show_net_demand:
        labels[1] = "Net Demand"
    label_offset = show_demand + show_net_demand
    labels = [type2label[l] if l in type2label else l for l in labels]

    # Add hatches
    for r in curtailable_resources:
        if r in available_resources:
            ind = available_resources.index(r)
            ax.fill_between(
                pg_stack[available_resources].index,
                pg_stack[available_resources].iloc[:, : ind + 1].sum(axis=1),
                pg_stack[available_resources].iloc[:, :ind].sum(axis=1),
                color="none",
                hatch="//",
                edgecolor=type2hatchcolor[r],
                linewidth=0.0,
            )
            handles[ind + label_offset] = mpatches.Patch(
                facecolor=type2color[r],
                hatch="//",
                edgecolor=type2hatchcolor[r],
                linewidth=0.0,
            )

    ax.legend(
        handles[::-1],
        labels[::-1],
        frameon=2,
        prop={"size": legend_fontsize},
        loc="upper left",
        bbox_to_anchor=(1, 1),
    )

    if save:
        if not filename:
            filename = area
        if not filepath:
            filepath = os.path.join(os.getcwd(), filename)
        plt.savefig(f"{filepath}.pdf", bbox_inches="tight", pad_inches=0)
