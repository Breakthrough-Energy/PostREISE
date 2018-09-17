import westernintnet
WI = westernintnet.WesternIntNet()
import matplotlib.pyplot as plt
import pytz
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import numpy as np
import pandas as pd

def plot_time_series(PG,load_zone,from_index='2016',to_index='2016',freq='W'):
    """Plots the time series stack plot for load zone, California or total for
    western interconnect including demand. It also prints the generation for
    for each type.

    """
    type2label = {'nuclear':'Nuclear','hydro':'Hydro','coal':'Coal','ng':'Natural Gas','solar':'Solar','wind':'Wind'}
    if load_zone not in WI.load_zones.values():
        if load_zone=='total':
            i = WI.genbus.index
        elif load_zone == 'California':
            california_list = ['Northern California','Central California','Bay Area','Southeast California','Southwest California']
            i = []
            for region in california_list:
                i = i + WI.genbus.groupby('ZoneName').get_group(region).index.values.tolist()
        else:
            print(load_zone + ' not in load_zone list.')
            print('Possible load_zones are ')
            print(WI.load_zones.values())
            return
    else:
        i = WI.genbus.groupby('ZoneName').get_group(load_zone).index
    PG_groups = PG[i].T.groupby(WI.genbus['type'])
    agg_df = PG_groups.agg(sum).T.resample(freq).mean()
    for type in WI.ID2type.values():
        if type not in agg_df.columns:
            del type2label[type]

    ax = agg_df.loc[from_index : to_index,list(type2label.keys())].rename(columns=type2label).plot.area(color = [WI.type2color[type] for type in type2label.keys()], fontsize=18, alpha = 0.7, figsize=(18, 12))
    if load_zone=='total':
        demand_data = WI.demand_data_2016.loc[from_index:to_index].sum(axis=1)
    elif load_zone == 'California':
        demand_data = WI.demand_data_2016.loc[from_index:to_index,california_list].sum(axis=1)
    else:
        demand_data = WI.demand_data_2016.loc[from_index:to_index,load_zone]

    demand_data.resample(freq).mean().rename('Demand').plot(color='red',lw='1',legend='demand',ax=ax)
    ax.set_ylim([0,max(ax.get_ylim()[1] ,demand_data.resample(freq).mean().max()+100)])

    ax.set_facecolor('white')
    ax.grid(color='black',axis='y')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1],frameon = 2,prop={'size': 16},loc='lower right')
    ax.set_xlabel('')
    plt.title(load_zone)
    plt.show()
    print(agg_df)


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


