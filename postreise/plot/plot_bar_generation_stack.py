import os

import matplotlib.pyplot as plt
import pandas as pd
from powersimdata.network.model import ModelImmutables, area_to_loadzone
from powersimdata.scenario.scenario import Scenario

from postreise.analyze.generation.curtailment import (
    calculate_curtailment_time_series_by_areas_and_resources,
)
from postreise.analyze.generation.summarize import sum_generation_by_type_zone


def plot_bar_generation_stack(
    areas,
    scenario_ids,
    resources,
    area_types=None,
    scenario_names=None,
    curtailment_split=True,
    t2c=None,
    t2l=None,
    t2hc=None,
    titles=None,
    plot_show=True,
    save=False,
    filenames=None,
    filepath=None,
):
    """Plot any number of scenarios as generation stack bar for selected resources in
    each specified areas.

    :param list/str areas: list of area(s), each area is one of *loadzone*, *state*,
        *state abbreviation*, *interconnect*, *'all'*.
    :param int/list/str scenario_ids: list of scenario id(s), defaults to None.
    :param str/list resources: one or a list of resources. *'curtailment'*,
        *'solar_curtailment'*, *'wind_curtailment'*, *'wind_offshore_curtailment'*
        are valid entries together with all available generator types in the area(s).
        The order of the resources determines the stack order in the figure.
    :param list/str area_types: list of area_type(s), each area_type is one of
        *'loadzone'*, *'state'*, *'state_abbr'*, *'interconnect'*, defaults to None.
    :param list/str scenario_names: list of scenario name(s) of same len as scenario
        ids, defaults to None.
    :param bool curtailment_split: if curtailments are split into different
        categories, defaults to True.
    :param dict t2c: user specified color of resource type to overwrite pre-defined ones
        key: resource type, value: color code.
    :param dict t2l: user specified label of resource type to overwrite pre-defined ones
        key: resource type, value: label.
    :param dict t2hc: user specified color of curtailable resource hatches to overwrite
        pre-defined ones. key: resource type, valid keys are *'curtailment'*,
        *'solar_curtailment'*, *'wind_curtailment'*, *'wind_offshore_curtailment'*,
        value: color code.
    :param dict titles: user specified figure titles, key: area, value: new figure
        title in string, use area as title if None.
    :param bool plot_show: display the generated figure or not, defaults to True.
    :param bool save: save the generated figure or not, defaults to False.
    :param dict filenames: user specified filenames, key: area, value: new filename
        in string, use area as filename if None.
    :param str filepath: if save is True, user specified filepath, use current
        directory if None.
    :return: (*list*) -- matplotlib.axes.Axes object of each plot in a list.
    :raises TypeError:
        if resources is not a list/str and/or
        if titles is provided but not in a dictionary format and/or
        if filenames is provided but not in a dictionary format.
    :raises ValueError:
        if length of area_types and areas is different and/or
        if length of scenario_names and scenario_ids is different.
    """
    if isinstance(areas, str):
        areas = [areas]
    if isinstance(scenario_ids, (int, str)):
        scenario_ids = [scenario_ids]
    if not isinstance(scenario_ids, list):
        raise TypeError("ERROR: scenario_ids should be a int/str/list")
    if isinstance(resources, str):
        resources = [resources]
    if not isinstance(resources, list):
        raise TypeError("ERROR: resources should be a list/str")
    if isinstance(area_types, str):
        area_types = [area_types]
    if not area_types:
        area_types = [None] * len(areas)
    if len(areas) != len(area_types):
        raise ValueError(
            "ERROR: if area_types are provided, number of area_types must match number of areas"
        )
    if isinstance(scenario_names, str):
        scenario_names = [scenario_names]
    if scenario_names and len(scenario_names) != len(scenario_ids):
        raise ValueError(
            "ERROR: if scenario names are provided, number of scenario names must match number of scenario ids"
        )
    if titles is not None and not isinstance(titles, dict):
        raise TypeError("ERROR: titles should be a dictionary if provided")
    if filenames is not None and not isinstance(filenames, dict):
        raise TypeError("ERROR: filenames should be a dictionary if provided")
    s_list = []
    for sid in scenario_ids:
        s_list.append(Scenario(sid))
    mi = ModelImmutables(s_list[0].info["grid_model"])
    type2color = mi.plants["type2color"]
    type2label = mi.plants["type2label"]
    type2hatchcolor = mi.plants["type2hatchcolor"]
    if t2c:
        type2color.update(t2c)
    if t2l:
        type2label.update(t2l)
    if t2hc:
        type2hatchcolor.update(t2hc)
    all_loadzone_data = dict()
    for sid, scenario in zip(scenario_ids, s_list):
        curtailment = calculate_curtailment_time_series_by_areas_and_resources(
            scenario, areas={"loadzone": mi.zones["loadzone"]}
        )
        for area in curtailment:
            for r in curtailment[area]:
                curtailment[area][r] = curtailment[area][r].sum().sum()
        curtailment = (
            pd.DataFrame(curtailment).rename(columns=mi.zones["loadzone2id"]).T
        )
        curtailment.rename(
            columns={c: c + "_curtailment" for c in curtailment.columns}, inplace=True
        )
        curtailment["curtailment"] = curtailment.sum(axis=1)
        all_loadzone_data[sid] = pd.concat(
            [
                sum_generation_by_type_zone(scenario).T,
                scenario.state.get_demand().sum().T.rename("load"),
                curtailment,
            ],
            axis=1,
        ).rename(index=mi.zones["id2loadzone"])

    width = 0.4
    x_scale = 0.6
    ax_list = []
    for area, area_type in zip(areas, area_types):
        fig, ax = plt.subplots(figsize=(10, 8))
        for ind, s in enumerate(s_list):
            patches = []
            fuels = []
            bottom = 0
            loadzone_set = area_to_loadzone(s.info["grid_model"], area, area_type)
            data = (
                all_loadzone_data[scenario_ids[ind]]
                .loc[loadzone_set]
                .sum()
                .divide(1e6)
                .astype("float")
                .round(2)
            )
            for i, f in enumerate(resources[::-1]):
                if f == "load":
                    continue
                if curtailment_split and f == "curtailment":
                    continue
                if not curtailment_split and f in {
                    "wind_curtailment",
                    "solar_curtailment",
                    "wind_offshore_curtailment",
                }:
                    continue
                fuels.append(f)
                if "curtailment" in f:
                    patches.append(
                        ax.bar(
                            ind * x_scale,
                            data[f],
                            width,
                            bottom=bottom,
                            color=type2color.get(f, "red"),
                            hatch="//",
                            edgecolor=type2hatchcolor.get(f, "black"),
                            lw=0,
                        )
                    )
                else:
                    patches.append(
                        ax.bar(
                            ind * x_scale,
                            data[f],
                            width,
                            bottom=bottom,
                            color=type2color[f],
                        )
                    )
                bottom += data[f]

            # plot load line
            xs = [ind * x_scale - 0.5 * width, ind * x_scale + 0.5 * width]
            ys = [data["load"]] * 2
            line_patch = ax.plot(xs, ys, "--", color="black")

        if scenario_names:
            labels = scenario_names
        else:
            labels = [s.info["name'"] for s in s_list]
        ax.set_xticks([i * x_scale for i in range(len(s_list))])
        ax.set_xticklabels(labels, fontsize=12)
        ax.set_ylabel("TWh", fontsize=12)
        bar_legend = ax.legend(
            handles=patches[::-1] + line_patch,
            labels=[type2label.get(f, f.capitalize()) for f in fuels[::-1]]
            + ["Demand"],
            fontsize=12,
            bbox_to_anchor=(1, 1),
            loc="upper left",
        )
        ax.add_artist(bar_legend)
        ax.set_axisbelow(True)
        ax.grid(axis="y")
        if titles is not None and area in titles:
            ax.set_title(titles[area])
        else:
            ax.set_title(area)
        fig.tight_layout()
        ax_list.append(ax)
        if plot_show:
            plt.show()
        if save:
            if filenames is not None and area in filenames:
                filename = filenames[area]
            else:
                filename = area
            if not filepath:
                filepath = os.getcwd()
            fig.savefig(
                f"{os.path.join(filepath, filename)}.pdf",
                bbox_inches="tight",
                pad_inches=0,
            )
    return ax_list
