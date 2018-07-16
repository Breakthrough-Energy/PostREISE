import numpy as np
import pandas as pd
import time

import matlab.engine
eng = matlab.engine.start_matlab()


def extract_data(case_name, data_location, start_index, end_index):
    """Takes subintervals from simulation in matlab
    binary formate, converts and connects it into csv format.
    It uses the matlab functions get_power_output_from_gen
    and get_load_on_branch to extract data.

    WARNING:
    date_range is hard coded

    """

    start = time.process_time()
    for i in range(start_index, end_index+1):
        print('Reading'+str(i))
        filename = case_name + '_sub_result_' + str(i)
        # Call matlab functions
        matlab_pg = eng.get_power_output_from_gen(data_location + filename)
        matlab_pf = eng.get_load_on_branch(data_location + filename)
        if i > start_index:
            pg = pg.append(pd.DataFrame(np.array(matlab_pg._data).reshape(
                matlab_pg.size[::-1])))
            pf = pf.append(pd.DataFrame(np.array(matlab_pf._data).reshape(
                matlab_pf.size[::-1])))
        else:
            pg = pd.DataFrame(np.array(matlab_pg._data).reshape(
                matlab_pg.size[::-1]))
            pg.name = case_name + 'PG'
            pf = pd.DataFrame(np.array(matlabpf._data).reshape(
                matlab_pf.size[::-1]))
            pf.name = case_name + 'PF'
    end = time.process_time()
    print('Reading time ' + str(100 * (end-start)) + 's')

    # Set data range
    date_start = pd.Timestamp('2010-01-01')
    date_end = pd.Timestamp('2012-12-31 23:00:00')
    date_range = pd.date_range(date_start, date_end, freq='H')

    pf.index = date_range[(start_index-1)*4*24:(end_index)*4*24]
    pg.index = date_range[(start_index-1)*4*24:(end_index)*4*24]

    # Shift index of PG becasue bus index in matlab
    pg = pg.rename(columns=lambda x: x+1)

    return (pg, pf)


def extract_data_and_save(case_name, data_location, save_location,
                          start_index, end_index):
    """Extract data and save as csv in locSave locaton."""

    (pg, pf) = extract_data(case_name, data_location, start_index, end_index)

    pg.to_csv(save_location+case_name+'PG.csv')
    pf.to_csv(save_location+case_name+'PF.csv')


if __name__ == "__main__":
    import sys
    extract_data_and_save(sys.argv[1], sys.argv[2], sys.argv[3], int(
        sys.argv[4]), int(sys.argv[5]))
