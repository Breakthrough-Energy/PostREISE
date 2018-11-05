This package contains the following modules:
  * extract
  * process
  * analyze
  * plot

## extract
This module reads from the cases database to get information about the location
of the data and the data range of the data.
It extracts the data from the MATLAB results.
It saves the data as csv files.
## process
### Transfer Data
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
## analyze 
Reads the data from the database and performs the analyze of the data.
It first performs validation(Data within range, correct type, ...)  and verification(Compare data with input data of case from preprocessing ) of the data.
## plot
This module reads the data from the analyze process and plots the output.
This module could be combined with the analyze step.

## Setup/Install
This package requires Matlab.
### For Matlab the following setup is required:
On Windows systems —
'''
cd "matlabroot\extern\engines\python"
python setup.py install
'''
On Mac or Linux systems —
'''
cd "matlabroot/extern/engines/python"
python setup.py install
'''
### Install this package
In the folder with the setup.py file type:
`pip3 install .`
