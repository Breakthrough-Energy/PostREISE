import pandas as pd
from powersimdata.design.generation.clean_capacity_scaling import (
    add_demand_to_targets,
    add_resource_data_to_targets,
    add_shortfall_to_targets,
    calculate_overall_shortfall,
)
from powersimdata.scenario.scenario import Scenario


def plot_bar_shortfall(
    areas,
    scenario_ids,
    target_df,
    strategy=None,
    scenario_names=None,
    baseline_scenario=None,
    baseline_scenario_name=None,
):
    """Plot a stacked bar chart of generation shortfall based on given targets for
        any number of scenarios.

    :param list/str areas: list of area(s) to show shortfall bar plots. If the target of
        an area is not defined in target_df, it will be ignored.
    :param int/list/str scenario_ids: list of scenario id(s).
    :param pandas.DataFrame target_df: target data frame, which defines the clean
        energy target fraction, allowed resources and external historical amount of
        qualified energy for each area.
    :param dict strategy: a dictionary with keys being scenario ids and values being
        strategies, either *"collaborative"* or *"independent"*. *"collaborative"* is
        used if None.
    :param list/str scenario_names: list of scenario name(s) of same len as scenario
        ids, defaults to None.
    :param str/int baseline_scenario: scenario id that serves as a baseline in the
        bar chart, default to None.
    :param str baseline_scenario_name: specify the label of the baseline scenario
        shown in the bar chart, default to None, in which case the name of the
        scenario will be used.
    :raises ValueError:
        if length of scenario_names and scenario_ids is different.
    :raises TypeError:
        if target_df is not a pandas.DataFrame and/or
        if strategy is provided but not in a dictionary format and/or
        if baseline_scenario is provided but not in a str/int format and/or
        if baseline_scenario_name is provided but not in a str format.
    """
    if isinstance(areas, str):
        areas = [areas]
    if isinstance(scenario_ids, (int, str)):
        scenario_ids = [scenario_ids]
    if not isinstance(target_df, pd.DataFrame):
        raise TypeError("ERROR: target_df must be a pandas.DataFrame")
    if strategy is None:
        strategy = dict()
    if not isinstance(strategy, dict):
        raise TypeError("ERROR: strategy must be a dictionary")
    if isinstance(scenario_names, str):
        scenario_names = [scenario_names]
    if scenario_names is not None and len(scenario_names) != len(scenario_ids):
        raise ValueError(
            "ERROR: if scenario names are provided, number of scenario names must match number of scenario ids"
        )
    if baseline_scenario is not None and not isinstance(baseline_scenario, (str, int)):
        raise TypeError("ERROR: baseline_scenario must be a string or integer")
    if baseline_scenario_name is not None and not isinstance(
        baseline_scenario_name, str
    ):
        raise TypeError("ERROR: baseline_scenario_name must be a string")

    scenarios = dict()
    targets = dict()
    all_sids = scenario_ids + [baseline_scenario] if baseline_scenario else scenario_ids
    for sid in all_sids:
        s = Scenario(sid)
        tmp_df = target_df.copy()
        tmp_df = add_resource_data_to_targets(tmp_df, s)
        tmp_df = add_demand_to_targets(tmp_df, s)
        tmp_df = add_shortfall_to_targets(tmp_df)
        scenarios[sid] = s
        targets[sid] = tmp_df
    for area in areas:
        if area not in target_df.index and area != "all":
            print(f"{area} is skipped due to lack of target information in target_df!")
            continue
        ax_data = {}
        for i, sid in enumerate(scenario_ids):
            label = scenario_names[i] if scenario_names else scenarios[sid].info["name"]
            if area == "all":
                demand = targets[sid]["demand"].sum()
                shortfall = calculate_overall_shortfall(
                    targets[sid], method=strategy.get(sid, "collaborative")
                )
                ce_generated = targets[sid]["ce_target"].sum() - shortfall
                if baseline_scenario:
                    baseline_shortfall = calculate_overall_shortfall(
                        targets[baseline_scenario],
                        method=strategy.get(baseline_scenario, "collaborative"),
                    )
                    baseline = (
                        targets[baseline_scenario]["ce_target"].sum()
                        - baseline_shortfall
                    )
                shortfall = max(shortfall, 0)
            else:
                demand = targets[sid].loc[area, "demand"]
                shortfall = targets[sid].loc[area, "ce_shortfall"]
                ce_generated = (
                    targets[sid].loc[area, "prev_ce_generation"]
                    + targets[sid].loc[area, "external_ce_addl_historical_amount"]
                )
                if baseline_scenario:
                    baseline = (
                        targets[baseline_scenario].loc[area, "prev_ce_generation"]
                        + targets[baseline_scenario].loc[
                            area, "external_ce_addl_historical_amount"
                        ]
                    )
            if baseline_scenario:
                ax_data.update(
                    {
                        label: {
                            baseline_scenario_name: round(100 * baseline / demand, 2),
                            "Increment from baseline": max(
                                0, round(100 * (ce_generated - baseline) / demand, 2)
                            ),
                            "Missed target": round(100 * shortfall / demand, 2),
                        }
                    }
                )
            else:
                ax_data.update(
                    {
                        label: {
                            "Qualified clean energy": round(
                                100 * ce_generated / demand, 2
                            ),
                            "Missed target": round(100 * shortfall / demand, 2),
                        }
                    }
                )
        if area != "all":
            target_pct = round(100 * target_df.loc[area, "ce_target_fraction"], 2)
        else:
            # The overall target percentage is different among scenarios given the
            # demand might be different. Here we pick the first scenario in scenario_ids
            # to calculate the overall target percentage
            target_demand = targets[scenario_ids[0]]["demand"].sum()
            target_generation = targets[scenario_ids[0]]["ce_target"].sum()
            target_pct = round(100 * target_generation / target_demand, 2)

        if baseline_scenario:
            _construct_shortfall_visuals(
                area,
                ax_data,
                target_pct,
                baseline=True,
                baseline_scenario_name=baseline_scenario_name,
            )
        else:
            _construct_shortfall_visuals(
                area,
                ax_data,
                target_pct,
            )


