from postreise.extract import const

import numpy as np
import pandas as pd
import time
import os

import matlab.engine
eng = matlab.engine.start_matlab()
this_dirname = os.path.dirname(__file__)
eng.addpath(this_dirname)


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
    """

    start_index = int(scenario_info['start_index']) + 1
    end_index = int(scenario_info['end_index']) + 1

    start = time.process_time()
    for i in range(start_index, end_index+1):
        print('Reading'+str(i))
        output_dir = os.path.join(const.EXECUTE_DIR,
                                  'scenario_%s/output' % scenario_info['id'])
        filename = scenario_info['id'] + '_sub_result_' + str(i)

        matlab_pg = eng.get_power_output_from_gen(os.path.join(output_dir,
                                                               filename))
        matlab_pf = eng.get_load_on_branch(os.path.join(output_dir,
                                                        filename))
        if i > start_index:
            pg = pg.append(pd.DataFrame(np.array(matlab_pg._data).reshape(
                matlab_pg.size[::-1])))
            pf = pf.append(pd.DataFrame(np.array(matlab_pf._data).reshape(
                matlab_pf.size[::-1])))
        else:
            pg = pd.DataFrame(np.array(matlab_pg._data).reshape(
                matlab_pg.size[::-1]))
            pg.name = scenario_info['id'] + '_PG'
            pf = pd.DataFrame(np.array(matlab_pf._data).reshape(
                matlab_pf.size[::-1]))
            pf.name = scenario_info['id'] + '_PF'
    end = time.process_time()
    print('Reading time ' + str(100 * (end-start)) + 's')

    # Set data range
    date_range = pd.date_range(scenario_info['start_date'],
                               scenario_info['end_date'],
                               freq='H')

    pf.index = date_range
    pf.index.name = 'UTC'
    pg.index = date_range
    pg.index.name = 'UTC'

    # Shift index of PG becasue bus index in matlab
    pg = pg.rename(columns=lambda x: x+1)

    return (pg, pf)

def extract_scenario(scenario_id):
    """Extracts data and save data as csv.

    :param str scenario_id: scenario id.
    """

    scenario_info = get_scenario(scenario_id)

    (pg, pf) = extract_data(scenario_info)

    pg.to_csv(os.path.join(const.OUTPUT_DIR, scenario_info['id']+'_PG.csv'))
    pf.to_csv(os.path.join(const.OUTPUT_DIR, scenario_info['id']+'_PF.csv'))

    # Update status in ExecuteList.csv
    insert_in_file(const.EXECUTE_LIST, scenario_info['id'], '2', 'extracted')


if __name__ == "__main__":
    import sys
    extract_scenario(sys.argv[1])
