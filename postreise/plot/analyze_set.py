from powersimdata.scenario.scenario import Scenario
from postreise.plot.multi import constants

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import AutoMinorLocator


def get_plant_id(grid, zone):
    """Lists the id of the plants located in zone.

    :param powersimdata.input.grid.Grid grid: grid instance.
    :param str zone: load zone or California or Western.
    :return: (*list*) -- id of the plants in the specified zone.
    """

    if zone not in grid.zone2id.keys():
        if zone == 'Western':
            plant_id = grid.plant.index
        elif zone == 'California':
            plant_id = []
            ca = ['Northern California', 'Central California', 'Bay Area',
                  'Southeast California', 'Southwest California']
            for z in ca:
                plant_id += grid.plant.groupby('zone_name').get_group(
                    z).index.values.tolist()
        else:
            print('Possible load zones are:')
            print(grid.zone2id.keys())
            return
    else:
        plant_id = grid.plant.groupby('zone_name').get_group(zone).index

    return plant_id


def fraction_renewable(scenarios, zone):
    """Plots the fraction of power generated by generators fueled by renewable
        energies in zone for scenarios.

    :param dict scenarios: set of scenario with scenario description as key and
        list of scenario name as values.
    :param str zone: load zone.
    """

    nb = len(scenarios.keys())
    frac = np.zeros(nb*2).reshape(nb, 2)

    for i, files in enumerate(scenarios.values()):
        for j, f in enumerate(files):
            if f:
                scenario = Scenario(f)
                grid = scenario.state.get_grid()
                pg = scenario.state.get_pg()

                plant_id_all = get_plant_id(grid, zone)
                plant_id_renewable = []
                for r in ['solar', 'wind']:
                    plant_id_renewable += list(set(plant_id_all).intersection(
                        grid.plant.groupby('type').get_group(r).index))

                frac[i, j] = pg[plant_id_renewable].sum(axis=1).sum() / \
                    pg[plant_id_all].sum(axis=1).sum()
                frac[i, j] *= 100
                print('\n')
            else:
                frac[i, j] = float('nan')

    fig = plt.figure(figsize=(12, 12))
    plt.title(zone, fontsize=25)
    ax = fig.gca()

    ax.set_facecolor('white')
    ax.grid(color='black', axis='y')
    ax.tick_params(labelsize=20)
    ax.set_xlabel('Scenario', fontsize=22)
    ax.set_ylabel('Renewable Energy Generation [%]', fontsize=22)

    ax.plot(scenarios.keys(), frac[:, 0], 'r-o', label='Current Grid', lw=4,
            markersize=12)
    ax.plot(scenarios.keys(), frac[:, 1], 'b-o', label='Enhanced Grid', lw=4,
            markersize=12)

    ax.legend(loc='lower right', prop={'size': 18})

    plt.show()


def fraction(scenarios, zone):
    """Plots the fraction of power generated by every type of generators in zone
        for scenarios.

    :param dict scenarios: set of scenario with scenario description as key and
        list of scenario name as values.
    :param str zone: load zone.
    :return: (pandas.DataFrame) -- data frame of the power generated with fuel
        type as columns.
    """

    plotted_resources = ('nuclear', 'hydro', 'coal', 'ng', 'solar', 'wind',
                         'dfo', 'geothermal', 'biomass', 'other')
    r2l = {r: constants.RESOURCE_LABELS[r] for r in plotted_resources}

    thermal_gen_types = ['dfo', 'geothermal', 'nuclear', 'hydro', 'coal', 'ng']

    nb = len(scenarios.keys())

    frac = pd.DataFrame(columns=r2l.keys(), index=range(nb*2))
    y_title = [None]*nb*2

    for i, files in enumerate(scenarios.values()):
        for j, f in enumerate(files):
            if f:
                scenario = Scenario(f)
                grid = scenario.state.get_grid()
                plant_id = get_plant_id(grid, zone)
                pg = scenario.state.get_pg()[plant_id]

                total = pg.sum(axis=1).sum()
                pg_stack = pg.T.groupby(grid.plant['type']).agg(sum).T
                for r in grid.id2type.values():
                    if r not in pg_stack.columns:
                        del r2l[r]

                if j == 0:
                    frac.loc[i, r2l.keys()] = [pg_stack.sum()[r] / total
                                               for r in r2l.keys()]
                    y_title[i] = list(scenarios.keys())[i] + ' ' + \
                        '(current grid)'
                else:
                    frac.loc[nb+i, r2l.keys()] = [pg_stack.sum()[r] / total
                                                  for r in r2l.keys()]
                    y_title[nb+i] = list(scenarios.keys())[i] + ' ' + \
                        '(enhanced grid)'
                print('\n')

    frac_plot = frac.copy()
    for i in frac.index:
        if frac_plot.loc[i, 'nuclear'] != np.nan:
            frac_plot.loc[i, thermal_gen_types] *= -1

    fig = plt.figure(figsize=(12, 12))
    plt.title(zone, fontsize=25)
    ax = fig.gca()
    ax.set_facecolor('white')

    colors = [grid.type2color[r] for r in r2l.keys()]
    ax = frac_plot[list(r2l.keys())].rename(
        columns=r2l).plot(
        ax=ax, kind='barh', stacked=True, label=True, color=colors, alpha=0.7)

    ax.axvline(0, 0, 1, color='black')
    ax.grid(color='black', which='major')
    ax.grid(color='gray', which='minor', alpha=0.5)
    ax.set_xticklabels([80, 70, 60, 50, 40, 30, 20, 10, 0, 10, 20, 30, 40])
    ax.set_xticks([-0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0,
                   0.1, 0.2, 0.3, 0.4])
    ax.legend(frameon=2, loc='upper left', prop={'size': 18})
    ax.set_yticklabels(y_title)
    ax.set_xlabel('Generation [%]', fontsize=22)
    ax.tick_params(labelsize=20)
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))

    plt.show()

    return frac


