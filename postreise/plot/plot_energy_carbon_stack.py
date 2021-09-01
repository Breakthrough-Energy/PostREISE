# This plotting module has a corresponding demo notebook in
#   PostREISE/postreise/plot/demo: energy_emissions_stack_bar_demo.ipynb

import matplotlib.pyplot as plt
import numpy as np
from powersimdata.network.model import ModelImmutables
from powersimdata.scenario.scenario import Scenario

from postreise.analyze.generation.emissions import generate_emissions_stats

# Define common classifications
possible_renewable = ["solar", "wind", "wind_offshore"]
possible_clean = possible_renewable + ["geothermal", "hydro", "nuclear"]
possible_carbon = ["coal", "dfo", "ng"]
all_possible = possible_carbon + ["other"] + possible_clean


def plot_n_scenarios(*args):
    """For 1-to-n scenarios, plot stacked energy and carbon side-by-side.

    :param powersimdata.scenario.scenario.Scenario args: scenario instances.
    :raises ValueError: if arguments are not scenario instances.
    """
    if not all([isinstance(a, Scenario) for a in args]):
        raise ValueError("all inputs must be Scenario objects")
    # Build dictionaries of calculated data for each scenario
    scenario_numbers = [a.info["id"] for a in args]
    first_id = scenario_numbers[0]
    scenarios = {id: scen for (id, scen) in zip(scenario_numbers, args)}
    grid = {id: scenario.state.get_grid() for id, scenario in scenarios.items()}
    plant = {k: v.plant for k, v in grid.items()}
    # First scenario is chosen to set fuel colors
    type2color = ModelImmutables(args[0].info["grid_model"]).plants["type2color"]
    carbon_by_type, energy_by_type = {}, {}
    for id, scenario in scenarios.items():
        # Calculate raw numbers
        annual_plant_energy = scenario.state.get_pg().sum()
        raw_energy_by_type = annual_plant_energy.groupby(plant[id].type).sum()
        annual_plant_carbon = generate_emissions_stats(scenario).sum()
        raw_carbon_by_type = annual_plant_carbon.groupby(plant[id].type).sum()
        # Drop fuels with zero energy (e.g. all offshore_wind scaled to 0 MW)
        energy_by_type[id] = raw_energy_by_type[raw_energy_by_type != 0]
        carbon_by_type[id] = raw_carbon_by_type[raw_energy_by_type != 0]
    # Carbon multiplier is inverse of carbon intensity, to scale bar heights
    carbon_multiplier = energy_by_type[first_id].sum() / carbon_by_type[first_id].sum()

    # Determine the fuel types with generation in either scenario
    fuels = list(set.union(*[set(v.index) for v in energy_by_type.values()]))
    # Fill zeros in scenarios without a fuel when it's present in another
    for id in scenario_numbers:
        energy_by_type[id] = energy_by_type[id].reindex(fuels, fill_value=0)
        carbon_by_type[id] = carbon_by_type[id].reindex(fuels, fill_value=0)
    # Re-order according to plotting preferences
    fuels = [f for f in all_possible if f in fuels]
    # Re-assess subsets
    renewable_fuels = [f for f in possible_renewable if f in fuels]
    clean_fuels = [f for f in possible_clean if f in fuels]
    carbon_fuels = [f for f in possible_carbon if f in fuels]
    dropped_fuels = (set(possible_clean) | set(possible_carbon)) - (
        set(clean_fuels) | set(carbon_fuels)
    )
    print("no energy in any grid(s), dropping: %s" % ", ".join(dropped_fuels))

    fuel_series = {
        f: sum(
            [
                [energy_by_type[s][f], carbon_by_type[s][f] * carbon_multiplier]
                for s in scenario_numbers
            ],
            [],
        )
        for f in fuels
    }
    num_bars = 2 * len(scenario_numbers)
    ind = np.arange(num_bars)
    width = 0.5
    line_alpha = 0.25
    line_offsets = np.array((0.25, 0.75))

    # Strart plotting
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    # Plot bars
    patches = {}
    bottom = np.zeros(num_bars)
    for i, f in enumerate(fuels):
        patches[i] = plt.bar(
            ind, fuel_series[f], width, bottom=bottom, color=type2color[f]
        )
        bottom += fuel_series[f]
    # Plot lines
    for i, fuel in enumerate(carbon_fuels):
        for j, s in enumerate(scenario_numbers):
            cumulative_energy = sum(
                [energy_by_type[s][carbon_fuels[k]] for k in range(i + 1)]
            )
            cumulative_scaled_carbon = carbon_multiplier * sum(
                [carbon_by_type[s][carbon_fuels[k]] for k in range(i + 1)]
            )
            ys = (cumulative_energy, cumulative_scaled_carbon)
            xs = line_offsets + 2 * j
            plt.plot(xs, ys, "k-", alpha=line_alpha)

    # Labeling
    energy_fmt = "{0:,.0f} TWh\n{1:.0f}% renewable\n{2:.0f}% carbon-free\n"
    carbon_fmt = "{0:,.0f} million\ntons CO2\n"
    energy_total = {s: energy_by_type[s].sum() for s in scenarios}
    for j, s in enumerate(scenario_numbers):
        carbon_total = carbon_by_type[s].sum()
        renewable_energy = sum([energy_by_type[s][f] for f in renewable_fuels])
        clean_energy = sum([energy_by_type[s][f] for f in clean_fuels])
        renewable_share = renewable_energy / energy_total[s] * 100
        clean_share = clean_energy / energy_total[s] * 100
        annotation_str = energy_fmt.format(
            energy_total[s] / 1e6, renewable_share, clean_share
        )
        annotation_x = 2 * (j - 0.08)
        plt.annotate(xy=(annotation_x, energy_total[s]), text=annotation_str)
        annotation_str = carbon_fmt.format(carbon_total / 1e6)
        annotation_x = 2 * (j - 0.08) + 1
        annotation_y = carbon_total * carbon_multiplier
        plt.annotate(xy=(annotation_x, annotation_y), text=annotation_str)

    # Plot formatting
    plt.ylim((0, max(energy_total.values()) * 1.2))
    labels = sum([["%s Energy" % id, "%s Carbon" % id] for id in scenario_numbers], [])
    plt.xticks(ind, labels)
    plt.yticks([], [])
    ax.tick_params(axis="x", labelsize=12)
    # Invert default legend order to match stack ordering
    plt.legend(
        handles=(patches[i] for i in range(len(fuels) - 1, -1, -1)),
        labels=fuels[::-1],
        fontsize=12,
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
    )
    plt.tight_layout()
    plt.show()
