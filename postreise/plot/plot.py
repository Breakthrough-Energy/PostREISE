import westernintnet
WI = westernintnet.WesternIntNet()
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import seaborn as sns
import pytz
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import numpy as np
import pandas as pd
import sys

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
    """Calculates time difference between utc and local time for a given location.

    Arguments:
        year: year of the timestamp.
        month: month of the timestamp.
        day: day of the timestamp.
        hour: hour of the timestamp.
        minute: minute of the timestamp.
        sec: second of the timestamp.
        lon: longitude of the site (in deg.) measured eastward from Greenwich.
        lat: latitude of the site (in deg.). Equator is the zero point.

    Returns:
        Offset (in hours) between UTC and local time.
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



def to_PST(TS, columns, from_index, to_index):
    """Converts a time series from UTC to PST (Pacific Standard Time). Eventual daylight
    saving are taken into account.

    Arguments:
        TS: pandas time series with UTC-timestamp indexing.
        columns: columns to consider in the data frame.
        from_index: starting timestamp.
        to_index: ending timestamp.

    Returns:
        Power generated time series of the selected columns with PST-timestamp indexing.
    """
    TS_PST = TS[columns]
    TS_PST.set_index(pd.to_datetime(TS_PST.index) - timedelta(hours=8), inplace=True)
    TS_PST.index.name = 'PST'

    return TS_PST[from_index:to_index]



def to_LT(PG, plantID, from_index, to_index):
    """Converts a power generated time series from UTC to LT (local time). Eventual daylight
    saving are taken into account.

    Arguments:
        PG: pandas time series of the power generated with UTC-timestamp indexing.
        plantID: plantID to consider in the data frame.
        from_index: starting timestamp.
        to_index: ending timestamp.

    Returns:
        Power generated time series of the selected plantID with LT-timestamp indexing.
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

    Arguments:
        zone: one of the zone defined as keys in the <zone2style> dictionary.

    Returns:
        plantID in a given zone.
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
    """demand profile for a given zone.

    Arguments:
        demand: demand profiles for all 16 load zones.
        zone: one of the zone defined as keys in the <zone2style> dictionary.

    Returns:
        time series of the demand for a given zone.
    """
    if zone == 'total':
        return demand.sum(axis=1)
    elif zone == 'California':
        return demand.loc[:,California].sum(axis=1)
    else:
        return demand.loc[:,zone]



def IsRenewableResource(type):
    """Is resource renewable.

    Arguments:
        type: either <nuclear>, <hydro>, <coal>, <ng>, <solar> or <wind>.
    """
    if type != 'solar' and type != 'wind':
        print('Possible <type> are <solar> and <wind>')
        return



def ts_all_onezone(PG, zone, from_index='2016-01-01-00', to_index='2017-01-01-00', freq='W'):
    """Plots the time series stack plot for load zone, California or total for western
    interconnect including demand. It also prints the generation for each type.

    Arguments:
        PG: pandas time series of the power generated with UTC-timestamp indexing.
        zone: one of the zone defined as keys in the <zone2style> dictionary.

    Options:
        from_index: starting timestamp.
        to_index: ending timestamp.
        freq: frequency for resampling.

    Returns:
        Power generated time series for every available resource in the load zone.
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



def ts_renewable_onezone(PG, type, zone,
                         from_index='2016-01-01-00', to_index='2017-01-01-00', freq='W',
                         LT=True, seed=0):
    """Plots the time series of the power generated by solar or wind plants in a given
    load zone, California or total western interconnect. Also show on the same plot the time
    series of power generated by 2, 8 and 15 randomly chosen plants in the load zone.

    Arguments:
        PG: pandas time series of the power generated with UTC-timestamp indexing.
        type: can be 'solar' or 'wind'.
        zone: one of the zone defined as keys in the <zone2style> dictionary.

    Options:
        from_index: starting timestamp.
        to_index: ending timestamp.
        freq: frequency for resampling.
        LT: apply the to_LT method to PG. If False the to_PST method is applied instead.
        seed: seed for the random selection of plants.

    Returns:
        Power generated time series for the chosen renewable resource in the load zone and the
        selected plants in the load zone.
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


def ts_renewable_comp(PG, type, zone_list,
                      from_index='2016-01-01-00', to_index='2016-12-31-00', freq='W',
                      normalize=False):
    """Plots the time series of the power generated by solar or wind plants in various
    load zones. PST is chosen as a common timezone.

    Arguments:
        PG: pandas time series of the power generated with UTC-timestamp indexing.
        type: Can be 'solar' or 'wind'.
        zone: list of zone. Zones are defined as keys in the <zone2style> dictionary.

    Options:
        from_index: starting timestamp.
        to_index: ending timestamp.
        freq: frequency for resampling.
        normalize: if True, the total capacity (in MWh) of the renewable resource in each
                   load zone is used to derive a normalized power generated.

    Returns:
        Power generated time series for the chosen renewable resource in the selected load zones.
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
    """Plots the time series of the curtailment for solar or wind plants in a given
    load zone, California or total western interconnect. Also show on the same plot
    the time series of the associated power output of the farms and the demand for
    the load zone.

    Arguments:
        PG: pandas time series of the power generated with UTC-timestamp indexing.
        type: either <solar> or <wind>.
        zone: one of the zone defined as keys in the <zone2style> dictionary.

    Options:
        from_index: starting timestamp.
        to_index: ending timestamp.
        freq: frequency for resampling.
        multiplier: multiplier for renewable power output.

    Returns:
        Curtailment time series for the chosen renewable resource in the load zone.
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
    """Plots the power generated by wind farms and solar plants in a given zone with respect to
       the total power generated in that zone for various scenarios.

    Arguments:
        zone: either <total> or <California>.
    """
    if zone == 'total':
        scenarios = scenarios_total
    elif zone == 'California':
        scenarios = scenarios_California
    else:
        print('Only <total> and <California> are available')
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
    """Plots the stacked power generated for a given zone for various scenarios.

    Arguments:
        zone: either <total> or <California>.

    Returns:
        Allotment of power generated per resource type.
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
    """Plots the stacked power generated for given load zones per increased renewable
       energy on a specified grid.

    Arguments:
        zone_ref: California
        zone_tostudy: one of the zone defined as keys in the zone2style dictionary

    Returns:
        List of stacked power generated in multiple zones for various increased renewable
        energy scenarios.
    """
    if zone_ref == 'California':
        scenarios = scenarios_California
    else:
        print('Only <California> is available')
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
    """Plots the correlation between power generated in given load zone and for wind or solar

    Arguments:
        PG: pandas time series of the power generated with UTC-timestamp indexing.
        type: either <wind> or <solar>
        zone: one of the zone defined as keys in the <zone2style> dictionary.

    Returns:
        Power generated time series for the specified energy type and load zones.
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
