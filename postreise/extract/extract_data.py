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

    :param str scenario_id: scenario index.
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
    """Builds data frames of {PG, PF, LMP, CONGU, CONGL}
        from MATLAB simulation output binary files produced by MATPOWER.

    :param dict scenario_info: scenario information.
    :return: (*pandas.DataFrame*) -- data frames of: PG, PF, LMP, CONGU, CONGL.
    """

    interval = int(scenario_info['interval'].split('H', 1)[0])
    start_date = scenario_info['start_date']
    end_date = scenario_info['end_date']
    diff = pd.Timestamp(end_date) - pd.Timestamp(start_date)
    hours = diff / np.timedelta64(1, 'h') + 1

    start_index = 0
    end_index = int(hours / interval)

    infeasibilities = []
    
    extraction_vars = ['pf', 'pg', 'lmp', 'congu', 'congl']
    temps = {}
    outputs = {}

    tic = time.process_time()
    folder = os.path.join(const.EXECUTE_DIR,
                          'scenario_%s' % scenario_info['id'])
    for i in tqdm(range(start_index, end_index)):
        filename = 'result_' + str(i)

        output = loadmat(os.path.join(folder, 'output', filename),
                         squeeze_me=True, struct_as_record=False)

        demand_scaling = output['mdo_save'].demand_scaling
        if demand_scaling < 1:
            demand_change = round(100 * (1 - demand_scaling))
            infeasibilities.append('%s:%s' % (str(i), str(demand_change)))
        temps['pg'] = output['mdo_save'].flow.mpc.gen.PG.T
        temps['pf'] = output['mdo_save'].flow.mpc.branch.PF.T
        temps['lmp'] = output['mdo_save'].flow.mpc.bus.LAM_P.T
        temps['congu'] = output['mdo_save'].flow.mpc.branch.MU_SF.T
        temps['congl'] = output['mdo_save'].flow.mpc.branch.MU_ST.T
        try:
            temps['pf_dcline'] = output['mdo_save'].flow.mpc.dcline.PF_dcline.T
            extraction_vars.append('pf_dcline')
        except AttributeError:
            pass
        for v in extraction_vars:
            if i > start_index:
                outputs[v] = outputs[v].append(pd.DataFrame(temps[v]))
            else:
                outputs[v] = pd.DataFrame(temps[v])
                outputs[v].name = scenario_info['id'] + '_' + v.upper()
    toc = time.process_time()
    print('Reading time ' + str(round(toc-tic)) + 's')

    # Add infeasibilities in ScenarioList.csv
    insert_in_file(const.SCENARIO_LIST, scenario_info['id'], '15',
                   '_'.join(infeasibilities))

    # Set data range
    date_range = pd.date_range(start_date, end_date, freq='H')
    
    for v in extraction_vars:
        outputs[v].index = date_range
        outputs[v].index.name = 'UTC'

    case = loadmat(os.path.join(folder, 'case.mat'), squeeze_me=True,
                   struct_as_record=False)
    outputs['pg'].columns = case['mpc'].genid.tolist()
    outputs['pf'].columns = case['mpc'].branchid.tolist()
    outputs['lmp'].columns = case['mpc'].bus[:,0].astype(np.int64).tolist()
    outputs['congu'].columns = case['mpc'].branchid.tolist()
    outputs['congl'].columns = case['mpc'].branchid.tolist()
    try:
        outputs['pf_dcline'].columns = case['mpc'].dclineid.tolist()
    except AttributeError:
        pass

    return outputs


def extract_scenario(scenario_id):
    """Extracts data and save data as csv.

    :param str scenario_id: scenario id.
    """

    scenario_info = get_scenario(scenario_id)

    outputs = extract_data(scenario_info)
    
    for k, v in outputs.items():
        v.to_pickle(os.path.join(
            const.OUTPUT_DIR, scenario_info['id']+'_'+k.upper()+'.pkl'))

    # Update status in ExecuteList.csv
    insert_in_file(const.EXECUTE_LIST, scenario_info['id'], '2', 'extracted')

    # Update status in ScenarioList.csv
    insert_in_file(const.SCENARIO_LIST, scenario_info['id'], '4', 'analyze')


if __name__ == "__main__":
    import sys
    extract_scenario(sys.argv[1])
