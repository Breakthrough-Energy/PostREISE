# PostREISE
---

This package contains the following modules:
  * extract
  * process
  * analyze
  * plot
  
It requires the Matlab simulation engine.

## 1. Setup/Install
```
cd "matlabroot\extern\engines\python"
python setup.py install
```

## 2. Extracting Data
This module reads from the cases database to get information about the location and range of the data. It extracts the data from the MATLAB results and saves the data as csv files. This module runs only on the server for now.

To extract results from the MATLAB results after a simulation you can run:
```python
from postreise.extract import extract_data
extract_data.extract_scenario('western_scenarioUnitTest02')
```
To run a test:
```python
from postreise.extract.test import test_extract
test_extract.test()
```

## 3. Transfer Data
This module is used to handle the simulation output data. 
The simulation output data is located on the server.
To work more efficiently this module will download the data from the server
to a local folder.

First, create a OutputData instance. You can pass a local address, where you
want to store the data. If no location is specifies the data will be stored in
your home directory in the *scenario_data* folder.

Second, call the get_data method, where you specify which data from which 
scenario you want to get the data. Here is an example:
```python
from postreise.process.transferdata import OutputData
od = OutputData()
PGtest = od.get_data('western_scenarioUnitTest02','PG')
PFtest = od.get_data('western_scenarioUnitTest02','PF')
``` 

## 4. Analyzing data 
Reads the data from the database and performs the data analysis. It first performs validation (data within range, correct type, ...) and verification (compare data with input data of case from preprocessing) of the data.

### Transmission Congestion Analysis
To carry out transmission congestion analyses per scenario, (1) download the power flow output; (2) calculate congestion statistics; (3) display the data. The notebook postreise/analyze/demo/transmission_analysis_demo.ipynb shows the steps for downloading and calculation of various statistics. The notebook postreise/analyze/demo/WECC_Congestion_interactive_map.ipynb shows how the output of the transmission_analyses notebook is used to display the congested transmission lines. (Note that since the plot outputs are meant to be interactive, they may not render on github. A sample static shot is in demo/sampleTransmissionCongestion.png.)


## 5. Plot
This module reads the data from the analyze process and plots the output. Note that this module could be combined with the analyze step.
