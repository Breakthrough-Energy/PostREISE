import pandas as pd
import numpy as np
from math import *
import os

import sys
sys.path.append("..")

import westernintnet
WI = westernintnet.WesternIntNet()

def generate_congestion_stats(congestion_data,name):
    '''
    Generates congestion statistics from the input congestion data.
    
    Parameters: 
    congestion_data :  Power flow dataframe, values normalized to Capacity
    name : filename of output

    Returns:
    Dataframe with 
    hutil1 : number of hours a line has power flow = Capacity
    hutil0p9-1 : number of hours a line has power flow between 90 to 100% Capacity
    hutil0p8-0p9 : number of hours a line has power flow between 80 to 90% Capacity
    hutil0p75-0p8 : number of hours a line has power flow between 75 to 80% Capacity
    hutil>=0p9 : number of hours a line has power flow >= 90% Capacity
    hutil>=0p8 : number of hours a line has power flow >= 80% Capacitybetween 80 to 90% Capacity
    hutil>=0p75 : number of hours a line has power flow >= 75% Capacity between 80 to 90% Capacity
    dist : distance (km) between substations 
    zscore : (hutil>=0p75 - mu)/std
            mu : population mean of hutil>=0p75, derived by assuming all the hourly line readings form the population
            std : standard deviation of hutil>=0p75 distribution
    pvalue : measure of confidence in congestion call, assuming normal distribution
    
    Todo:
    Generalize pvalue calculation to non-Gaussian distribution
    
    '''
    import numpy as np
    import scipy.special as scsp
    import math
    
    congestion_stats = pd.concat([WI.branches['Capacity'],                                                            
                    congestion_data[(congestion_data==1)].describe().loc['count',:],                             
                    congestion_data[(congestion_data<1) & (congestion_data>=0.9)].describe().loc['count',:],      
                    congestion_data[(congestion_data<0.9) & (congestion_data>=0.8) ].describe().loc['count',:],
                    congestion_data[(congestion_data<0.8) & (congestion_data>=0.75) ].describe().loc['count',:]
                   ],axis=1)                                                                                   
    congestion_stats.columns = ['Capacity','hutil1','hutil0p9-1','hutil0p8-0p9','hutil0p75-0p8']                                       

    congestion_stats[['Capacity',                                                                                      
              'hutil1',                                                                                        
              'hutil0p9-1',                                                                                    
              'hutil0p8-0p9',
              'hutil0p75-0p8'
             ]] = congestion_stats[['Capacity','hutil1','hutil0p9-1','hutil0p8-0p9','hutil0p75-0p8']].astype(int)                       

    congestion_stats.index.name = 'line'                                                                               
    congestion_stats = pd.concat([congestion_stats,                                                                            
                    congestion_stats[['hutil1','hutil0p9-1']].sum(axis=1),                                             
                    congestion_stats[['hutil1','hutil0p9-1','hutil0p8-0p9']].sum(axis=1), 
                    congestion_stats[['hutil1','hutil0p9-1','hutil0p8-0p9','hutil0p75-0p8']].sum(axis=1)
                   ],axis=1).rename(columns={0:'hutil>=0p9',1:'hutil>=0p8',2:'hutil>=0p75'})                                   

    WI.branches['dist'] = WI.branches\
                            .apply(lambda row : haversine([row['from_lat'],row['from_lon']],
                                                       [row['to_lat'], row['to_lon']]), axis=1)
    
    congestion_stats = pd.concat([congestion_stats, WI.branches['dist']], axis=1)
    
    totalHours = len(congestion_data)
    p_cong = congestion_stats.loc[congestion_stats['Capacity'] != 99999]\
                             .describe()\
                             .loc['mean']['hutil>=0p75']/totalHours  
    mu = 8784*p_cong
    var = 8784*p_cong*(1-p_cong)
    congestion_stats['zscore'] = (congestion_stats['hutil>=0p75'] - mu)/math.sqrt(var)
    congestion_stats['pvalue'] = congestion_stats['zscore'].apply(lambda x: 1-scsp.ndtr(x))

    congestion_stats.to_csv(name + '.csv')  
    
    return congestion_stats   


def haversine(coord1: object, coord2: object):
    '''
    Calculate great circle distance between 2 points

    Parameters:
    coord1 : latitude and longitude in decimal degrees of point 1
    coord2 : latitude and longitude in decimal degrees of point 2

    Return:
    distance in kilometers
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

    a = math.sin(delta_phi/2.0)**2 + math.cos(phi_1)*math.cos(phi_2)*math.sin(delta_lambda/2.0)**2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    meters = R*c  # output distance in meters
    km = meters/1000.0  # output distance in kilometers

    meters = round(meters, 3)
    km = round(km, 3)

    return km

