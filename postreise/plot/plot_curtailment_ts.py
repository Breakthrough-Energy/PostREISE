import os

import matplotlib.pyplot as plt
import pandas as pd
from powersimdata.input.check import _check_resources_and_format
from powersimdata.network.model import ModelImmutables
from powersimdata.scenario.check import _check_scenario_is_in_analyze_state

from postreise.analyze.demand import get_demand_time_series
from postreise.analyze.generation.curtailment import get_curtailment_time_series
from postreise.analyze.generation.summarize import (
    get_generation_time_series_by_resources,
)
from postreise.analyze.time import (
    change_time_zone,
    resample_time_series,
    slice_time_series,
)


def plot_curtailment_time_series(
    scenario,
    area,
    resources,
    area_type=None,
    time_range=None,
    time_zone="utc",
    time_freq="H",
    show_demand=True,
    percentage=True,
    t2c=None,
    t2l=None,
    title=None,
    label_fontsize=20,
    title_fontsize=22,
    tick_fontsize=15,
    legend_fontsize=18,
    save=False,
    filename=None,
    filepath=None,
):
    """Generate time series curtailment plot of each specified resource in a certain
    area of a scenario.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance
    :param str area: one of *loadzone*, *state*, *state abbreviation*,
        *interconnect*, *'all'*
    :param str/list resources: one or a list of resources.
    :param str area_type: one of *'loadzone'*, *'state'*, *'state_abbr'*,
        *'interconnect'*
    :param tuple time_range: [start_timestamp, end_timestamp] where each time stamp
        is pandas.Timestamp/numpy.datetime64/datetime.datetime. If None, the entire
        time range is used for the given scenario.
    :param str time_zone: new time zone.
    :param str time_freq: frequency. Either *'D'* (day), *'W'* (week), *'M'* (month).
    :param bool show_demand: show demand line in the plot or not, default is True.
    :param bool percentage: plot the curtailment in terms of percentage or not,
        default is True.
    :param dict t2c: user specified color of resource type to overwrite type2color
        default dict. key: resource type, value: color code.
    :param dict t2l: user specified label of resource type to overwrite type2label
        default dict. key: resource type, value: label.
    :param str title: user specified title of the figure.
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
    resources = _check_resources_and_format(
        resources, grid_model=scenario.info["grid_model"]
    )

    mi = ModelImmutables(scenario.info["grid_model"])
    type2color = mi.plants["type2color"]
    type2label = mi.plants["type2label"]
    if t2c:
        type2color.update(t2c)
    if t2l:
        type2label.update(t2l)

    resource_pg = get_generation_time_series_by_resources(
        scenario, area, resources, area_type=area_type
    )
    demand = get_demand_time_series(scenario, area, area_type=area_type)
    curtailment = get_curtailment_time_series(scenario, area, area_type=area_type)

    resource_pg = change_time_zone(resource_pg, time_zone)
    demand = change_time_zone(demand, time_zone)
    curtailment = change_time_zone(curtailment, time_zone)
    if not time_range:
        time_range = (
            pd.Timestamp(scenario.info["start_date"], tz="utc"),
            pd.Timestamp(scenario.info["end_date"], tz="utc"),
        )
    resource_pg = slice_time_series(resource_pg, time_range[0], time_range[1])
    demand = slice_time_series(demand, time_range[0], time_range[1])
    curtailment = slice_time_series(curtailment, time_range[0], time_range[1])
    if time_freq != "H":
        resource_pg = resample_time_series(resource_pg, time_freq)
        demand = resample_time_series(demand, time_freq)
        curtailment = resample_time_series(curtailment, time_freq)

    for r in resource_pg.columns:
        curtailment[r + "_curtailment" + "_mean"] = curtailment[
            r + "_curtailment"
        ].mean()
        curtailment[r + "_available"] = curtailment[r + "_curtailment"] + resource_pg[r]
        curtailment[r + "_curtailment" + "_percentage"] = (
            curtailment[r + "_curtailment"] / curtailment[r + "_available"] * 100
        )
        curtailment[r + "_curtailment" + "_percentage" + "_mean"] = curtailment[
            r + "_curtailment" + "_percentage"
        ].mean()

    for r in resources:
        if r not in resource_pg.columns:
            raise ValueError(f"{r} is invalid in {area}!")
        fig = plt.figure(figsize=(20, 10))
        ax = fig.gca()

        title_text = f"{area} {r.capitalize()}" if not title else title
        plt.title(title_text, fontsize=title_fontsize)

        cr = r + "_curtailment"
        if percentage:
            key1, key2 = f"{cr}_percentage", f"{cr}_percentage_mean"
        else:
            key1, key2 = cr, f"{cr}_mean"
        curtailment[key1].plot(
            ax=ax,
            lw=4,
            alpha=0.7,
            color=type2color[cr],
            label=type2label[cr],
        )
        curtailment[key2].plot(
            ax=ax,
            ls="--",
            lw=4,
            alpha=0.7,
            color=type2color[cr],
            label=type2label[cr] + " Mean",
        )

        ax_twin = ax.twinx()
        curtailment[r + "_available"].plot(
            ax=ax_twin,
            lw=4,
            alpha=0.7,
            color=type2color[r],
            label=f"{type2label[r]} Energy Available",
        )

        if show_demand:
            demand.plot(ax=ax_twin, lw=4, alpha=0.7, color="red", label="Demand")

        # Erase year in xticklabels
        xt_with_year = list(ax_twin.__dict__["date_axis_info"][0])
        xt_with_year[-1] = b"%b"
        ax_twin.__dict__["date_axis_info"][0] = tuple(xt_with_year)
        ax_twin.set_xlabel("")
        ax_twin.tick_params(which="both", labelsize=tick_fontsize)
        ax_twin.yaxis.get_offset_text().set_fontsize(tick_fontsize)
        ax_twin.set_ylabel("MWh", fontsize=label_fontsize)
        ax_twin.legend(loc="upper right", prop={"size": legend_fontsize})

        ax.tick_params(which="both", labelsize=tick_fontsize)
        ax.yaxis.get_offset_text().set_fontsize(tick_fontsize)
        ax.grid(color="black", axis="y")
        ax.set_xlabel("")
        if percentage:
            ax.set_ylabel("Curtailment [%]", fontsize=label_fontsize)
        else:
            ax.set_ylabel("Curtailment", fontsize=label_fontsize)
        ax.legend(loc="upper left", prop={"size": legend_fontsize})

        if save:
            if not filename:
                filename = f"{area.lower()}_{r}_curtailment"
            if not filepath:
                filepath = os.path.join(os.getcwd(), filename)
            plt.savefig(f"{filepath}.pdf", bbox_inches="tight", pad_inches=0)
