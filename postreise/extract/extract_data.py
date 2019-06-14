from postreise.extract import const

import numpy as np
import pandas as pd
import time
import os

from scipy.io import loadmat
from tqdm import tqdm
from collections import OrderedDict


def get_scenario(scenario_id):
    """Returns scenario information.

    :param int scenario_id: scenario index.
    :return: (*dict*) -- scenario information.
    """
    scenario_list = pd.read_csv(const.SCENARIO_LIST, dtype=str)
    scenario_list.fillna('', inplace=True)
    scenario = scenario_list[scenario_list.id == scenario_id]

    return scenario.to_dict('records', into=OrderedDict)[0]

def insert_in_file(filename, scenario_id, column_number, column_value):
    """Updates status in execute list on server.

    :param str filename: path to execute or scenario list.
    :param str scenario_id: scenario index.
    :param str column_number: id of column (indexing starts at 1).
    :param str column_value: value to insert.
    """
    options = "-F, -v OFS=',' -v INPLACE_SUFFIX=.bak -i inplace"
    program = ("'{for(i=1; i<=NF; i++){if($1==%s) $%s=\"%s\"}};1'" %
               (scenario_id, column_number, column_value))
    command = "awk %s %s %s" % (options, program, filename)
    os.system(command)

def extract_data(scenario_info):
    """Takes subintervals from simulation in MATLAB binary formats, \
        converts and connects it into csv format. It uses the MATLAB \
        functions to extract data.

    :param dict scenario_info: scenario information.
    :return: (*pandas*) -- data frame of PG and PF.
    """

    interval = int(scenario_info['interval'].split('H', 1)[0])
    start_date = scenario_info['start_date']
    end_date = scenario_info['end_date']
    diff = pd.Timestamp(end_date) - pd.Timestamp(start_date)
    hours = diff / np.timedelta64(1, 'h') + 1

    start_index = 0
    end_index = int(hours / interval)

    infeasibilities = []

    start = time.process_time()
    for i in tqdm(range(start_index, end_index)):
        dir = os.path.join(const.EXECUTE_DIR,
                           'scenario_%s' % scenario_info['id'])
        filename = 'result_' + str(i)

        struct = loadmat(os.path.join(dir, 'output', filename),
                         squeeze_me=True, struct_as_record=False)

        demand_scaling = struct['mdo_save'].demand_scaling
        if demand_scaling < 1:
            demand_change = round(100 * (1 - demand_scaling))
            infeasibilities.append('%s:%s' % (str(i), str(demand_change)))
        pg_tmp = struct['mdo_save'].flow.mpc.gen.PG.T
        pf_tmp = struct['mdo_save'].flow.mpc.branch.PF.T
        if i > start_index:
            pg = pg.append(pd.DataFrame(pg_tmp))
            pf = pf.append(pd.DataFrame(pf_tmp))
        else:
            pg = pd.DataFrame(pg_tmp)
            pg.name = scenario_info['id'] + '_PG'
            pf = pd.DataFrame(pf_tmp)
            pf.name = scenario_info['id'] + '_PF'
    end = time.process_time()
    print('Reading time ' + str(100 * (end-start)) + 's')

    # Add infeasibilities in ScenarioList.csv
    insert_in_file(const.SCENARIO_LIST, scenario_info['id'], '15',
                   '_'.join(infeasibilities))

    # Set data range
    date_range = pd.date_range(start_date, end_date, freq='H')

    pf.index = date_range
    pf.index.name = 'UTC'
    pg.index = date_range
    pg.index.name = 'UTC'

    # Shift index of PG becasue bus index in matlab
    case = loadmat(os.path.join(dir, 'case.mat'), squeeze_me=True,
                   struct_as_record=False)
    pg.columns = case['mpc'].genid.tolist()
    pf.columns = case['mpc'].branchid.tolist()

    return (pg, pf)

def extract_scenario(scenario_id):
    """Extracts data and save data as csv.

    :param str scenario_id: scenario id.
    """

    scenario_info = get_scenario(scenario_id)

    (pg, pf) = extract_data(scenario_info)

    pg.to_pickle(os.path.join(const.OUTPUT_DIR, scenario_info['id']+'_PG.pkl'))
    pf.to_pickle(os.path.join(const.OUTPUT_DIR, scenario_info['id']+'_PF.pkl'))

    # Update status in ExecuteList.csv
    insert_in_file(const.EXECUTE_LIST, scenario_info['id'], '2', 'extracted')

    # Update status in ScenarioList.csv
    insert_in_file(const.SCENARIO_LIST, scenario_info['id'], '4', 'analyze')

if __name__ == "__main__":
    import sys
    extract_scenario(sys.argv[1])