def generation(scenarios, zone, grid_type=0):
    """Plots the stacked power generated in zones for various scenarios.

    :param dict scenarios: set of scenario with scenario description as key and
        list of scenario name as values.
    :param list zone: list of zones.
    :param int grid_type: either *'0'* (current grid) or *'1'* (enhanced grid).
    :return: (*list*) -- list of data frame of the power generated in specified
        zones. Each data frame has fuel type as columns and the the scenario
        name as indices.
    """

    if grid_type == 0:
        main_title = 'Current Grid'
    elif grid_type == 1:
        main_title = 'Enhanced Grid'
    else:
        print('Incorrect grid type:')
        print('grid_type=0: current grid, grid_type=1: enhanced grid')
        return

    allotment = []
    title = []

    analyzed_types = ['nuclear', 'hydro', 'coal', 'ng', 'solar', 'wind']

    for key, files in scenarios.items():
        f = files[grid_type]
        if f:
            scenario = Scenario(f)
            grid = scenario.state.get_grid()
            pg = scenario.state.get_pg()
            allotment_scenario = pd.DataFrame(
                columns=analyzed_types, index=zone)
            for z in zone:
                r2l = {r: constants.RESOURCE_LABELS[r] for r in analyzed_types}
                plant_id = get_plant_id(grid, z)
                pg_tmp = pg[plant_id]

                pg_groups = pg_tmp.T.groupby(grid.plant['type'])
                pg_stack = pg_groups.agg(sum).T
                for r in grid.id2type.values():
                    if r not in pg_stack.columns:
                        del r2l[r]

                allotment_scenario.loc[z, r2l.keys()] = [pg_stack.sum()[r]/1000
                                                         for r in r2l.keys()]
            allotment.append(allotment_scenario)
            title.append(key)
            print('\n')

    fig = plt.figure(figsize=(12, 12))
    plt.title(main_title, fontsize=25)
    ax = fig.gca()
    ax.set_facecolor('white')
    ax.grid(color='black', axis='y')
    ax.tick_params(labelsize=20)
    ax.set_ylabel('Generation [GWh]', fontsize=22)

    colors = [grid.type2color[r] for r in analyzed_types]
    for df in allotment:
        rename_dict = {r: constants.RESOURCE_LABELS[r] for r in analyzed_types}
        ax = df.rename(columns=rename_dict).plot(
            kind="bar", linewidth=0, stacked=True, ax=ax, color=colors,
            label=True, alpha=0.7)
    ax.set_ylim(0, ax.get_ylim()[1])
    ax.ticklabel_format(axis='y', useOffset=False, style='plain')

    n_col = 6  # number of resources
    n_df = len(allotment)
    n_ind = len(zone)
    handle, label = ax.get_legend_handles_labels()  # get the handles to modify
    for i in range(0, n_df * n_col, n_col):  # len(h) = n_col * n_df
        for j, pa in enumerate(handle[i:i + n_col]):
            for rect in pa.patches:  # for each index
                rect.set_x(rect.get_x() + 1 / float(n_df+1) * i / float(n_col))
                rect.set_hatch('/' * int(i / n_col))  # edited part
                rect.set_width(1 / float(n_df + 1))

    ax.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
    ax.set_xticklabels(df.index, rotation=0)

    # Add invisible data to add another legend
    n = [ax.bar(0, 0, color="gray", hatch='/' * i) for i in range(n_df)]
    l1 = ax.legend(handle[:n_col], label[:n_col], loc=[1.01, 0.5], fontsize=18)
    l2 = ax.legend(n, title, loc=[1.01, 0.1], fontsize=18)
    ax.add_artist(l1)
    ax.add_artist(l2)

    plt.show()

    return allotment
