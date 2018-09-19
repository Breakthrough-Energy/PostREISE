import westernintnet
WI = westernintnet.WesternIntNet()
import matplotlib.pyplot as plt
import pytz
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import numpy as np
import pandas as pd


def ts_all_onezone(PG, load_zone, from_index='2016-01-01-00', to_index='2017-01-01-00', freq='W'):
    """Plots the time series stack plot for load zone, California or total for
    western interconnect including demand. It also prints the generation for
    for each type.

    """
    type2label = {'nuclear':'Nuclear','hydro':'Hydro','coal':'Coal','ng':'Natural Gas','solar':'Solar','wind':'Wind'}
    if load_zone not in WI.load_zones.values():
        if load_zone=='total':
            plantID = WI.genbus.index
        elif load_zone == 'California':
            california_list = ['Northern California','Central California','Bay Area','Southeast California','Southwest California']
            plantID = []
            for region in california_list:
                plantID = plantID + WI.genbus.groupby('ZoneName').get_group(region).index.values.tolist()
        else:
            print(load_zone + ' not in load_zone list.')
            print('Possible load_zones are ')
            print(WI.load_zones.values())
            return
    else:
        plantID = WI.genbus.groupby('ZoneName').get_group(load_zone).index

    PG_new = to_PST(PG, plantID, from_index, to_index)

    PG_groups = PG_new.T.groupby(WI.genbus['type'])
    agg_df = PG_groups.agg(sum).T.resample(freq).mean()
    for type in WI.ID2type.values():
        if type not in agg_df.columns:
            del type2label[type]

    demand_data = to_PST(WI.demand_data_2016, WI.demand_data_2016.columns, from_index, to_index)

    ax = agg_df.loc[:,list(type2label.keys())].rename(columns=type2label).plot.area(color = [WI.type2color[type] for type in type2label.keys()], fontsize=18, alpha = 0.7, figsize=(18, 12))
    if load_zone=='total':
        demand_data = demand_data.sum(axis=1)
    elif load_zone == 'California':
        demand_data = demand_data.loc[:,california_list].sum(axis=1)
    else:
        demand_data = demand_data.loc[:,load_zone]

    demand_data.resample(freq).mean().rename('Demand').plot(color='red',lw='1',legend='demand',ax=ax)
    ax.set_ylim([0,max(ax.get_ylim()[1] ,demand_data.resample(freq).mean().max()+100)])

    ax.set_facecolor('white')
    ax.grid(color='black',axis='y')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1],frameon = 2,prop={'size': 16},loc='lower right')
    ax.set_xlabel('')
    ax.set_ylabel('Net Generation (MWh)', fontsize=20)
    plt.title('%s: %s - %s' % (load_zone, from_index, to_index), fontsize=20)

    filename = '%s_%s-%s_NetGeneration.png' % (load_zone, from_index, to_index)
    plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0)

    plt.show()


    return agg_df


