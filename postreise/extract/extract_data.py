from postreise.extract import const

import glob
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
    infeasibilities = []
    cost = []
    setup_time = []
    solve_time = []
    optimize_time = []

    extraction_vars = ['pf', 'pg', 'lmp', 'congu', 'congl']
    temps = {}
    outputs = {}

    folder = os.path.join(const.EXECUTE_DIR,
                          'scenario_%s' % scenario_info['id'])
    end_index = len(glob.glob(os.path.join(folder, 'output', 'result_*.mat')))

    tic = time.process_time()
    for i in tqdm(range(end_index)):
        filename = 'result_' + str(i)

        output = loadmat(os.path.join(folder, 'output', filename),
                         squeeze_me=True, struct_as_record=False)
        try:
            cost.append(output['mdo_save'].results.f)
            setup_time.append(output['mdo_save'].results.SetupTime)
            solve_time.append(output['mdo_save'].results.SolveTime)
            optimize_time.append(output['mdo_save'].results.OptimizerTime)
        except AttributeError:
            pass

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
            if i == 0:
                extraction_vars.append('pf_dcline')
        except AttributeError:
            pass
        for v in extraction_vars:
            if i > 0:
                outputs[v] = outputs[v].append(pd.DataFrame(temps[v]))
            else:
                outputs[v] = pd.DataFrame(temps[v])
                outputs[v].name = scenario_info['id'] + '_' + v.upper()
    toc = time.process_time()
    print('Reading time ' + str(round(toc-tic)) + 's')

    # Write infeasibilities
    insert_in_file(const.SCENARIO_LIST, scenario_info['id'], '15',
                   '_'.join(infeasibilities))

    # Write log
    log = pd.DataFrame(data={'cost': cost, 'setup': setup_time,
                             'solve': solve_time,
                             'optimize': optimize_time})
    log.to_csv(os.path.join(const.OUTPUT_DIR, scenario_info['id']+'_log.csv'),
               header=True)

    # Set index of data frame
    date_range = pd.date_range(scenario_info['start_date'],
                               scenario_info['end_date'],
                               freq='H')
    
    for v in extraction_vars:
        outputs[v].index = date_range
        outputs[v].index.name = 'UTC'

    # Set index column name of data frame
    case = loadmat(os.path.join(folder, 'case.mat'), squeeze_me=True,
                   struct_as_record=False)

    outputs_id = {'pg': case['mpc'].genid,
                  'pf': case['mpc'].branchid,
                  'lmp': case['mpc'].bus[:, 0].astype(np.int64),
                  'congu': case['mpc'].branchid,
                  'congl': case['mpc'].branchid}
    try:
        outputs_id['pf_dcline'] = case['mpc'].dclineid
    except AttributeError:
        pass

    for k, v in outputs_id.items():
        if isinstance(v, int):
            outputs[k].columns = [v]
        else:
            outputs[k].columns = v.tolist()

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

    # Update status
    insert_in_file(const.EXECUTE_LIST, scenario_info['id'], '2', 'extracted')
    insert_in_file(const.SCENARIO_LIST, scenario_info['id'], '4', 'analyze')


if __name__ == "__main__":
    import sys
    extract_scenario(sys.argv[1])