def plot_solar(PG, load_zone, from_index='2016', to_index='2016', freq='W'):
    """Plots the time series of the power generated by solar plants in a given load zone,
    California or total western interconnect. Also show on the same plot the time series
    of the aggregated 25%, 50% and 75% most powerful plants (in terms of capacity).

    """
    if load_zone not in WI.load_zones.values():
        if load_zone == 'total':
            plantID = WI.genbus.groupby('type').get_group('solar').index
        elif load_zone == 'California':
            california = ['Northern California',
                          'Central California',
                          'Bay Area',
                          'Southeast California',
                          'Southwest California']
            plantID = []
            for region in california:
                plantID = plantID + WI.genbus.groupby(['type','ZoneName']).get_group(('solar',region)).index.values.tolist()
        else:
            print(load_zone + ' not in load_zone list.')
            print('Possible load_zones are ')
            print(WI.load_zones.values())
            return
    else:
        g = WI.genbus.groupby(['type','ZoneName'])
        try:
            plantID = g.get_group(('solar',load_zone)).index
        except KeyError:
            return "No solar plant in %s" % load_zone

    n_plants = len(plantID)
    daylight_saving = [datetime.strptime('2016/3/13/2', '%Y/%m/%d/%H'),
                       datetime.strptime('2016/11/6/2', '%Y/%m/%d/%H')]

    for enum, i in enumerate(plantID):
        # Get local time
        offset = time_offset(2016, 1, 1, 0, 0, 0, WI.genbus.loc[i].lon, WI.genbus.loc[i].lat)
        PG_lt_tmp = pd.DataFrame({i:PG[i].values})
        lt_tmp = (PG.index + timedelta(hours=offset)).tolist()
        # Is this a daylight saving location
        if offset == time_offset(2016, 6, 1, 0, 0, 0, WI.genbus.loc[i].lon, WI.genbus.loc[i].lat):
            PG_lt_tmp['lt'] = lt_tmp
            PG_lt_tmp.set_index('lt', inplace=True, drop=True)
        else:
            lt_tmp.remove(daylight_saving[0])
            lt_tmp.insert(lt_tmp.index(daylight_saving[1]),
                          datetime.strptime('2016/11/6/1', '%Y/%m/%d/%H'))
            PG_lt_tmp['lt'] = lt_tmp
            PG_lt_tmp.set_index('lt', inplace=True, drop=True)

        if enum == 0:
            PG_lt = PG_lt_tmp[from_index:to_index]
        else:
            PG_lt = pd.merge(PG_lt, PG_lt_tmp[from_index:to_index],
                             left_index=True, right_index=True, how='outer')

    total = pd.DataFrame(PG_lt.T.sum().resample(freq).mean().rename('Total: %d plants' % n_plants))

    if n_plants < 20:
        ax = total.plot(fontsize=18, alpha=0.7, figsize=(18, 12),
                        color=WI.type2color['solar'], lw=2)
        ax.set_facecolor('white')
        ax.grid(color='black', axis='y')
        ax.set_xlabel('Local Time', fontsize=20)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1],frameon=2, prop={'size':16}, loc='upper right')
        plt.title(load_zone, fontsize=20)
        plt.show()
    else:
        top_25p = WI.genbus.loc[plantID].GenMWMax.sort_values(ascending=False)[:n_plants//4].index
        top_50p = WI.genbus.loc[plantID].GenMWMax.sort_values(ascending=False)[:n_plants//2].index
        top_75p = WI.genbus.loc[plantID].GenMWMax.sort_values(ascending=False)[:n_plants*3//4].index

        total['Top 25%'] = PG_lt[top_25p].T.sum().resample(freq).mean()
        total['Top 50%'] = PG_lt[top_50p].T.sum().resample(freq).mean()
        total['Top 75%'] = PG_lt[top_75p].T.sum().resample(freq).mean()

        ax = total.plot(fontsize=18, alpha=0.7, figsize=(18, 12), lw=2,
                        color=[WI.type2color['solar'],'red','orangered','darkorange'])
        ax.set_facecolor('white')
        ax.grid(color='black', axis='y')
        ax.set_xlabel('Local Time', fontsize=20)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], frameon=2, prop={'size':16}, loc='upper right')
        plt.title(load_zone, fontsize=20)
        plt.show()



def plot_wind(PG, load_zone, from_index='2016', to_index='2016', freq='W'):
    """Plots the time series of the power generated by wind farms in a given load zone,
    Californiaor total western interconnect. Also show on the same plot the time series
    of the aggregated 25%, 50% and 75% most powerful plants (in terms of capacity).

    """
    if load_zone not in WI.load_zones.values():
        if load_zone == 'total':
            plantID = WI.genbus.groupby('type').get_group('wind').index
        elif load_zone == 'California':
            california = ['Northern California',
                          'Central California',
                          'Bay Area',
                          'Southeast California',
                          'Southwest California']
            plantID = []
            for region in california:
                try:
                    plantID = plantID + WI.genbus.groupby(['type','ZoneName']).get_group(('wind',region)).index.values.tolist()
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
            plantID = g.get_group(('wind',load_zone)).index
        except KeyError:
            return "No wind farm in %s" % load_zone

    n_plants = len(plantID)
    daylight_saving = [datetime.strptime('2016/3/13/2', '%Y/%m/%d/%H'),
                       datetime.strptime('2016/11/6/2', '%Y/%m/%d/%H')]

    for enum, i in enumerate(plantID):
        # Get local time
        offset = time_offset(2016, 1, 1, 0, 0, 0, WI.genbus.loc[i].lon, WI.genbus.loc[i].lat)
        PG_lt_tmp = pd.DataFrame({i:PG[i].values})
        lt_tmp = (PG.index + timedelta(hours=offset)).tolist()
        # Is this a daylight saving location
        if offset == time_offset(2016, 6, 1, 0, 0, 0, WI.genbus.loc[i].lon, WI.genbus.loc[i].lat):
            PG_lt_tmp['lt'] = lt_tmp
            PG_lt_tmp.set_index('lt', inplace=True, drop=True)
        else:
            lt_tmp.remove(daylight_saving[0])
            lt_tmp.insert(lt_tmp.index(daylight_saving[1]),
                          datetime.strptime('2016/11/6/1', '%Y/%m/%d/%H'))
            PG_lt_tmp['lt'] = lt_tmp
            PG_lt_tmp.set_index('lt', inplace=True, drop=True)

        if enum == 0:
            PG_lt = PG_lt_tmp[from_index:to_index]
        else:
            PG_lt = pd.merge(PG_lt, PG_lt_tmp[from_index:to_index],
                             left_index=True, right_index=True, how='outer')

    total = pd.DataFrame(PG_lt.T.sum().resample(freq).mean().rename('Total: %d plants' % n_plants))

    if n_plants < 20:
        ax = total.plot(fontsize=18, alpha=0.7, figsize=(18, 12),
                        color=WI.type2color['wind'], lw=2)
        ax.set_facecolor('white')
        ax.grid(color='black', axis='y')
        ax.set_xlabel('Local Time', fontsize=20)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1],frameon=2, prop={'size':16}, loc='upper right')
        plt.title(load_zone, fontsize=20)
        plt.show()
    else:
        top_25p = WI.genbus.loc[plantID].GenMWMax.sort_values(ascending=False)[:n_plants//4].index
        top_50p = WI.genbus.loc[plantID].GenMWMax.sort_values(ascending=False)[:n_plants//2].index
        top_75p = WI.genbus.loc[plantID].GenMWMax.sort_values(ascending=False)[:n_plants*3//4].index

        total['Top 25%'] = PG_lt[top_25p].T.sum().resample(freq).mean()
        total['Top 50%'] = PG_lt[top_50p].T.sum().resample(freq).mean()
        total['Top 75%'] = PG_lt[top_75p].T.sum().resample(freq).mean()

        ax = total.plot(fontsize=18, alpha=0.7, figsize=(18, 12), lw=2,
                        color=[WI.type2color['wind'],'dodgerblue','teal','turquoise'])
        ax.set_facecolor('white')
        ax.grid(color='black', axis='y')
        ax.set_xlabel('Local Time', fontsize=20)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1], frameon=2, prop={'size':16}, loc='upper right')
        plt.title(load_zone, fontsize=20)
        plt.show()
