import numpy as np
import pandas as pd
import time

import matlab.engine
eng = matlab.engine.start_matlab()


def extractData(caseName, locRead, nStart, nEnd):
    """Takes subintervals from simulation in matlab
    binary formate, converts and connects it into csv format.
    It uses the matlab functions get_power_output_from_gen
    and get_load_on_branch to extract data.
    
    WARNING:
    dataRange is hard coded

    """
    
    start = time.process_time()
    for i in range(nStart, nEnd+1):
        print('Reading'+str(i))
        filename = '/sub_result_' + str(i)
        # Call matlab functions
        matlabPG = eng.get_power_output_from_gen(locRead + filename)
        matlabPF = eng.get_load_on_branch(locRead + filename)
        if i > nStart:
            PG = PG.append(pd.DataFrame(np.array(matlabPG._data).reshape(
                matlabPG.size[::-1])))
            PF = PF.append(pd.DataFrame(np.array(matlabPF._data).reshape(
                matlabPF.size[::-1])))
        else:
            PG = pd.DataFrame(np.array(matlabPG._data).reshape(
                matlabPG.size[::-1]))
            PG.name = caseName + 'PG'
            PF = pd.DataFrame(np.array(matlabPF._data).reshape(
                matlabPF.size[::-1]))
            PF.name = caseName + 'PF'
    end = time.process_time()
    print('Reading time ' + str(100 * (end-start)) + 's')    

    # Set data range
    dataStart = pd.Timestamp('2010-01-01')
    dataEnd = pd.Timestamp('2012-12-31 23:00:00')
    dataRange = pd.dateRange(dataStart, dataEnd, freq='H')

    PF.index = dataRange[nStart-1:nEnd-1]
    PG.index = dataRange[nStart-1:nEnd-1]

    # Shift index of PG becasue bus index in matlab
    PG = PG.rename(columns=lambda x: x+1)

    return (PG, PF)


def extractDataAndSave(caseName, locRead, locSave, nStart, nEnd):
    """Extract data and save as csv in locSave locaton."""
    
    (PG, PF) = extractData(caseName, locRead, nStart, nEnd)
    
    PG.to_csv(locSave+caseName+'PG.csv')
    PF.to_csv(locSave+caseName+'PF.csv')


if __name__ == "__main__":
    import sys
    extractDataAndSave(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
