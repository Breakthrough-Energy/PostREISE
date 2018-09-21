import westernintnet
WI = westernintnet.WesternIntNet()
import matplotlib.pyplot as plt
import pytz
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import numpy as np
import pandas as pd



region2style = {'Washington':{'color':'green', 'alpha':1, 'lw':4, 'ls':'-'},
                'Oregon':{'color':'blue', 'alpha':1, 'lw':4, 'ls':'-'},
                'California':{'color':'red', 'alpha':1, 'lw':4, 'ls':'-'},
                'Northern California':{'color':'red', 'alpha':0.6, 'lw':4, 'ls':'--'},
                'Bay Area':{'color':'red', 'alpha':0.6, 'lw':4, 'ls':':'},
                'Central California':{'color':'red', 'alpha':0.6, 'lw':4, 'ls':'-.'},
                'Southwest California':{'color':'red', 'alpha':0.6, 'lw':4, 'ls':'-+'},
                'Southeast California':{'color':'red', 'alpha':0.6, 'lw':4, 'ls':'-o'},
                'Nevada':{'color':'orange', 'alpha':1, 'lw':4, 'ls':'-'},
                'Arizona':{'color':'maroon', 'alpha':1, 'lw':4, 'ls':'-'},
                'Utah':{'color':'tomato', 'alpha':1, 'lw':4, 'ls':'-'},
                'New Mexico':{'color':'teal', 'alpha':1, 'lw':4, 'ls':'-'},
                'Colorado':{'color':'darkorchid', 'alpha':1, 'lw':4, 'ls':'-'},
                'Wyoming':{'color':'goldenrod', 'alpha':1, 'lw':4, 'ls':'-'},
                'Idaho':{'color':'magenta', 'alpha':1, 'lw':4, 'ls':'-'},
                'Montana':{'color':'indigo', 'alpha':1, 'lw':4, 'ls':'-'},
                'El Paso':{'color':'dodgerblue', 'alpha':1, 'lw':4, 'ls':'-'},
                'total':{'color':'black', 'alpha':1, 'lw':4, 'ls':'-'}}



def time_offset(year, month, day, hour, minute, sec, lon, lat):
    """Calculates time difference between utc and local time for a given location.

    Arguments:
        year: year of the timestamp
        month: month of the timestamp
        day: day of the timestamp
        hour: hour of the timestamp
        minute: minute of the timestamp
        sec: second of the timestamp
        lon: longitude (in deg.) of the timestamp
        lat: latitude (in deg.) of the timestamp

    Returns:
        Offset (in hours) between UTC and local time
    """
    current = datetime(year, month, day, hour, minute, sec)

    # Current time set as UTC
    current_utc = pytz.utc.localize(current)

    # Current time set as local time at target site.
    # Account for eventual Daylight Saving Time
    tf = TimezoneFinder()
    tz_target = pytz.timezone(tf.certain_timezone_at(lat=lat, lng=lon))
    current_local = tz_target.localize(current)

    return (current_utc - current_local).total_seconds() / 60 / 60



def to_LT(PG, plantID, from_index, to_index):
    """Convert a power generated time series from UTC to LT (local time). Eventual daylight
    saving are taken into account.

    Arguments:
        PG: pandas time series of the power generated with UTC-timestamp indexing
        plantID: plantID to consider in the data frame
        from_index: starting timestamp
        to_index: ending timestamp

    Returns:
        Power generated time series of the selected plantID with LT-timestamp indexing
    """
    daylight_saving = [datetime.strptime('2016-3-13-2', '%Y-%m-%d-%H'),
                       datetime.strptime('2016-11-6-2', '%Y-%m-%d-%H')]

    for enum, i in enumerate(plantID):
        offset = time_offset(2016, 1, 1, 0, 0, 0, WI.genbus.loc[i].lon, WI.genbus.loc[i].lat)
        PG_LT_tmp = pd.DataFrame({i:PG[i].values})
        LT_tmp = (PG.index + timedelta(hours=offset)).tolist()
        if offset == time_offset(2016, 6, 1, 0, 0, 0, WI.genbus.loc[i].lon, WI.genbus.loc[i].lat):
            PG_LT_tmp['LT'] = LT_tmp
            PG_LT_tmp.set_index('LT', inplace=True, drop=True)
        else:
            LT_tmp.remove(daylight_saving[0])
            LT_tmp.insert(LT_tmp.index(daylight_saving[1]), daylight_saving[1]-timedelta(hours=1))
            PG_LT_tmp['LT'] = LT_tmp
            PG_LT_tmp.set_index('LT', inplace=True, drop=True)

        PG_LT_tmp = PG_LT_tmp[from_index:to_index]
        if enum == 0:
            PG_LT = PG_LT_tmp
        else:
            PG_LT = pd.merge(PG_LT, PG_LT_tmp, left_index=True, right_index=True, how='outer')

    return PG_LT


