import westernintnet
WI = westernintnet.WesternIntNet()
import matplotlib.pyplot as plt

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

    ax = agg_df.loc[from_index : to_index,list(type2label.keys())].rename(columns=type2label).plot.area(color = [WI.type2color[type] for type in type2label.keys()],fontsize=18,alpha = 0.7,figsize=(18, 12))
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
    #ax.set_xlabel('Week in Mai',fontsize=16)
    ax.set_xticklabels([])
    plt.title(load_zone)
    plt.show()
    print(agg_df)
