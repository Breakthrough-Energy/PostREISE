import matplotlib.pyplot as plt
import numpy as np

from postreise.analyze.generation.carbon import generate_carbon_stats


# Define common classifications
possible_renewable = ['solar', 'wind', 'wind_offshore']
possible_clean = possible_renewable + ['geothermal', 'hydro', 'nuclear']
possible_carbon = ['coal', 'dfo', 'ng']
all_possible = possible_carbon + ['other'] + possible_clean


def plot_single_scenario(scenario):
    """For a single scenario, plot stacked energy and carbon.
    
    :param powersimdata.scenario.scenario.Scenario scenario: scenario in
        Analyze state.
    """
    # Retrieve data and calculate summary statistics
    grid = scenario.state.get_grid()
    plant = grid.plant
    annual_plant_carbon = generate_carbon_stats(scenario).sum()
    carbon_by_type = annual_plant_carbon.groupby(plant.type).sum()
    annual_plant_energy = scenario.state.get_pg().sum()
    energy_by_type = annual_plant_energy.groupby(plant.type).sum()
    energy_total = energy_by_type.sum()
    carbon_total = carbon_by_type.sum()
    # carbon multiplier is inverse of carbon intensity, to scale bar heights
    carbon_multiplier = energy_total / carbon_total
    fuels = list(energy_by_type.index.to_numpy())
    # Re-order according to plotting preferences
    fuels = [f for f in all_possible if f in fuels]
    
    # Filter out fuel types which are not in this grid
    renewable_fuels = [f for f in possible_renewable if f in energy_by_type]
    clean_fuels = [f for f in possible_clean if f in energy_by_type]
    carbon_fuels = [f for f in possible_carbon if f in energy_by_type]
    dropped_fuels = ((set(possible_clean) | set(possible_carbon))
                     - (set(clean_fuels) | set(carbon_fuels)))
    print('not present in grid, dropping: %s' % ', '.join(dropped_fuels))
    
    # Setup data, parameters, and axis for plotting
    fuel_series = {
        f: (energy_by_type[f], carbon_by_type[f] * carbon_multiplier)
        for f in fuels}
    num_bars = 2
    ind = np.arange(num_bars)
    width = 0.5
    line_alpha = 0.25
    line_xs = (0.25, 0.75)
    resource_colors = grid.type2color
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    
    # Plot bars
    patches = {}
    bottom = np.zeros(num_bars)
    for i, f in enumerate(fuels):
        color = resource_colors[f]
        patches[i] = plt.bar(
            ind, fuel_series[f], width, bottom=bottom,color=color)
        bottom += fuel_series[f]
    
    # Plot lines
    for i, fuel in enumerate(carbon_fuels):
        cumulative_energy = sum(
            [energy_by_type[carbon_fuels[j]] for j in range(i+1)])
        cumulative_scaled_carbon = carbon_multiplier * sum(
            [carbon_by_type[carbon_fuels[j]] for j in range(i+1)])
        ys = (cumulative_energy, cumulative_scaled_carbon)
        plt.plot(line_xs, ys, 'k-', alpha=line_alpha)
    
    # Labeling
    renewable_energy = sum([energy_by_type[f] for f in renewable_fuels])
    clean_energy = sum([energy_by_type[f] for f in clean_fuels])
    renewable_share = renewable_energy / energy_total * 100
    clean_share = clean_energy / energy_total * 100
    annotate_fmt = '{0:,.0f} TWh\n{1:.0f}% renewable\n{2:.0f}% carbon-free\n'
    annotation_str = annotate_fmt.format(
        energy_total / 1e6, renewable_share, clean_share)
    plt.annotate(xy=(-0.125, energy_total), s=annotation_str)
    annotation_str = '{0:,.0f} million\ntons CO2\n'.format(carbon_total / 1e6)
    plt.annotate(xy=(0.875, carbon_total*carbon_multiplier), s=annotation_str)
    
    # Plot formatting
    plt.ylim((0, energy_total * 1.2))
    plt.xticks(ind, ('Energy', 'Carbon'))
    plt.yticks([], [])
    ax.tick_params(axis='x', labelsize=12)
    # Invert default legend order to match stack ordering
    plt.legend(
        handles=(patches[i] for i in range(len(fuels)-1, -1, -1)),
        labels=fuels[::-1],
        fontsize=12,
        bbox_to_anchor=(1.02, 1),
        loc='upper left')
    plt.tight_layout()
    plt.show()