def to_PST(TS, columns, from_index, to_index):
    """Convert a time series from UTC to PST (Pacific Standard Time). Eventual daylight
    saving are taken into account.

    Arguments:
        TS: pandas time series with UTC-timestamp indexing
        columns: columns to consider in the data frame
        from_index: starting timestamp
        to_index: ending timestamp

    Returns:
        Power generated time series of the selected columns with PST-timestamp indexing
    """
    TS_PST = TS[columns]
    TS_PST = TS_PST.set_index(TS.index - timedelta(hours=8))
    TS_PST.index.name = 'PST'

    return TS_PST[from_index:to_index]


def ts_all_onezone(PG, load_zone, from_index='2016-01-01-00', to_index='2017-01-01-00', freq='W'):
    """Plots the time series stack plot for load zone, California or total for western
    interconnect including demand. It also prints the generation for each type.

    Arguments:
        PG: pandas time series of the power generated with UTC-timestamp indexing
        load_zone: load zone to consider. If the load zone is set to total, all the plants in the
                   western interconnect will be considered. If load zone is set to California,
                   the plants located in Northern California, Central California, Bay Area,
                   Southeast California and Southwest California will be considered.

    Options:
        from_index: starting timestamp
        to_index: ending timestamp
        freq: frequency for resampling

    Returns:
        Power generated time series for every available resource in the load zone
    """
    type2label = {'nuclear':'Nuclear',
                  'hydro':'Hydro',
                  'coal':'Coal',
                  'ng':'Natural Gas',
                  'solar':'Solar',
                  'wind':'Wind'}
    if load_zone not in WI.load_zones.values():
        if load_zone == 'total':
            plantID = WI.genbus.index
        elif load_zone == 'California':
            california = ['Northern California',
                          'Central California',
                          'Bay Area',
                          'Southeast California',
                          'Southwest California']
            plantID = []
            for region in california:
                plantID += WI.genbus.groupby('ZoneName').get_group(region).index.values.tolist()
        else:
            print(load_zone + ' not in load_zone list.')
            print('Possible load_zones are ')
            print(WI.load_zones.values())
            return
    else:
        plantID = WI.genbus.groupby('ZoneName').get_group(load_zone).index

    PG_new = to_PST(PG, plantID, from_index, to_index)

    PG_groups = PG_new.T.groupby(WI.genbus['type'])
    PG_stack = PG_groups.agg(sum).T.resample(freq).mean()
    for type in WI.ID2type.values():
        if type not in PG_stack.columns:
            del type2label[type]

    demand_data = to_PST(WI.demand_data_2016, WI.demand_data_2016.columns, from_index, to_index)

    colors=[WI.type2color[type] for type in type2label.keys()]
    ax = PG_stack[list(type2label.keys())].rename(columns=type2label).plot.area(color=colors,
                                                  fontsize=18, alpha=0.7, figsize=(18,12))
    if load_zone == 'total':
        demand_data = demand_data.sum(axis=1)
    elif load_zone == 'California':
        demand_data = demand_data.loc[:,california].sum(axis=1)
    else:
        demand_data = demand_data.loc[:,load_zone]

    demand_data.resample(freq).mean().rename('Demand').plot(color='red', legend='demand', ax=ax)
    ax.set_ylim([0,max(ax.get_ylim()[1], demand_data.resample(freq).mean().max()+100)])

    ax.set_facecolor('white')
    ax.grid(color='black', axis='y')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], frameon = 2, prop={'size':16}, loc='lower right')
    ax.set_xlabel('')
    ax.set_ylabel('Net Generation (MWh)', fontsize=20)
    plt.title('%s: %s - %s' % (load_zone, from_index, to_index), fontsize=20)

    filename = '%s_%s-%s_NetGeneration.png' % (load_zone, from_index, to_index)
    plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0)

    plt.show()

    return PG_stack



