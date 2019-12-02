# PostREISE
This package is dedicated to the analysis and plotting of the output data. It
also takes care of constructing the PG (power generated) and PF (power flow)
from the MATLAB binary files produced by MATPOWER; and transferring data from/to
the server from/to the local machine.



## 1. Setup/Install
In the PostREISE package, locate the ***setup.py*** file and type:
`pip3 install .`. The other option is to update the PYTHONPATH environment
variable.



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
```python
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

The ***[transmission_analysis_demo.ipynb][transmission]*** notebook shows the
steps for downloading and calculating various statistics. The
***[congestion_interactive_map.ipynb][congestion]*** notebook shows how the
output of the ***[transmission_analysis_demo.ipynb][transmission]*** notebook
is used to display the congested transmission lines. Note that since the plot
outputs are meant to be interactive, they may not render on GitHub.



## 5. Plot
The `postreise.plot.analyze_pg` module is dedicated to the analysis of the PG
(Power Generated) output file. There are currently 8 analysis implemented:
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
* Map the shadowprice and congested branches for a given hour

Check out the notebooks within the [demo][plot_notebooks] folder.

The `postreise.plot.analyze_set` module accomplishes a similar job for a set of
scenarios. This is illustrated [here][collection].

[plot_notebooks]: https://github.com/intvenlab/PostREISE/blob/develop/postreise/plot/demo/
[collection]: https://github.com/intvenlab/PostREISE/blob/develop/postreise/plot/demo/collection.ipynb
[transmission]: https://github.com/intvenlab/PostREISE/tree/develop/postreise/analyze/demo/transmission_analysis_demo.ipynb
[congestion]: https://github.com/intvenlab/PostREISE/tree/develop/postreise/analyze/demo/congestion_interactive_map.ipynb
[shadowprice]: https://github.com/intvenlab/PostREISE/tree/develop/postreise/plot/demo/plot_shadowprice_demo.ipynb

The `carbon_plot` module is used to plot carbon emissions on a map.
There are two ways it can be used:
* Map carbon emissions per bus, size scaled to emissions quantity (tons) and color coded by fuel type.
* Map carbon emissions per bus for two scenarios and compare.
Commparison map color codes by increase vs. decrease from first to second scenario analyzed.

The `carbon_barchart` module is used to make barcharts comparing carbon emissions of two scenarios.

The `carbon_plothelper.py` module contains helper functions such as reprojection, necessary for mapping.