def plot_two_scenarios(left_scenario, right_scenario):
    """For two scenarios, plot stacked energy and carbon side-by-side.

    :param powersimdata.scenario.scenario.Scenario left_scenario: scenario in
        Analyze state.
    :param powersimdata.scenario.scenario.Scenario right_scenario: scenario in
        Analyze state.
    """
    # Build dictionaries of calculated data for each scenario
    scenarios = {'left': left_scenario, 'right': right_scenario}
    scenario_numbers = {k: v.info['id'] for k, v in scenarios.items()}
    grid = {name: scenario.state.get_grid()
            for name, scenario in scenarios.items()}
    plant = {k: v.plant for k, v in grid.items()}
    carbon_by_type, energy_by_type = {}, {}
    for name, scenario in scenarios.items():
        # Calculate raw numbers
        annual_plant_energy = scenario.state.get_pg().sum()
        raw_energy_by_type = annual_plant_energy.groupby(plant[name].type).sum()
        annual_plant_carbon = generate_carbon_stats(scenario).sum()
        raw_carbon_by_type = annual_plant_carbon.groupby(plant[name].type).sum()
        # Drop fuels with zero energy (e.g. all offshore_wind scaled to 0 MW)
        energy_by_type[name] = raw_energy_by_type[raw_energy_by_type != 0]
        carbon_by_type[name] = raw_carbon_by_type[raw_energy_by_type != 0]
    # carbon multiplier is inverse of carbon intensity, to scale bar heights
    carbon_multiplier = (
        energy_by_type['left'].sum() / carbon_by_type['left'].sum())

    # Determine the fuel types with generation in either scenario
    fuels = list(set.union(*[set(v.index) for v in energy_by_type.values()]))
    # Re-order according to plotting preferences
    fuels = [f for f in all_possible if f in fuels]
    # Re-assess subsets
    renewable_fuels = [f for f in possible_renewable if f in fuels]
    clean_fuels = [f for f in possible_clean if f in fuels]
    carbon_fuels = [f for f in possible_carbon if f in fuels]
    dropped_fuels = ((set(possible_clean) | set(possible_carbon))
                     - (set(clean_fuels) | set(carbon_fuels)))
    print('no energy in either grid, dropping: %s' % ', '.join(dropped_fuels))

    fuel_series = {
        f: sum([
            [energy_by_type[s][f], carbon_by_type[s][f] * carbon_multiplier]
            for s in scenarios], [])
        for f in fuels}
    num_bars = 4
    ind = np.arange(num_bars)
    width = 0.5
    line_alpha = 0.25
    line_offsets = np.array((0.25, 0.75))
    resource_colors = grid['left'].type2color
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)

    # Plot bars
    patches = {}
    bottom = np.zeros(num_bars)
    for i, f in enumerate(fuels):
        color = resource_colors[f]
        patches[i] = plt.bar(
            ind, fuel_series[f], width, bottom=bottom, color=color)
        bottom += fuel_series[f]

    # Plot lines
    for i, fuel in enumerate(carbon_fuels):
        for j, s in enumerate(scenarios):
            cumulative_energy = sum(
                [energy_by_type[s][carbon_fuels[k]] for k in range(i+1)])
            cumulative_scaled_carbon = carbon_multiplier * sum(
                [carbon_by_type[s][carbon_fuels[k]] for k in range(i+1)])
            ys = (cumulative_energy, cumulative_scaled_carbon)
            xs = line_offsets + 2 * j
            plt.plot(xs, ys, 'k-', alpha=line_alpha)

    # Labeling
    energy_fmt = '{0:,.0f} TWh\n{1:.0f}% renewable\n{2:.0f}% carbon-free\n'
    carbon_fmt = '{0:,.0f} million\ntons CO2\n'
    energy_total = {s: energy_by_type[s].sum() for s in scenarios}
    for j, s in enumerate(scenarios):
        carbon_total = carbon_by_type[s].sum()
        renewable_energy = sum([energy_by_type[s][f] for f in renewable_fuels])
        clean_energy = sum([energy_by_type[s][f] for f in clean_fuels])
        renewable_share = renewable_energy / energy_total[s] * 100
        clean_share = clean_energy / energy_total[s] * 100
        annotation_str = energy_fmt.format(
            energy_total[s] / 1e6, renewable_share, clean_share)
        annotation_x = 2 * j - 0.125
        plt.annotate(xy=(annotation_x, energy_total[s]), s=annotation_str)
        annotation_str = carbon_fmt.format(carbon_total / 1e6)
        annotation_x = 2 * j + 0.875
        annotation_y = carbon_total*carbon_multiplier
        plt.annotate(xy=(annotation_x, annotation_y), s=annotation_str)

    # Plot formatting
    plt.ylim((0, max(energy_total.values()) * 1.2))
    labels = ['%s Energy' % scenario_numbers['left'],
              '%s Carbon' % scenario_numbers['left'],
              '%s Energy' % scenario_numbers['right'],
              '%s Carbon' % scenario_numbers['right'],
              ]
    plt.xticks(ind, labels)
    plt.yticks([], [])
    ax.tick_params(axis='x', labelsize=12)
    # Invert default legend order to match stack ordering
    plt.legend(
        handles=(patches[i] for i in range(len(fuels)-1, -1, -1)),
        labels=fuels[::-1],
        fontsize=12,
        bbox_to_anchor=(1.02, 1),
        loc='upper left')
    plt.tight_layout()
    plt.show()
