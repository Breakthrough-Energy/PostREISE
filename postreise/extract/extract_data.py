import os
import time

import matlab.engine
import numpy as np
import pandas as pd
from pandas.core.indexes.datetimes import date_range

def extract_data(scenario_name, data_location, start_index, end_index):
    """Takes subintervals from simulation in MATLAB binary formats, \ 
        converts and connects it into csv format. It uses the MATLAB \ 
        functions to extract data.

    :param str scenario_name: scenario name.
    :param str data_location: data location.
    :param int start_index: starting index.
    :param int end_index: ending index.
    :return: (*tuple*) -- data frames of power generated (PG) and \ 
      power flow (PF).
    """

    # Start MATLAB engine
    print("Starting MATLAB")
    eng = matlab.engine.start_matlab()
    this_dirname = os.path.dirname(__file__)
    eng.addpath(this_dirname)
    print("Starting extracting data")
    eng.get_all_power_and_load(scenario_name, data_location,
                               int(start_index), int(end_index))
    print("Done extracting data")
    eng.quit()
    print("MATLAB terminated")

    pg = pd.read_csv(
                data_location+scenario_name+'fromMatlabPG.csv',
                header=None
            ).T
    pf = pd.read_csv(
                data_location+scenario_name+'fromMatlabPF.csv',
                header=None
            ).T

    pg.index = date_range
    pf.index = date_range

    return (pg, pf)


def extract_data_and_save(scenario_name, data_location, save_location,
                          start_index, end_index):
    """Extract data and save as csv.
    
    :param str scenario_name: scenario name.
    :param str data location: data location.
    :param str save location: save location.
    :param int start_index: starting index.
    :param int end_index: ending index.
    """

    (pg, pf) = extract_data(scenario_name, data_location, start_index,
                            end_index)

    pg.to_csv(save_location+scenario_name+'PG.csv')
    pf.to_csv(save_location+scenario_name+'PF.csv')


def extract_scenario(scenario_name):
    """Extracts data.
    
    :param str scenario_name: scenario name.
    """

    scenario_dirname = '/home/EGM/'
    scenario_list = pd.read_csv(scenario_dirname + 'ScenarioList.csv')

    # Get parameters related to scenario
    scenario = scenario_list[scenario_list.name == scenario_name]

    # Catch if name not found
    if scenario.shape[0] == 0:
        print('No scenario with name ' + scenario_name)
        return
    if scenario.extract.values[0]:
        print('Scenario already extracted or does not want to be extracted')
        return
    # Set data range
    date_start = pd.Timestamp(scenario.start_date.values[0])
    date_end = pd.Timestamp(scenario.end_date.values[0])
    date_range = pd.date_range(date_start, date_end, freq='H')

    extract_data_and_save(scenario_name,
                          scenario.output_data_location.values[0],
                          scenario.output_data_location.values[0],
                          int(scenario.start_index.values[0]),
                          int(scenario.end_index.values[0]),
                          date_range)


if __name__ == "__main__":
    import sys
    extract_scenario(sys.argv[1])
