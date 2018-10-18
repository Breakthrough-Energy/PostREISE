import sys
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytz
import seaborn as sns
from matplotlib.ticker import AutoMinorLocator

from westernintnet.westernintnet import WesternIntNet
from timezonefinder import TimezoneFinder

WI = WesternIntNet()

sys.path.append("./test")



California = ['Northern California',
              'Central California',
              'Bay Area',
              'Southeast California',
              'Southwest California']



zone2style = {'Washington':{'color':'green', 'alpha':1, 'lw':4, 'ls':'-'},
              'Oregon':{'color':'red', 'alpha':1, 'lw':4, 'ls':'-'},
              'California':{'color':'blue', 'alpha':1, 'lw':4, 'ls':'-'},
              'Northern California':{'color':'blue', 'alpha':0.6, 'lw':4, 'ls':'--'},
              'Bay Area':{'color':'blue', 'alpha':0.6, 'lw':4, 'ls':':'},
              'Central California':{'color':'blue', 'alpha':0.6, 'lw':4, 'ls':'-.'},
              'Southwest California':{'color':'blue', 'alpha':0.6, 'lw':4, 'ls':'-+'},
              'Southeast California':{'color':'blue', 'alpha':0.6, 'lw':4, 'ls':'-o'},
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



scenarios_total = {'x1':['PG.pkl','PG_EnhancedGrid.pkl'],
                   'x2':['PG_RenX2.pkl','PG_EnhancedGridRenX2.pkl'],
                   'x3':['PG_RenX3.pkl','PG_EnhancedGridRenX3.pkl'],
                   'x4':['PG_RenX4.pkl','PG_EnhancedGridRenX4.pkl']}



scenarios_California = {'x1':['PG.pkl','PG_CAEnhancedGrid.pkl'],
                        'x2':['PG_CARenX2.pkl','PG_CAEnhancedGridRenX2.pkl'],
                        'x3':['PG_CARenX3.pkl','PG_CAEnhancedGridRenX3.pkl'],
                        'x4':['PG_CARenX4.pkl','PG_CAEnhancedGridRenX4.pkl']}



def time_offset(year, month, day, hour, minute, sec, lon, lat):
    """Calculates time difference between UTC and local time for a given \ 
        location.

    :param int year: year of the timestamp.
    :param int month: month of the timestamp.
    :param int day: day of the timestamp.
    :param int hour: hour of the timestamp.
    :param int minute: minute of the timestamp.
    :param int sec: second of the timestamp.
    :param float lon: longitude of the site (in deg.) measured eastward from \ 
        Greenwich.
    :param float lat: latitude of the site (in deg.). Equator is the zero point.
    :return: offset (in hours) between UTC and local time.
    """
    current = datetime(year, month, day, hour, minute, sec)

    # Current time set as UTC
    current_utc = pytz.utc.localize(current)

    # Current time set as local time at target site.
    # Account for eventual daylight saving time
    tf = TimezoneFinder()
    tz_target = pytz.timezone(tf.certain_timezone_at(lat=lat, lng=lon))
    current_local = tz_target.localize(current)

    return (current_utc - current_local).total_seconds() / 60 / 60



def to_PST(DF, columns, from_index, to_index):
    """Converts UTC timestamp indexing to PST (Pacific Standard Time) \ 
        timestamp indexing in a data frame.

    :param DF: pandas DataFrame of the power generated (load) with id of all \ 
        the plants (all 16 load zones) as columns and UTC timestamp as indices.
    :param columns: columns to consider in the pandas DataFrame.
    :param string from_index: starting timestamp.
    :param string to_index: ending timestamp.
    :return: data frame of power generated (load) with id of the selected \ 
        plants (load zones) as columns and PST timestamp indexing.
    """
    
    DF_PST = DF[columns]
    DF_PST.set_index(pd.to_datetime(DF_PST.index) - timedelta(hours=8), inplace=True)
    DF_PST.index.name = 'PST'

    return DF_PST[from_index:to_index]



def to_LT(PG, plantID, from_index, to_index):
    """Converts UTC timestamp indexing to LT (local time) timestamp indexing \ 
        in a power generated data frame

    :param PG: pandas DataFrame of the power generated and id of all the \ 
        plants as columns and UTC timestamp as indices.
    :param plantID: id of the plants to consider in the data frame.
    :param string from_index: starting timestamp.
    :param string to_index: ending timestamp.
    :return: data frame of the power generated with id of the selected plants \ 
        as columns and LT timestamp as indices.
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


def get_plantID(zone):
    """Lists the id of the plants located in a given zone.

    :param zone: one of the zones defined as keys in the \ 
        :py:const:`zone2style` dictionary.
    :param return: id of the plants in the selected zone.
    """
    
    if zone not in WI.load_zones.values():
        if zone == 'total':
            plantID = WI.genbus.index
        elif zone == 'California':
            plantID = []
            for load_zone in California:
                plantID += WI.genbus.groupby('ZoneName').get_group(load_zone).index.values.tolist()
        else:
            print('Possible zones are:')
            print(WI.load_zones.values())
            return
    else:
        plantID = WI.genbus.groupby('ZoneName').get_group(zone).index

    return plantID


def get_demand(demand, zone):
    """Get demand profile for load zone, California or total.

    :param demand: pandas DataFrame of the load with UTC timestamp indexing.
    :param string zone: one of the zones defined as keys in the \ 
        :py:const:`zone2style` dictionary.
    :return: data frame of the load with selected zone as columns and UTC \ 
        timestamp as indices.
    """
    if zone == 'total':
        return demand.sum(axis=1)
    elif zone == 'California':
        return demand.loc[:,California].sum(axis=1)
    else:
        return demand.loc[:,zone]


def IsRenewableResource(type):
    """Is energy resource renewable.

    :param string type: fuel type.
    """
    if type != 'solar' and type != 'wind':
        print('Possible type are solar and wind')
        return


def ts_all_onezone(PG, zone, from_index='2016-01-01-00', to_index='2017-01-01-00', freq='W'):
    """Plots the time series stack plot for load zone, California or total \ 
        including demand. It also prints the generation for each type.

    :param PG: pandas DataFrame of the power generated with id of the plants \ 
        as columns and UTC timestamp as indiced.
    :param sring zone: one of the zones defined as keys in the \ 
        :py:const:`zone2style` dictionary.
    :param string from_index: starting timestamp.
    :param string to_index: ending timestamp.
    :param freq: frequency for resampling.
    :return: data frame of the power generated in the slected zone with \ 
        fuel type as columns and PST timestamp as indices.
    """
    type2label = {'nuclear':'Nuclear',
                  'hydro':'Hydro',
                  'coal':'Coal',
                  'ng':'Natural Gas',
                  'solar':'Solar',
                  'wind':'Wind'}

    plantID = get_plantID(zone)
    PG_new = to_PST(PG, plantID, from_index, to_index)

    PG_groups = PG_new.T.groupby(WI.genbus['type'])
    PG_stack = PG_groups.agg(sum).T.resample(freq).mean()
    for type in WI.ID2type.values():
        if type not in PG_stack.columns:
            del type2label[type]


    demand = to_PST(WI.demand_data_2016, WI.demand_data_2016.columns, from_index, to_index)
    demand = get_demand(demand, zone)

    colors=[WI.type2color[type] for type in type2label.keys()]
    ax = PG_stack[list(type2label.keys())].rename(columns=type2label).plot.area(color=colors,
                                                  fontsize=18, alpha=0.7, figsize=(20,12))

    demand.resample(freq).mean().rename('Demand').plot(color='red', legend='demand', lw=4, ax=ax)
    ax.set_ylim([0,max(ax.get_ylim()[1], demand.resample(freq).mean().max()+100)])

    ax.set_facecolor('white')
    ax.grid(color='black', axis='y')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], frameon = 2, prop={'size':16}, loc='lower right')
    ax.set_xlabel('')
    ax.set_ylabel('Net Generation (MWh)', fontsize=20)
    plt.title('%s: %s - %s' % (zone, from_index, to_index), fontsize=20)

    filename = '.\Images\%s_%s-%s_NetGeneration.png' % (zone, from_index, to_index)
    plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0)

    plt.show()

    return PG_stack


def ts_renewable_onezone(PG, type, zone, from_index='2016-01-01-00', 
                         to_index='2017-01-01-00', freq='W', LT=True, seed=0):
    """Plots the time series of the power generated by solar or wind plants \ 
        for load zone, California or total. Also shows the time series of the \
        power generated by 2, 8 and 15 randomly chosen plants in the same zone.

    :param PG: pandas DataFrame of the power generated with id of the plants \ 
        as columns and UTC timestamp as indiced.
    :param string type: one of *solar* or *wind*.
    :param string zone: one of the zones defined as keys in the \ 
        :py:const:`zone2style` dictionary.
    :param string from_index: starting timestamp.
    :param string to_index: ending timestamp.
    :param freq: frequency for resampling.    
    :param bool LT: should the UTC time be converted to local time or Pacific \ 
        Standard Time.
    :param seed: seed for the random selection of plants.
    :return: data frame of the power generated of the selected renewable \ 
        resource with selected zone as column and selected timestamp as \ 
        indices.
    """
    IsRenewableResource(type)
    plantID = list(set(get_plantID(zone)).intersection(WI.genbus.groupby('type').get_group(type).index))
    n_plants = len(plantID)
    if n_plants == 0:
        print("No %s plants in %s" % (type,zone))
        return

    total_capacity = sum(WI.genbus.loc[plantID].GenMWMax.values)

    if LT == True:
        PG_new = to_LT(PG, plantID, from_index, to_index)
    else:
        PG_new = to_PST(PG, plantID, from_index, to_index)

    total = pd.DataFrame(PG_new.T.sum().resample(freq).mean().rename('Total: %d plants (%d MW)' % (n_plants, total_capacity)))

    if n_plants < 20:
        ax = total.plot(fontsize=18, alpha=0.7, figsize=(20,12), color=WI.type2color[type], lw=5)
        ax.set_facecolor('white')
        ax.grid(color='black', axis='y')
        ax.set_xlabel('')
        ax.set_ylabel('Net Generation (MWh)', fontsize=20)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1],frameon=2, prop={'size':16}, loc='upper right')
        plt.title('%s: %s - %s' % (zone, from_index, to_index), fontsize=20)

        filename = '.\Images\%s_%s_%s-%s_NetGeneration.png' % (zone, type, from_index, to_index)
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

        WI.genbus.loc[selected].to_csv('.\Images\%s_%s_%s-%s.csv' % (zone, type, from_index, to_index))

        for i, col in enumerate(total.columns):
            total[col] /= norm[i]

        fig, ax = plt.subplots(figsize=(20,12))
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
        plt.title('%s: %s - %s (%s)' % (zone, from_index, to_index, type), fontsize=20)

        filename = '.\Images\%s_%s_%s-%s_normalized.png' % (zone, type, from_index, to_index)
        plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0)

        plt.show()

    return total


def ts_renewable_comp(PG, type, zone_list, from_index='2016-01-01-00', 
                      to_index='2016-12-31-00', freq='W', normalize=False):
    """Plots the time series of the power generated by solar or wind plants \ 
        for various load zones.

    :param PG: pandas DataFrame of the power generated with id of the plants \ 
        as columns and UTC timestamp as indiced.
    :param string type: one of *solar* or *wind*.
    :param zone: list of zones defined as keys in the \ 
        :py:const:`zone2style` dictionary.
    :param string from_index: starting timestamp.
    :param string to_index: ending timestamp.
    :param freq: frequency for resampling.
    :param bool normalize: if True, the total capacity of the renewable \
        resource in each load zone is used to derive a normalized power \
        generated.
    :return: data frame of the power generated by the selected renewable \
        resource with the selected zones as columns and PST timestamp as \ 
        indices.
    """
    IsRenewableResource(type)

    for i, zone in enumerate(zone_list):
        plantID = list(set(get_plantID(zone)).intersection(WI.genbus.groupby('type').get_group(type).index))
        n_plants = len(plantID)
        if n_plants == 0:
            print("No %s plants in %s" % (type,zone))
            return
        capacity = sum(WI.genbus.loc[plantID].GenMWMax.values)

        PG_new = to_PST(PG, plantID, from_index, to_index)
        total_zone = pd.DataFrame(PG_new.T.sum().resample(freq).mean().rename('%s: %d plants (%d MW)' % (zone, n_plants, capacity)))

        norm = capacity if normalize else 1

        if i == 0:
            total = total_zone/norm
        else:
            total = pd.merge(total, total_zone/norm, left_index=True, right_index=True, how='outer')

    fig, ax = plt.subplots(figsize=(20,12))
    for col, zone in zip(total.columns, zone_list):
        color = zone2style[zone]['color']
        alpha = zone2style[zone]['alpha']
        lw = zone2style[zone]['lw']
        ls = zone2style[zone]['ls']
        total[col].plot(fontsize=18, color=color, alpha=alpha, lw=lw, ls=ls, ax=ax)

    ax.set_facecolor('white')
    ax.grid(color='black', axis='y')
    ax.set_xlabel('')
    if normalize:
        ax.set_ylabel('Normalized Output', fontsize=20)
        filename = '.\Images\%s_%s_%s-%s_normalized.png' % ("-".join(zone_list), type, from_index, to_index)
    else:
        ax.set_ylabel('Net Generation (MWh)', fontsize=20)
        filename = '.\Images\%s_%s_%s-%s_NetGeneration.png' % ("-".join(zone_list), type, from_index, to_index)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], frameon=2, prop={'size':16}, loc='upper left')
    plt.title('%s - %s (%s)' % (from_index, to_index, type), fontsize=20)

    plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0)

    plt.show()

    return total



def ts_curtailment_onezone(PG, type, zone,
                           from_index='2016-01-01-00', to_index='2017-01-01-00', freq='W',
                           multiplier=1):
    """Plots the time series of the curtailment for solar or wind plants for \ 
        load zone, California or total. Also shows the time series of the \ 
        demand for the zone along with the power produced by the plants in \ 
        the zone.

    :param PG: pandas DataFrame of the power generated with id of the plants \ 
        as columns and UTC timestamp as indiced.
    :param string type: one of *solar* or *wind*.
    :param string zone: one of the zones defined as keys in the \ 
        :py:const:`zone2style` dictionary.
    :param string from_index: starting timestamp.
    :param string to_index: ending timestamp.
    :param freq: frequency for resampling.
    :param multiplier: multiplier for renewable power output.
    :return: data frame with ['Produced', Used', 'Ratio', 'Demand'] as \ 
        columns and UTC timestamp as indices for the selected renewable \
        resource in the selected zone.
    """
    IsRenewableResource(type)

    plantID = list(set(get_plantID(zone)).intersection(WI.genbus.groupby('type').get_group(type).index))
    n_plants = len(plantID)
    if n_plants == 0:
        print("No %s plants in %s" % (type,zone))
        return
    capacity = sum(WI.genbus.loc[plantID].GenMWMax.values)

    produced = to_PST(eval('WI.'+type+'_data_2016'), plantID, from_index, to_index)
    demand = to_PST(WI.demand_data_2016, WI.demand_data_2016.columns, from_index, to_index)
    used = to_PST(PG, plantID, from_index, to_index)

    curtailment = pd.DataFrame(produced.T.sum().resample(freq).mean().rename('Produced'))
    curtailment['Used'] = used.T.sum().resample(freq).mean().values
    curtailment['Demand'] = get_demand(demand,zone).resample(freq).mean().values

    curtailment['Produced'] *= multiplier
    curtailment['Ratio'] = 100 * (curtailment['Produced'] - curtailment['Used']) / curtailment['Produced']

    # Deal with numerical precision
    curtailment.loc[abs(curtailment['Ratio']) < 0.5, 'Ratio'] = 0

    fig, ax = plt.subplots(figsize=(20,12))
    ax_MW = ax.twinx()

    curtailment['Ratio'].plot(ax=ax, legend=False, style='b', lw=4, fontsize=18, alpha=0.7)
    curtailment[['Produced','Demand']].plot(ax=ax_MW, style={'Produced':'g', 'Demand':'r'}, lw=4, fontsize=18, alpha=0.7)

    ax.set_facecolor('white')
    ax.grid(color='black', axis='y')
    ax.set_xlabel('')
    ax.set_ylabel('Curtailment [%]', fontsize=20)
    ax_MW.set_ylabel('MW', fontsize=20)
    ax_MW.legend(loc='upper right', prop={'size':16})

    plt.title('%s: %s - %s (%s x%d)' % (zone, from_index, to_index, type, multiplier), fontsize=20)

    filename = '.\Images\%s_%sx%d_%s-%s_curtailment.png' % (zone, type, multiplier, from_index, to_index)
    plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0)

    plt.show()

    return curtailment



def scenarios_renewable_onezone(zone):
    """Plots for various scenarios the power generated by wind farms and \ 
        solar plants for California or total with respect to the total power \ 
        generated in that zone.

    :param string zone: either *total* or *California*.
    """
    if zone == 'total':
        scenarios = scenarios_total
    elif zone == 'California':
        scenarios = scenarios_California
    else:
        print('Only total and California are available')
        return

    plantID_zone = get_plantID(zone)

    plantID = []
    for type in ['solar','wind']:
        plantID += list(set(plantID_zone).intersection(WI.genbus.groupby('type').get_group(type).index))

    n_scenarios = len(scenarios.keys())
    allotment = np.zeros(n_scenarios*2).reshape(n_scenarios,2)

    for i, files in enumerate(scenarios.values()):
        for j, f in enumerate(files):
            if f:
                PG_tmp = pd.read_pickle(f)
                allotment[i,j] = 100 * PG_tmp[plantID].sum(axis=1).sum() / PG_tmp[plantID_zone].sum(axis=1).sum()

    fig, ax = plt.subplots(figsize=(18,16))

    ax.set_facecolor('white')
    ax.grid(color='black', axis='y')
    ax.tick_params(labelsize=18)
    ax.set_xlabel('Renewable Energy', fontsize=20)
    ax.set_ylabel('Renewable Energy Generation [%]', fontsize=20)

    ax.plot(scenarios.keys(), allotment[:,0], 'r-o', label='Current Grid', lw=4, markersize=12)
    ax.plot(scenarios.keys(), allotment[:,1], 'b-o', label='Enhanced Grid',lw=4, markersize=12)
    for i in range(len(allotment)):
        ax.annotate('%.1f%%' % allotment[i,0], xy=(list(scenarios.keys())[i],allotment[i,0]),
                    xytext=(list(scenarios.keys())[i],allotment[i,0]-0.5),
                    horizontalalignment='left', verticalalignment='top', fontsize=14, color='r')
        ax.annotate('%.1f%%' % allotment[i,1], xy=(list(scenarios.keys())[i],allotment[i,1]),
                    xytext=(list(scenarios.keys())[i],allotment[i,1]+0.5),
                    horizontalalignment='right', verticalalignment='bottom', fontsize=14, color='b')



    ax.legend(loc='lower right', prop={'size':16})

    filename = '.\Images\%s_renewable_scenarios.png' % (zone)
    plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0)

    plt.show()



def scenarios_onezone(zone):
    """Plots the stacked power generated for California or total for \ 
        various scenarios.

    :param zone: either *total* or *California*.
    :return: data frame of the allotment of power generated with fuel type as \ 
        columns.
    """
    if zone == 'total':
        scenarios = scenarios_total
    elif zone == 'California':
        scenarios = scenarios_California
    else:
        print('Only <total> and <California> are available')
        return

    type2label = {'nuclear':'Nuclear',
                  'hydro':'Hydro',
                  'coal':'Coal',
                  'ng':'Natural Gas',
                  'solar':'Solar',
                  'wind':'Wind'}

    plantID = get_plantID(zone)
    n_scenarios = len(scenarios.keys())

    allotment = pd.DataFrame(columns=type2label.keys(), index=range(n_scenarios*2))
    ytitle = [None]*n_scenarios*2

    for i, files in enumerate(scenarios.values()):
        for j, f in enumerate(files):
            if f:
                PG_zone = pd.read_pickle(f)[plantID]
                total = PG_zone.sum(axis=1).sum()
                PG_groups = PG_zone.T.groupby(WI.genbus['type'])
                PG_stack = PG_groups.agg(sum).T
                for type in WI.ID2type.values():
                    if type not in PG_stack.columns:
                        del type2label[type]

                if j == 0:
                    allotment.loc[i,type2label.keys()] = [PG_stack.sum()[type]/total for type in type2label.keys()]
                    ytitle[i] = list(scenarios.keys())[i]+' Current Renewable'
                else:
                    allotment.loc[n_scenarios+i,type2label.keys()] = [PG_stack.sum()[type]/total for type in type2label.keys()]
                    ytitle[n_scenarios+i] = list(scenarios.keys())[i]+' Current Renewable'


    allotment_plot = allotment.copy()
    for i in allotment.index:
        if allotment_plot.loc[i,'nuclear'] != np.nan:
            allotment_plot.loc[i,['nuclear','hydro','coal','ng']] *= -1


    colors = [WI.type2color[type] for type in type2label.keys()]
    ax = allotment_plot[list(type2label.keys())].rename(columns=type2label).plot(kind='barh', stacked=True, figsize=(18, 16), label=True, color=colors, alpha=0.7, fontsize=18)


    ax.set_facecolor('white')
    ax.axvline(0, 0, 1, color='black')
    ax.grid(color='black', which='major')
    ax.grid(color='gray', which='minor', alpha=0.5)
    ax.set_xticklabels([80,70,60,50,40,30,20,10,0,10,20,30,40])
    ax.set_xticks([-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0,0.1,0.2,0.3,0.4])
    ax.legend(frameon=2, loc='upper left', prop={'size': 16})
    ax.set_yticklabels(ytitle)
    ax.set_xlabel('Generation [%]', fontsize=20)
    ax.tick_params(labelsize=18)
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))

    filename = '.\Images\%s_scenarios.png' % (zone)
    plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0, transparent=True)

    plt.show()

    return allotment



def upgrade_impact(zone_ref, zone_tostudy, grid=0):
    """Plots the stacked power generated for California along with other \ 
        zones for available scenarios energy and grid.

    :param string zone_ref: *California*.
    :param zone_tostudy: list of zones defined as keys in \ 
        :py:const:`zone2style` dictionary.
    :return: list of data frame of the allotment of power generated in \ 
        various zones. Each data frame has the fuel type as columns and the \ 
        the scenario name as indices.
    """
    if zone_ref == 'California':
        scenarios = scenarios_California
    else:
        print('Only California is available')
        return

    if grid == 0:
        main_title = 'Current Grid'
    elif grid == 1:
        main_title = 'Enhanced Grid'
    else:
        print('Incorrect grid type:')
        print('grid=0: current grid, grid=1: enhanced grid')
        return

    zone = [z for z in zone_tostudy]
    zone.append(zone_ref)
    allotment = []
    title = []

    for key, files in scenarios.items():
        f = files[grid]
        if f:
            PG = pd.read_pickle(f)
            allotment_scenario = pd.DataFrame(columns=['nuclear','hydro','coal','ng','solar','wind'], index=zone)
            for z in zone:
                type2label = {'nuclear':'Nuclear',
                              'hydro':'Hydro',
                              'coal':'Coal',
                              'ng':'Natural Gas',
                              'solar':'Solar',
                              'wind':'Wind'}
                PG_zone = PG[get_plantID(z)]
                total = PG_zone.sum(axis=1).sum()
                PG_groups = PG_zone.T.groupby(WI.genbus['type'])
                PG_stack = PG_groups.agg(sum).T
                for type in WI.ID2type.values():
                    if type not in PG_stack.columns:
                        del type2label[type]

                allotment_scenario.loc[z,type2label.keys()] = [PG_stack.sum()[type]/1000. for type in type2label.keys()]


            allotment.append(allotment_scenario)
            title.append('Renewable %s' % key)



    fig, ax = plt.subplots(figsize=(18,12))

    ax.set_facecolor('white')
    ax.grid(color='black', axis='y')
    ax.tick_params(labelsize=18)
    ax.set_ylabel('Generation [GWh]', fontsize=20)
    ax.set_title(main_title, fontsize=20)

    colors = [WI.type2color[type] for type in type2label.keys()]
    for df in allotment:
        ax = df.rename(columns={'nuclear':'Nuclear',
                                'hydro':'Hydro',
                                'coal':'Coal',
                                'ng':'Natural Gas',
                                'solar':'Solar',
                                'wind':'Wind'}).plot(kind="bar",
                                                     linewidth=0,
                                                     stacked=True,
                                                     ax=ax,
                                                     color=colors,
                                                     label=True,
                                                     alpha=0.7,
                                                     fontsize=18)
    ax.set_ylim(0,ax.get_ylim()[1])
    ax.ticklabel_format(axis='y', useOffset=False, style='plain')

    n_col = len(type2label.keys())
    n_df = len(allotment)
    n_ind = len(zone)
    h, l = ax.get_legend_handles_labels() # get the handles we want to modify
    for i in range(0, n_df * n_col, n_col): # len(h) = n_col * n_df
        for j, pa in enumerate(h[i:i+n_col]):
            for rect in pa.patches: # for each index
                rect.set_x(rect.get_x() + 1 / float(n_df + 1) * i / float(n_col))
                rect.set_hatch('/' * int(i / n_col)) # edited part
                rect.set_width(1 / float(n_df + 1))

    ax.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
    ax.set_xticklabels(df.index, rotation = 0)

    # Add invisible data to add another legend
    n = [ax.bar(0, 0, color="gray", hatch='/' * i) for i in range(n_df)]

    l1 = ax.legend(h[:n_col], l[:n_col], loc=[1.01, 0.5], fontsize=20)
    l2 = ax.legend(n, title, loc=[1.01, 0.1], fontsize=20)
    ax.add_artist(l1)
    ax.add_artist(l2)

    filename = '.\Images\%s_upgrade_impact.png' % (zone_ref)
    plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0)

    plt.show()

    return allotment



def corr_renewable(PG, type, zone):
    """Plots the correlation between solar or wind power generated in \ 
        various zones.

    :param PG: pandas DataFrame of the power generated with id of the plants \ 
        as columns and UTC timestamp as indiced.
    :param string type: one of *solar* or *wind*.
    :param zone: list of zones defined as keys in the \ 
        :py:const:`zone2style` dictionary.
    :return: data frame of the power generated  by the selected renewable \
        resource with the selected zones as columns and UTC timestamp as \ 
        indices.
    """
    IsRenewableResource(type)

    for i, z in enumerate(zone):
        plantID = list(set(get_plantID(z)).intersection(WI.genbus.groupby('type').get_group(type).index))
        n_plants = len(plantID)
        if n_plants == 0:
            print("No %s plants in %s" % (type,z))
            return
        if i == 0:
            PG_zone = pd.DataFrame({z:PG[plantID].sum(axis=1).values}, index=PG.index)
        else:
            PG_zone[z] = PG[plantID].sum(axis=1).values

    PG_zone.index.name = 'UTC'

    corr = PG_zone.corr()
    fig, ax = plt.subplots(figsize=(12,12))
    if type == 'solar':
        palette = 'OrRd'
    elif type == 'wind':
        palette='Greens'

    ax = sns.heatmap(corr, annot=True, fmt=".2f", cmap=palette, ax=ax, square=True, cbar=False,
                     annot_kws={"size": 18}, lw=4)
    ax.tick_params(labelsize=15)
    ax.set_yticklabels(zone, rotation=40, ha='right')

    filename = '.\Images\%s_%s_corr.png' % ("-".join(zone), type)
    plt.savefig(filename, bbox_inches = 'tight', pad_inches = 0)

    plt.show()

    return PG_zone
