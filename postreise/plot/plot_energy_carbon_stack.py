import matplotlib.pyplot as plt
import numpy as np

from postreise.analyze.generation.carbon import generate_carbon_stats


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
    
    # Filter out fuel types which are not in this grid
    possible_renewable = ['solar', 'wind', 'wind_offshore']
    possible_clean = possible_renewable + ['geothermal', 'hydro', 'nuclear']
    possible_carbon = ['coal', 'dfo', 'ng']
    renewable_fuels = [f for f in possible_renewable if f in energy_by_type]
    clean_fuels = [f for f in possible_clean if f in energy_by_type]
    carbon_fuels = [f for f in possible_carbon if f in energy_by_type]
    dropped_fuels = ((set(possible_clean) | set(possible_carbon))
                     - (set(clean_fuels) | set(carbon_fuels)))
    print('not present in grid, dropping: %s' % ', '.join(dropped_fuels))

    # Pop and re-append 'clean' fuels to get them at the end of the list,
    #   which puts them at the top of the stack
    for f in clean_fuels:
        fuels.pop(fuels.index(f))
        fuels.append(f)
    
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
    p = {}
    bottom = np.zeros(num_bars)
    for i, f in enumerate(fuels):
        color = resource_colors[f]
        p[i] = plt.bar(ind, fuel_series[f], width, bottom=bottom, color=color)
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
    clean_energy = sum(
        [energy_by_type[f] for f in clean_fuels if f in energy_by_type])
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
        (p[i] for i in range(len(fuels)-1, -1, -1)), fuels[::-1], fontsize=12)
    plt.show()
