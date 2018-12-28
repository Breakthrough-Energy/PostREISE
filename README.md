# PostREISE
---

## 1. Setup/Install
This package requires MATLAB and WesternInterconnectNetwork.

### A. MATLAB
Install MATLAB and proceed as follows
```
cd "matlabroot\extern\engines\python"
python setup.py install
```
for Windows system.
```
cd "matlabroot/extern/engines/python"
python setup.py install
```
for Mac or Linux systems.


### B. WesternInterconnectNetwork
In the WesternInterconnect package, locate the ***setup.py*** file and type: `pip3 install .` Do not forget to update your PYTHONPATH environment variable.


### C. PostREISE
In the PostREISE package, locate the ***setup.py*** file and type: `pip3 install .` Do not forget to update your PYTHONPATH environment variable.



## 2. Extract Data
The aim of the extract module is three fold: it locates the outputs of the simulation; it  extracts the results from the MATLAB files and it saves these data in csv files.



## 3. Transfer Data
Simulation output data are located on the server and hence need to be transferred for analysis. The process module will download the data from the server to a local folder on your computer.

First, a `OutputData` instance needs to be created. The path to the local folder where the data will be stored can be specified. If no location is specified the data will be stored in a *scenario_data* folder in home.

Then, the `get_data` method can be called. The scenario name along with the type of data (PG or PF) must be specified. The call to the function is illustrated below.
```python
from postreise.process.transferdata import OutputData
od = OutputData()
PGtest = od.get_data('western_scenarioUnitTest02','PG')
PFtest = od.get_data('western_scenarioUnitTest02','PF')
```


## analyze
Reads the data from the database and performs the analyze of the data. It first performs validation (data within range, correct type, ...) and verification (compare data with input data of case from preprocessing) of the data.

## plot
This module reads the data from the analyze process and plots the output. This module could be combined with the analyze step.
