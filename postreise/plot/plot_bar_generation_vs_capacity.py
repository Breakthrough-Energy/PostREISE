import matplotlib.pyplot as plt
import pandas as pd
from powersimdata.network.model import ModelImmutables, area_to_loadzone
from powersimdata.scenario.scenario import Scenario

from postreise.analyze.generation.capacity import sum_capacity_by_type_zone
from postreise.analyze.generation.summarize import sum_generation_by_type_zone


def plot_bar_generation_vs_capacity(
    areas,
    area_types=None,
    scenario_ids=None,
    scenario_names=None,
    time_range=None,
    time_zone=None,
    custom_data=None,
    resource_types=None,
    resource_labels=None,
    horizontal=False,
):
    """Plot any number of scenarios as bar or horizontal bar charts with two columns per
    scenario - generation and capacity.

    :param list/str areas: list of area(s), each area is one of *loadzone*, *state*,
        *state abbreviation*, *interconnect*, *'all'*.
    :param list/str area_types: list of area_type(s), each area_type is one of
        *'loadzone'*, *'state'*, *'state_abbr'*, *'interconnect'*, defaults to None.
    :param int/list/str scenario_ids: list of scenario id(s), defaults to None.
    :param list/str scenario_names: list of scenario name(s) of same len as scenario
        ids, defaults to None.
    :param tuple time_range: [start_timestamp, end_timestamp] where each time stamp
        is pandas.Timestamp/numpy.datetime64/datetime.datetime. If None, the entire
        time range is used for the given scenario.
    :param str time_zone: new time zone, defaults to None, which uses UTC.
    :param list custom_data: list of dictionaries with each element being
        hand-generated data as returned by :func:`make_gen_cap_custom_data`, defaults
        to None.
    :param list/str resource_types: list of resource type(s) to show, defaults to None,
        which shows all available resources in the area of the corresponding scenario.
    :param dict resource_labels: a dictionary with keys being resource_types and values
        being labels to show in the plots, defaults to None, which uses
        resource_types as labels.
    :param bool horizontal: display bars horizontally, default to False.
    """
    if isinstance(areas, str):
        areas = [areas]
    if isinstance(area_types, str):
        area_types = [area_types]
    if not area_types:
        area_types = [None] * len(areas)
    if len(areas) != len(area_types):
        raise ValueError(
            "ERROR: if area_types are provided, it should have the same number of entries with areas."
        )

    if not scenario_ids:
        scenario_ids = []
    if isinstance(scenario_ids, (int, str)):
        scenario_ids = [scenario_ids]
    if isinstance(scenario_names, str):
        scenario_names = [scenario_names]
    if scenario_names and len(scenario_names) != len(scenario_ids):
        raise ValueError(
            "ERROR: if scenario names are provided, number of scenario names must match number of scenario ids"
        )
    if not custom_data:
        custom_data = {}
    if len(scenario_ids) + len(custom_data) <= 1:
        raise ValueError(
            "ERROR: must include at least two scenario ids and/or custom data"
        )
    if isinstance(resource_types, str):
        resource_types = [resource_types]
    if not resource_labels:
        resource_labels = dict()
    if not isinstance(resource_labels, dict):
        raise TypeError("ERROR: resource_labels should be a dictionary")

    all_loadzone_data = {}
    scenario_data = {}
    for i, sid in enumerate(scenario_ids):
        scenario = Scenario(sid)
        mi = ModelImmutables(scenario.info["grid_model"])
        all_loadzone_data[sid] = {
            "gen": sum_generation_by_type_zone(scenario, time_range, time_zone).rename(
                columns=mi.zones["id2loadzone"]
            ),
            "cap": sum_capacity_by_type_zone(scenario).rename(
                columns=mi.zones["id2loadzone"]
            ),
        }
        scenario_data[sid] = {
            "name": scenario_names[i] if scenario_names else scenario.info["name"],
            "grid_model": mi.model,
            "gen": {"label": "Generation", "unit": "TWh", "data": {}},
            "cap": {"label": "Capacity", "unit": "GW", "data": {}},
        }
    for area, area_type in zip(areas, area_types):
        for sid in scenario_ids:
            loadzone_set = area_to_loadzone(
                scenario_data[sid]["grid_model"], area, area_type
            )
            scenario_data[sid]["gen"]["data"][area] = (
                all_loadzone_data[sid]["gen"][loadzone_set]
                .sum(axis=1)
                .divide(1e6)
                .astype("float")
                .round(2)
                .to_dict()
            )
            scenario_data[sid]["cap"]["data"][area] = (
                all_loadzone_data[sid]["cap"][loadzone_set]
                .sum(axis=1)
                .divide(1e3)
                .astype("float")
                .round(2)
                .to_dict()
            )
    for c_data in custom_data:
        scenario_data[c_data["name"]] = c_data

    for area in areas:
        if not resource_types:
            area_resource_types = sorted(
                set(
                    r
                    for sd in scenario_data.values()
                    for side in ["gen", "cap"]
                    for r, v in sd[side]["data"][area].items()
                    if v > 0
                )
            )
        else:
            area_resource_types = resource_types

        ax_data_list = []
        for side in ["gen", "cap"]:
            ax_data = {}
            for sd in scenario_data.values():
                # If we don't have data for a resource type, set it to 0
                ax_data[sd["name"]] = [
                    sd[side]["data"][area].get(r, 0) for r in area_resource_types
                ]
            ax_data_list.append(
                {
                    "title": f"""{sd[side]["label"]} ({sd[side]["unit"]})""",
                    "labels": [resource_labels.get(r, r) for r in area_resource_types],
                    "values": ax_data,
                    "unit": sd[side]["unit"],
                }
            )

        if horizontal:
            _construct_hbar_visuals(area, ax_data_list)
        else:
            _construct_bar_visuals(area, ax_data_list)