def time_offset(year, month, day, hour, minute, sec, lon, lat):
    """Calculates time difference between utc and local time for a given location
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


def to_LT(PG, columns, from_index, to_index):
    daylight_saving = [datetime.strptime('2016-3-13-2', '%Y-%m-%d-%H'),
                       datetime.strptime('2016-11-6-2', '%Y-%m-%d-%H')]

    for enum, i in enumerate(columns):
        offset = time_offset(2016, 1, 1, 0, 0, 0, WI.genbus.loc[i].lon, WI.genbus.loc[i].lat)
        PG_LT_tmp = pd.DataFrame({i:PG[i].values})
        LT_tmp = (PG.index + timedelta(hours=offset)).tolist()
        if offset == time_offset(2016, 6, 1, 0, 0, 0, WI.genbus.loc[i].lon, WI.genbus.loc[i].lat):
            PG_LT_tmp['LT'] = LT_tmp
            PG_LT_tmp.set_index('LT', inplace=True, drop=True)
        else:
            LT_tmp.remove(daylight_saving[0])
            LT_tmp.insert(LT_tmp.index(daylight_saving[1]), daylight_saving[1] - timedelta(hours=1))
            PG_LT_tmp['LT'] = LT_tmp
            PG_LT_tmp.set_index('LT', inplace=True, drop=True)

        if enum == 0:
            PG_LT = PG_LT_tmp[from_index:to_index]
        else:
            PG_LT = pd.merge(PG_LT, PG_LT_tmp[from_index:to_index],left_index=True, right_index=True, how='outer')

    return PG_LT


def to_PST(PG, columns, from_index, to_index):
    PG_PST = PG[columns]
    PG_PST = PG_PST.set_index(PG.index - timedelta(hours=8))
    PG_PST.index.name = 'PST'

    return PG_PST[from_index:to_index]

def ts_renewable_onezone(PG, type, load_zone,
                         from_index='2016-01-01-00', to_index='2017-01-01-00', freq='W',
                         LT=True, noplot=False, seed=0):
    """Plots the time series of the power generated by solar or wind plants in a given load zone,
    California or total western interconnect. Also show on the same plot the time series
    of the aggregated 25%, 50% and 75% most powerful plants (in terms of capacity).

    """
    if type != 'solar' and type != 'wind':
        print(type + ' not in type list.')
        print('Possible type are solar and wind')
        return

    if load_zone not in WI.load_zones.values():
        if load_zone == 'total':
            plantID = WI.genbus.groupby('type').get_group(type).index
        elif load_zone == 'California':
            california = ['Northern California','Central California','Bay Area','Southeast California','Southwest California']
            plantID = []
            for region in california:
                try:
                    plantID = plantID + WI.genbus.groupby(['type','ZoneName']).get_group((type,region)).index.values.tolist()
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
            return "No plant in %s" % load_zone

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
        ax = total.plot(fontsize=18, alpha=0.7, figsize=(18, 12), color=WI.type2color[type], lw=5)
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

        fig, ax = plt.subplots()
        colors = [WI.type2color[type]]
        if type == 'solar':
            colors += ['red','orangered','darkorange']
        elif type == 'wind':
            colors += ['dodgerblue','teal','turquoise']
        linewidths    = [5,3,3,3]
        linestyles    = ['-','--','--','--']
        for col, c, lw, ls in zip(total.columns, colors, linewidths, linestyles):
            total[col].plot(fontsize=18, alpha=0.7, figsize=(18, 12), lw=lw, ls=ls, color= c, ax = ax)
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


def ts_renewable_comp(PG, type, load_zone, from_index='2016-01-01-00', to_index='2016-12-31-00', freq='H', normalize=False):

    for i, region in enumerate(load_zone):
        total_zone = ts_renewable_onezone(PG, type, region, from_index=from_index, to_index=to_index, freq=freq, noplot=True, LT=False)
        name = total_zone.columns[0]
        n_plants = name.split()[1]
        capacity = int(name.split()[3].split('(')[1])
        total_zone.rename(columns={name:'%s: %s plants (%d MW)' % (region, n_plants, capacity)}, inplace=True)

        norm = capacity if normalize else 1

        if i == 0:
            total = total_zone/norm
        else:
            total = pd.merge(total, total_zone/norm, left_index=True, right_index=True, how='outer')


    ax = total.plot(fontsize=18, alpha=0.7, figsize=(18, 12), lw=2)
    ax.set_facecolor('white')
    ax.grid(color='black', axis='y')
    ax.set_xlabel('')
    if normalize:
        filename = '%s_%s_%s-%s_normalized.png' % ("-".join(load_zone), type, from_index, to_index)
        ax.set_ylabel('Normalized Output', fontsize=20)
    else:
        ax.set_ylabel('Net Generation (MWh)', fontsize=20)
        filename = '%s_%s_%s-%s_NetGeneration.png' % ("-".join(load_zone), type, from_index, to_index)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], frameon=2, prop={'size':16}, loc='upper right')
    plt.title('%s - %s (%s)' % (from_index, to_index, type), fontsize=20)
    plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0)
    plt.show()



    return total
