# PostREISE
This package is dedicated to the analysis and plotting of the output data. It also handles the extraction of the data and its transfer from the server to the local machine.

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
The aim of the `postreise.extract.extract_data` module is three fold:
* locate the outputs of the simulation;
* extract the results from the MATLAB files and;
* save the data in csv files.



## 3. Transfer Data
Simulation output data are located on the server. These can be easily transferred to your local machine using the `postreise.procees.transferdata` module.

First, create a `OutputData` instance. Note that the path to the local folder where the data will be stored can be specified. If no location is specified the data will be stored in a *scenario_data* folder in home.

Then, call the `get_data` method with the scenario name along with the type of data (PG or PF) as arguments. The call to the function is illustrated below:
```python
from postreise.process.transferdata import OutputData
od = OutputData()
PGtest = od.get_data('western_scenarioUnitTest02', 'PG')
PFtest = od.get_data('western_scenarioUnitTest02', 'PF')
```


## 4. Analyze
The `postreise.analyze` module encloses the congestion analysis.

### A. Transmission Congestion Analysis
To carry out transmission congestion analyses per scenario:
1. download the power flow output;
2. calculate congestion statistics;
3. display the data.

The notebook [transmission_analysis_demo.ipynb](https://github.com/intvenlab/PostREISE/tree/mlh/postreise/analyze/demo/transmission_analysis_demo.ipynb) notebook shows the steps for downloading and calculation of various statistics. The notebook [WECC_Congestion_interactive_map.ipynb](https://github.com/intvenlab/PostREISE/tree/mlh/postreise/analyze/demo/WECC_Congestion_interactive_map.ipynb) notebook shows how the output of the transmission_analyses notebook is used to display the congested transmission lines. (Note that since the plot outputs are meant to be interactive, they may not render on GitHub. A sample static shot can be found [here](https://github.com/intvenlab/PostREISE/tree/mlh/postreise/analyze/demo/sampleTransmissionCongestion.PNG).)


## 5. Plot
This module reads the data from the analyze process and plots the output. Note that this module could be combined with the analyze step.