def _construct_bar_visuals(zone, ax_data_list):
    """Plot bar chart based on formatted data.

    :param str zone: the zone name
    :param list ax_data_list: a list of labels and values for each axis of the plot
    """
    num_scenarios = len(ax_data_list[0]["values"].keys())
    num_resource_types = len(ax_data_list[0]["labels"])

    fig, axes = plt.subplots(
        1, 2, figsize=(1.5 * num_scenarios * num_resource_types, 6)
    )
    plt.suptitle(zone, fontsize=30, verticalalignment="bottom")
    plt.subplots_adjust(wspace=3 / (num_scenarios * num_resource_types))

    for ax_data, ax in zip(ax_data_list, axes):
        df = pd.DataFrame(ax_data["values"], index=ax_data["labels"])
        df.plot(kind="bar", ax=ax, edgecolor="white", linewidth=2)
        ax.set_title(ax_data["title"], fontsize=25)

        ax.tick_params(axis="both", which="both", labelsize=20)
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.set_xlabel("")
        ax.set_xticklabels(
            ax.get_xticklabels(), rotation=45, horizontalalignment="right"
        )
        ax.set_yticks([])
        ax.set_ylim(top=1.3 * ax.get_ylim()[1])

        ax.legend(bbox_to_anchor=(-0.03, -0.4), loc="upper left", fontsize=16)

        for p in ax.patches:
            b = p.get_bbox()
            ax.annotate(
                _get_bar_display_val(b.y1),
                ((b.x1 + b.x0) / 2, b.y1 + 0.02 * ax.get_ylim()[1]),
                fontsize=10,
                rotation="horizontal",
                horizontalalignment="center",
            )

    axes[1].get_legend().remove()
    plt.show()


def _construct_hbar_visuals(zone, ax_data_list):
    """Plot horizontal bar chart based on formatted data.

    :param str zone: the zone name.
    :param list ax_data_list: a list of labels and values for each axis of the plot
    """
    num_scenarios = len(ax_data_list[0]["values"].keys())
    num_resource_types = len(ax_data_list[0]["labels"])

    fig, axes = plt.subplots(
        1, 2, figsize=(20, 0.7 * num_scenarios * num_resource_types)
    )
    plt.suptitle(zone, fontsize=30, verticalalignment="bottom")
    plt.subplots_adjust(wspace=1)

    for ax_data, ax in zip(ax_data_list, axes):
        df = pd.DataFrame(ax_data["values"], index=ax_data["labels"])
        df.plot(kind="barh", ax=ax, edgecolor="white", linewidth=2)
        ax.set_title(ax_data["title"], fontsize=25)

        ax.tick_params(axis="y", which="both", labelsize=20)
        ax.set_xticklabels("")
        ax.set_ylabel("")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.set_xticks([])

        handles, labels = ax.get_legend_handles_labels()
        ax.legend(
            reversed(handles),
            reversed(labels),
            bbox_to_anchor=(-0.03, 0),
            loc="upper left",
            fontsize=16,
        )

        for p in ax.patches:
            b = p.get_bbox()
            ax.annotate(
                _get_bar_display_val(b.x1),
                (b.x1, b.y1 - 0.02),
                fontsize=14,
                verticalalignment="top",
            )
    plt.show()


def _get_bar_display_val(val):
    """Format the display value for a single bar.

    :param float val: the original value.
    :return: (*int/float*) -- the formatted value.
    """
    if val >= 10:
        return int(round(val, 0))

    rounded = round(val, 1)
    return rounded if rounded > 0 else 0


def make_gen_cap_custom_data(areas, label, gen_data=None, cap_data=None):
    """Format custom data for :func:`plot_bar_generation_vs_capacity`.

    :param list/str areas: list of interest area(s).
    :param str label: the name of the custom scenario to be shown in the plot.
    :param pandas.DataFrame gen_data: generation data with rows being resource types
        and columns being areas in TWh, default to None.
    :param pandas.DataFrame cap_data: capacity data with rows being reousrce types
        and columns being areas in GW, defaults to None
    :return: (*dict*) --  formatted custom data.
    """
    if isinstance(areas, str):
        areas = [areas]
    if gen_data is None:
        gen_data = pd.DataFrame()
    if cap_data is None:
        cap_data = pd.DataFrame()

    gen = dict()
    cap = dict()
    for area in areas:
        if area in gen_data.columns:
            gen.update(gen_data[[area]].round(2).to_dict())
        else:
            gen[area] = {}
        if area in cap_data.columns:
            cap.update(cap_data[[area]].round(2).to_dict())
        else:
            cap[area] = {}

    return {
        "name": label,
        "gen": {"label": "Generation", "unit": "TWh", "data": gen},
        "cap": {"label": "Capacity", "unit": "GW", "data": cap},
    }
