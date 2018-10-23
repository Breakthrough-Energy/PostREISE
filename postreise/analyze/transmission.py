import os
import sys
from math import *

import numpy as np
import pandas as pd

sys.path.append("..")


def generate_cong_stats(cong_df, branches_df, name):
    '''
    Generates congestion statistics from the input congestion data.
    :param dataframe cong_df: Power flow dataframe, \ 
    values normalized to Capacity
    :param string name: filename of output
    :return: pandas dataframe with columns = ['hutil1','hutil0p9-1', \ 
                                              'hutil0p8-0p9','hutil0p75-0p8', \ 
                                              'hutil>=0p9','hutil>=0p8', \ 
                                              'hutil>=0p75', \ 
                                              'dist','zscore','pvalue']
    '''
    import numpy as np
    import scipy.special as scsp
    import math

    cong_stats = pd.concat([branches_df['Capacity'],
                            cong_df[(cong_df == 1)].describe().loc['count', :],
                            cong_df[(cong_df < 1) & (cong_df >= 0.9)
                                    ].describe().loc['count', :],
                            cong_df[(cong_df < 0.9) & (cong_df >= 0.8)
                                    ].describe().loc['count', :],
                            cong_df[(cong_df < 0.8) & (cong_df >= 0.75)
                                    ].describe().loc['count', :]
                            ], axis=1)
    cong_stats.columns = ['Capacity', 'hutil1', 'hutil0p9-1',
                          'hutil0p8-0p9', 'hutil0p75-0p8']

    cong_stats[['Capacity',
                'hutil1',
                'hutil0p9-1',
                'hutil0p8-0p9',
                'hutil0p75-0p8'
                ]] = cong_stats[['Capacity', 'hutil1',
                                 'hutil0p9-1', 'hutil0p8-0p9',
                                 'hutil0p75-0p8']].astype(int)

    cong_stats.index.name = 'line'
    cong_stats = pd.concat([cong_stats,
                            cong_stats[['hutil1', 'hutil0p9-1']].sum(axis=1),
                            cong_stats[['hutil1', 'hutil0p9-1',
                                        'hutil0p8-0p9']].sum(axis=1),
                            cong_stats[['hutil1', 'hutil0p9-1',
                                        'hutil0p8-0p9',
                                        'hutil0p75-0p8']].sum(axis=1)
                            ], axis=1).rename(columns={0: 'hutil>=0p9',
                                                       1: 'hutil>=0p8',
                                                       2: 'hutil>=0p75'})

    branches_df['dist'] = branches_df\
                            .apply(lambda row: haversine([row['from_lat'],
                                                          row['from_lon']],
                                                         [row['to_lat'],
                                                          row['to_lon']]),
                                   axis=1)

    cong_stats = pd.concat([cong_stats, branches_df['dist']], axis=1)

    total_hours = len(cong_df)
    p_cong = cong_stats.loc[cong_stats['Capacity'] != 99999]\
        .describe()\
        .loc['mean']['hutil>=0p75']/total_hours
    mu = total_hours*p_cong
    var = total_hours*p_cong*(1 - p_cong)
    cong_stats['zscore'] = (cong_stats['hutil>=0p75'] - mu)/math.sqrt(var)
    cong_stats['pvalue'] = cong_stats['zscore'].apply(lambda x: 1-scsp.ndtr(x))

    cong_stats.to_csv(name + '.csv')

    return cong_stats


def haversine(coord1: object, coord2: object):
    '''
    Calculate great circle distance between 2 points

    :param coord1: latitude and longitude in decimal degrees of point 1
    :param coord2: latitude and longitude in decimal degrees of point 2
    :return: distance in kilometers

    '''

    import math

    # Coordinates in decimal degrees (e.g. 2.89078, 12.79797)
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    R = 6371000  # radius of Earth in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)

    delta_phi = math.radians(lat2-lat1)
    delta_lambda = math.radians(lon2-lon1)

    a = (math.sin(delta_phi/2.0)**2
         + math.cos(phi_1)*math.cos(phi_2)*math.sin(delta_lambda/2.0)**2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    meters = R*c  # output distance in meters
    km = meters/1000.0  # output distance in kilometers

    meters = round(meters, 3)
    km = round(km, 3)

    return km
