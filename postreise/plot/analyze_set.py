import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import AutoMinorLocator
from westernintnet.westernintnet import win_data as grid
from postreise.process import transferdata as td

od = td.OutputData()


def get_plant_id(zone):
    """Lists the id of the plants located in zone.

    :param str zone: one of the zones.
    :param return: id of the plants in the specified zone.
    """

    if zone not in grid.load_zones.values():
        if zone == 'Western':
            plant_id = grid.genbus.index
        elif zone == 'California':
            plant_id = []
            ca = ['Northern California', 'Central California', 'Bay Area',
                  'Southeast California', 'Southwest California']
            for load_zone in ca:
                plant_id += grid.genbus.groupby('ZoneName').get_group(
                    load_zone).index.values.tolist()
        else:
            print('Possible zones are:')
            print(grid.load_zones.values())
            return
    else:
        plant_id = grid.genbus.groupby('ZoneName').get_group(zone).index

    return plant_id


def fraction_renewable(scenarios, zone):
    """Plots the fraction of power generated by generators fueled by \ 
        renewable energies in zone for scenarios.

    :param dict scenarios: set of scenario with scenario description as key \ 
        and list of scenario name as values.
    :param str zone: one of the load zones.
    """

    plant_id_all = get_plant_id(zone)

    plant_id_renewable = []
    for r in ['solar', 'wind']:
        plant_id_renewable += list(set(plant_id_all).intersection(
            grid.genbus.groupby('type').get_group(r).index))

    nb = len(scenarios.keys())
    frac = np.zeros(nb*2).reshape(nb, 2)

    for i, files in enumerate(scenarios.values()):
        for j, f in enumerate(files):
            if f:
                pg = od.get_data(f, 'PG')
                frac[i, j] = pg[plant_id_renewable].sum(axis=1).sum() / \
                    pg[plant_id_all].sum(axis=1).sum()
                frac[i, j] *= 100

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
    """Plots the fraction of power generated by every type of generators in \ 
        zone for scenarios.

    :param dict scenarios: set of scenario with scenario description as key \ 
        and list of scenario name as values.
    :param str zone: one of the load zones.
    :return: data frame of the power generated with fuel type as columns.
    """

    r2l = {'nuclear': 'Nuclear',
           'hydro': 'Hydro',
           'coal': 'Coal',
           'ng': 'Natural Gas',
           'solar': 'Solar',
           'wind': 'Wind'}

    plant_id = get_plant_id(zone)
    nb = len(scenarios.keys())

    frac = pd.DataFrame(columns=r2l.keys(), index=range(nb*2))
    ytitle = [None]*nb*2

    for i, files in enumerate(scenarios.values()):
        for j, f in enumerate(files):
            if f:
                pg = od.get_data(f, 'PG')[plant_id]
                total = pg.sum(axis=1).sum()
                pg_stack = pg.T.groupby(grid.genbus['type']).agg(sum).T
                for r in grid.ID2type.values():
                    if r not in pg_stack.columns:
                        del r2l[r]

                if j == 0:
                    frac.loc[i, r2l.keys()] = [pg_stack.sum()[r] / total
                                               for r in r2l.keys()]
                    ytitle[i] = list(scenarios.keys())[i] + ' ' + \
                        '(current grid)'
                else:
                    frac.loc[nb+i, r2l.keys()] = [pg_stack.sum()[r] / total
                                                  for r in r2l.keys()]
                    ytitle[nb+i] = list(scenarios.keys())[i] + ' ' + \
                        '(enhanced grid)'

    frac_plot = frac.copy()
    for i in frac.index:
        if frac_plot.loc[i, 'nuclear'] != np.nan:
            frac_plot.loc[i, ['nuclear', 'hydro', 'coal', 'ng']] *= -1

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
    ax.set_yticklabels(ytitle)
    ax.set_xlabel('Generation [%]', fontsize=22)
    ax.tick_params(labelsize=20)
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))

    plt.show()

    return frac


def generation(scenarios, zones, grid_type=0):
    """Plots the stacked power generated in zones for various scenarios.

    :param dict scenarios: set of scenario with scenario description as key \ 
        and list of scenario name as values.
    :param list zones: list of zones.
    :param int grid_type: either *'0'* (current grid) or *'1'* (enhanced grid).
    :return: list of data frame of the power generated in specified zones. \ 
        Each data frame has fuel type as columns and the the scenario name as \ 
        indices.
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

    for key, files in scenarios.items():
        f = files[grid_type]
        if f:
            pg = od.get_data(f, 'PG')
            allotment_scenario = pd.DataFrame(
                columns=['nuclear', 'hydro', 'coal', 'ng', 'solar', 'wind'],
                index=zones)
            for z in zones:
                r2l = {'nuclear': 'Nuclear',
                       'hydro': 'Hydro',
                       'coal': 'Coal',
                       'ng': 'Natural Gas',
                       'solar': 'Solar',
                       'wind': 'Wind'}
                plant_id = get_plant_id(z)
                pg_tmp = pg[plant_id]

                pg_groups = pg_tmp.T.groupby(grid.genbus['type'])
                pg_stack = pg_groups.agg(sum).T
                for r in grid.ID2type.values():
                    if r not in pg_stack.columns:
                        del r2l[r]

                allotment_scenario.loc[z, r2l.keys()] = [pg_stack.sum()[r]/1000
                                                         for r in r2l.keys()]
            allotment.append(allotment_scenario)
            title.append(key)

    fig = plt.figure(figsize=(12, 12))
    plt.title(main_title, fontsize=25)
    ax = fig.gca()
    ax.set_facecolor('white')
    ax.grid(color='black', axis='y')
    ax.tick_params(labelsize=20)
    ax.set_ylabel('Generation [GWh]', fontsize=22)

    colors = [grid.type2color[r] 
              for r in ['nuclear', 'hydro', 'coal', 'ng', 'solar', 'wind']]
    for df in allotment:
        ax = df.rename(columns={'nuclear': 'Nuclear', 'hydro': 'Hydro',
                                'coal': 'Coal', 'ng': 'Natural Gas',
                                'solar': 'Solar', 'wind': 'Wind'}).plot(
                                kind="bar", linewidth=0, stacked=True,
                                ax=ax, color=colors, label=True, alpha=0.7)
    ax.set_ylim(0, ax.get_ylim()[1])
    ax.ticklabel_format(axis='y', useOffset=False, style='plain')

    n_col = 6 # number of resources
    n_df = len(allotment)
    n_ind = len(zones)
    h, l = ax.get_legend_handles_labels()  # get the handles we want to modify
    for i in range(0, n_df * n_col, n_col):  # len(h) = n_col * n_df
        for j, pa in enumerate(h[i:i+n_col]):
            for rect in pa.patches:  # for each index
                rect.set_x(rect.get_x() + 1 / float(n_df+1) * i / float(n_col))
                rect.set_hatch('/' * int(i / n_col))  # edited part
                rect.set_width(1 / float(n_df + 1))

    ax.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
    ax.set_xticklabels(df.index, rotation=0)

    # Add invisible data to add another legend
    n = [ax.bar(0, 0, color="gray", hatch='/' * i) for i in range(n_df)]
    l1 = ax.legend(h[:n_col], l[:n_col], loc=[1.01, 0.5], fontsize=18)
    l2 = ax.legend(n, title, loc=[1.01, 0.1], fontsize=18)
    ax.add_artist(l1)
    ax.add_artist(l2)

    plt.show()

    return allotment
