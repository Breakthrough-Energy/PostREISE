This package contains the following modules:
  * extract
  * analyze
  * plot

## extract
This module reads from the cases database to get information about the location
of the data and the data range of the data.
It extracts the data from the MATLAB results.
It saves the data as csv files.
This module runs only on the server for now.
### extract_data
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
## analyze 
Reads the data from the database and performs the analyze of the data.
It first performs validation(Data within range, correct type, ...)  
and verification(Compare data with input data of case from preprocessing ) 
of the data.
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