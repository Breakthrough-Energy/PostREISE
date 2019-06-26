# PostREISE
This package is dedicated to the analysis and plotting of the output data. It
also takes care of constructing the PG (power generated) and PF (power flow)
from the MATLAB binary files produced by MATPOWER; and transferring data from/to
the server from/to the local machine.

## 1. Setup/Install
This WesternInterconnectNetwork.


### A. WesternInterconnectNetwork
In the WesternInterconnect package, locate the ***setup.py*** file and type:
`pip3 install .` Do not forget to update your PYTHONPATH environment variable.


### C. PostREISE
In the PostREISE package, locate the ***setup.py*** file and type:
`pip3 install .` Do not forget to update your PYTHONPATH environment variable.



## 2. Extract Data
The aim of the `postreise.extract.extract_data` module is three fold:
* locate the outputs of the simulation;
* extract the results from the MATLAB files and;
* save the data as pickle files.



## 3. Transfer Data
Data are located on the server. These can be easily transferred to your local
machine using functions written in the `postreise.process.transferdata` module.

The OutputData class in `powersimdata.input.profiles` and the InputData class
in `powersimdata.output.profiles` make use of these functions to download the
simulation inputs an outputs. Using the a *Scenario* object to gat data is the
way to go. To illustrate, to download the the demand, hydro, solar and wind
profiles as well as the PG and PF simulation outputs of the base case scenario
for the Western Interconnection (*id*=0). 

```
from powersimdata.scenario.scenario import Scenario

scenario = Scenario('0')
demand = scenario.state.get_demand()
hydro = scenario.state.get_hydro()
solar = scenario.state.get_solar()
wind = scenario.state.get_wind()
pg = scenario.state.get_pg()
pf = scenario.state.get_pf()
``` 



## 4. Analyze
The `postreise.analyze` module encloses the congestion analysis.

### A. Transmission Congestion Analysis
To carry out transmission congestion analyses per scenario:
1. download the power flow output;
2. calculate congestion statistics;
3. display the data.

The notebook [transmission_analysis_demo.ipynb](https://github.com/intvenlab/PostREISE/tree/develop/postreise/analyze/demo/transmission_analysis_demo.ipynb) notebook shows the steps for downloading and calculation of various statistics. The notebook [congestion_interactive_map.ipynb](https://github.com/intvenlab/PostREISE/tree/develop/postreise/analyze/demo/WECC_Congestion_interactive_map.ipynb) notebook shows how the output of the transmission_analyses notebook is used to display the congested transmission lines. (Note that since the plot outputs are meant to be interactive, they may not render on GitHub. A sample static shot can be found [here](https://github.com/intvenlab/PostREISE/tree/develop/postreise/analyze/demo/sampleTransmissionCongestion.PNG)).


## 5. Plot
The `postreise.plot.analyze_pg` module is dedicated to the analysis of the PG
(Power Generated) output file. There are currently 7 analysis implemented:
* Time series of power generated and demand in one zone. The contribution of
the different resources is broken down by colors.
* Time series of the power generated for one resource in multiple zones.
* Time series of the curtailment for one renewable resource in one zone.
* Calculate statistical relationships (correlation coefficients) between the
power generated in two zones for one resource. Correlation matrix is used to
display results.
* Calculate the proportion of resources and generation per resources in one
zone. Bar charts are used for display.
* Time series of power generated in one zone for one resource. Also superimpose
the time series of the power generated by 2, 8 and 15 randomly chosen plants in
the same zone and using the same resource.
* Calculate the capacity factor of one resource in one zone and show result
using box plots.

Check out the notebooks within the [demo][1] folder.

The `postreise.plot.analyze_set` module accomplishes a similar job for a set of
scenario. The [october_meeting][2] Jupyter notebook illustrates the plot
routines that have been implemented implemented.

[1]: https://github.com/intvenlab/PostREISE/tree/addAnalyzeAndPlot/postreise/plot/demo/
[2]: https://github.com/intvenlab/PostREISE/tree/addAnalyzeAndPlot/postreise/plot/demo/october_meeting.ipynb