def ts_renewable_onezone(PG, type, load_zone,
                         from_index='2016-01-01-00', to_index='2017-01-01-00', freq='W',
                         LT=True, noplot=False, seed=0):
    """Plots the time series of the power generated by solar or wind plants in a given
    load zone, California or total western interconnect. Also show on the same plot the time
    series of power generated by 2, 8 and 15 randomly chosen plants in the load zone.

    Arguments:
        PG: pandas time series of the power generated with UTC-timestamp indexing
        type: Can be 'solar' or 'wind'
        load_zone: load zone to consider. If the load zone is set to total, all the plants in the
                   western interconnect will be considered. If load zone is set to California,
                   the plants located in Northern California, Central California, Bay Area,
                   Southeast California and Southwest California will be considered.

    Options:
        from_index: starting timestamp
        to_index: ending timestamp
        freq: frequency for resampling
        LT: apply the to_LT method to PG. If False the to_PST method is applied instead
        noplot: if True, returns the time converted PG for the chosen renewable resource
        seed: seed for the random selection of plants

    Returns:
        Power generated time series for the chosen renewable resource in the load zone and the
        selected plants in the load zone.
    """
    if type != 'solar' and type != 'wind':
        print('Possible <type> are solar and wind')
        return

    if load_zone not in WI.load_zones.values():
        if load_zone == 'total':
            plantID = WI.genbus.groupby('type').get_group(type).index
        elif load_zone == 'California':
            california = ['Northern California',
                          'Central California',
                          'Bay Area',
                          'Southeast California',
                          'Southwest California']
            plantID = []
            for region in california:
                try:
                    plantID += WI.genbus.groupby(['type','ZoneName']).get_group((type,region)).index.values.tolist()
                except KeyError:
                    continue
        else:
            print(load_zone + ' not in load_zone list.')
            print('Possible load_zones are ')
            print(WI.load_zones.values())
            return
    else:
        g = WI.genbus.groupby(['type','ZoneName'])
        try:
            plantID = g.get_group((type,load_zone)).index
        except KeyError:
            print("No plant in %s" % load_zone)
            return

    n_plants = len(plantID)
    total_capacity = sum(WI.genbus.loc[plantID].GenMWMax.values)

    if LT == True:
        PG_new = to_LT(PG, plantID, from_index, to_index)
    else:
        PG_new = to_PST(PG, plantID, from_index, to_index)

    total = pd.DataFrame(PG_new.T.sum().resample(freq).mean().rename('Total: %d plants (%d MW)' % (n_plants, total_capacity)))

    if noplot == True:
        return total

    if n_plants < 20:
        ax = total.plot(fontsize=18, alpha=0.7, figsize=(18,12), color=WI.type2color[type], lw=5)
        ax.set_facecolor('white')
        ax.grid(color='black', axis='y')
        ax.set_xlabel('')
        ax.set_ylabel('Net Generation (MWh)', fontsize=20)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1],frameon=2, prop={'size':16}, loc='upper right')
        plt.title('%s: %s - %s' % (load_zone, from_index, to_index), fontsize=20)

        filename = '%s_%s_%s-%s_NetGeneration.png' % (load_zone, type, from_index, to_index)
        plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0)

        plt.show()
    else:
        np.random.seed(seed)
        selected = np.random.choice(plantID,15,replace=False).tolist()

        norm = [total_capacity]
        norm += [sum(WI.genbus.loc[selected[:i]].GenMWMax.values) for i in [15,8,2]]

        total['15 plants (%d MW)' % norm[1]] = PG_new[selected].T.sum().resample(freq).mean()
        total['8 plants (%d MW)' % norm[2]] = PG_new[selected[:8]].T.sum().resample(freq).mean()
        total['2 plant (%d MW)' % norm[3]] = PG_new[selected[:2]].T.sum().resample(freq).mean()

        WI.genbus.loc[selected].to_csv('%s_%s_%s-%s.csv' % (load_zone, type, from_index, to_index))

        for i, col in enumerate(total.columns):
            total[col] /= norm[i]

        fig, ax = plt.subplots(figsize=(18,12))
        colors = [WI.type2color[type]]
        if type == 'solar':
            colors += ['red','orangered','darkorange']
        elif type == 'wind':
            colors += ['dodgerblue','teal','turquoise']
        linewidths = [5,3,3,3]
        linestyles = ['-','--','--','--']
        for col, c, lw, ls in zip(total.columns, colors, linewidths, linestyles):
            total[col].plot(fontsize=18, alpha=0.7, lw=lw, ls=ls, color= c, ax=ax)
        ax.set_facecolor('white')
        ax.grid(color='black', axis='y')
        ax.set_xlabel('')
        ax.set_ylabel('Normalized Output', fontsize=20)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], frameon=2, prop={'size':16}, loc='upper right')
        plt.title('%s: %s - %s (%s)' % (load_zone, from_index, to_index, type), fontsize=20)

        filename = '%s_%s_%s-%s_normalized.png' % (load_zone, type, from_index, to_index)
        plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0)

        plt.show()

    return total


