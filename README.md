# PostREISE
---

This package contains the following modules:
  * extract
  * analyze
  * plot
  
It requires the Matlab simulation engine.

## 1. Setuo/Install
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


## 3. Analyzing data 
Reads the data from the database and performs the data analysis. It first performs validation (data within range, correct type, ...) and verification (compare data with input data of case from preprocessing) of the data.


## 4. Plot
This module reads the data from the analyze process and plots the output. Note that this module could be combined with the analyze step.