def _construct_shortfall_visuals(
    zone, ax_data, target_pct, baseline=False, baseline_scenario_name=None
):
    """Plot formatted data.

    :param str zone: the zone name.
    :param dict ax_data: nested dictionary with keys on the top layer being scenario
        names and values are dictionaries with keys being the categories of the bar
        chart data and values being the numbers in percentage.
    :param float target_pct: target in terms of percentage of demand.
    :param bool baseline: a boolean indicator indicates whether there is a baseline
        scenario specified.
    :param str baseline_scenario_name: name of the baseline scenario.
    """
    df = pd.DataFrame(ax_data).T
    if baseline:
        df = df[[baseline_scenario_name, "Increment from baseline", "Missed target"]]
    else:
        df = df[["Qualified clean energy", "Missed target"]]
    ax = df.plot.bar(
        stacked=True,
        color=["darkgreen", "yellowgreen", "salmon"]
        if baseline
        else ["yellowgreen", "salmon"],
        figsize=(10, 8),
        fontsize=16,
    )
    ax.set_title(zone, fontsize=26)
    ax.set_ylim(top=1.33 * ax.get_ylim()[1])
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment="right")

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        reversed(handles), reversed(labels), bbox_to_anchor=(1.556, 1.015), fontsize=14
    )

    # Add target line
    if target_pct > 0:
        ax_text = f"Target {target_pct:}% of demand"
        ax.text(
            1.01,
            target_pct,
            ax_text,
            transform=ax.get_yaxis_transform(),
            fontsize=16,
            verticalalignment="center",
        )
        ax.axhline(y=target_pct, dashes=(5, 2), color="black")

    # Percent numbers
    patch_indices = list(range(len(ax_data) * (2 + baseline)))[-1 * len(ax_data) :]
    ax_data_value = list(ax_data.values())
    for i, ind in enumerate(patch_indices):
        if ax_data_value[i]["Missed target"] != 0:
            b = ax.patches[ind].get_bbox()
            ax.annotate(
                f"{ax_data_value[i]['Missed target']}%\nshortfall",
                (b.x1 - 0.5, b.y1 * 1.02),
                fontsize=16,
            )