def ts_renewable_comp(PG, type, load_zone,
                      from_index='2016-01-01-00', to_index='2016-12-31-00', freq='W',
                      normalize=False):
    """Plots the time series of the power generated by solar or wind plants in various
    load zones. PST is chosen as a common timezone.

    Arguments:
        PG: pandas time series of the power generated with UTC-timestamp indexing
        type: Can be 'solar' or 'wind'
        load_zone: list of load zone. The list can include 'total' and/or California

    Options:
        from_index: starting timestamp
        to_index: ending timestamp
        freq: frequency for resampling
        normalize: if True, the total capacity (in MWh) of the renewable resource in each
                   load zone is used to derive a normalized power generated

    Returns:
        Power generated time series for the chosen renewable resource in the selected load zones
    """
    for i, region in enumerate(load_zone):
        total_zone = ts_renewable_onezone(PG, type, region,
                                          from_index=from_index, to_index=to_index, freq=freq,
                                          noplot=True, LT=False)

        try:
            name = total_zone.columns[0]
        except AttributeError:
            return
        n_plants = name.split()[1]
        capacity = int(name.split()[3].split('(')[1])
        total_zone.rename(columns={name:'%s: %s plants (%d MW)' % (region, n_plants, capacity)},
                          inplace=True)

        norm = capacity if normalize else 1

        if i == 0:
            total = total_zone/norm
        else:
            total = pd.merge(total, total_zone/norm, left_index=True, right_index=True, how='outer')


    fig, ax = plt.subplots(figsize=(18,12))
    for col, region in zip(total.columns, load_zone):
        color = region2style[region]['color']
        alpha = region2style[region]['alpha']
        lw = region2style[region]['lw']
        ls = region2style[region]['ls']
        total[col].plot(fontsize=18, color=color, alpha=alpha, lw=lw, ls=ls, ax=ax)

    ax.set_facecolor('white')
    ax.grid(color='black', axis='y')
    ax.set_xlabel('')
    if normalize:
        ax.set_ylabel('Normalized Output', fontsize=20)
        filename = '%s_%s_%s-%s_normalized.png' % ("-".join(load_zone), type, from_index, to_index)
    else:
        ax.set_ylabel('Net Generation (MWh)', fontsize=20)
        filename = '%s_%s_%s-%s_NetGeneration.png' % ("-".join(load_zone), type, from_index, to_index)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], frameon=2, prop={'size':16}, loc='upper right')
    plt.title('%s - %s (%s)' % (from_index, to_index, type), fontsize=20)
    plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0)
    plt.show()

    return total



def ts_curtailment_onezone(PG, type, load_zone,
                           from_index='2016-01-01-00', to_index='2017-01-01-00', freq='W',
                           LT=True):
    """Plots the time series of the curtailment for solar or wind plants in a given
    load zone, California or total western interconnect. Also show on the same plot
    the time series of the associated power output of the farms and the demand for
    the load zone.

    Arguments:
        PG: pandas time series of the power generated with UTC-timestamp indexing
        type: Can be 'solar' or 'wind'
        load_zone: load zone to consider. If the load zone is set to total, all the plants in the
                   western interconnect will be considered. If load zone is set to California,
                   the plants located in Northern California, Central California, Bay Area,
                   Southeast California and Southwest California will be considered.

    Options:
        from_index: starting timestamp
        to_index: ending timestamp
        freq: frequency for resampling
        LT: apply the to_LT method to PG. If False the to_PST method is applied instead
        noplot: if True, returns the time converted PG for the chosen renewable resource
        seed: seed for the random selection of plants

    Returns:
        Curtailment time series for the chosen renewable resource in the load zone
    """
