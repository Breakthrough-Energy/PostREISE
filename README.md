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
The `postreise.analyze` module encloses several analysis modules.

### A. Transmission Congestion (Utilization) Analysis
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

### B. Transmission Congestion (Surplus) Analysis
The congestion surplus for each hour can be calculated by calling
```postreise.analyze.congestion.calculate_congestion_surplus(scenario)```
where `scenario` is a powersimdata.scenario.scenario.Scenario object in Analyze
state.

### C. Analysis of Transmission Upgrades

#### I. Cumulative Upgrade Quantity
Using the change table of a scenario, the number of upgrades lines/transformers
and their cumulative upgraded capacity (for transformers) and cumulative
upgraded megawatt-miles (for lines) can be calculated with:
```
postreise.analyze.mwmiles.calculate_mw_miles(scenario)
```
where `scenario` is a powersimdata.scenario.scenario.Scenario object.

#### II. Cumulative Upgrade Quantity
The upgraded branches can also be classified into either interstate or
intrastate branches by calling:
```
postreise.analyze.statelines.classify_interstate_intrastate(scenario)
```
where `scenario` is a powersimdata.scenario.scenario.Scenario object.

### D. Carbon Analysis
The hourly CO<sub>2</sub> emissions from a scenario may be analyzed by calling
```
postreise.analyze.carbon.generate_carbon_stats(scenario)
```
where `scenario` is a powersimdata.scenario.scenario.Scenario object in Analyze
state.

The resulting dataframe can be summed by generator type and bus by calling
```
postreise.analyze.carbon.summarize_carbon_by_bus(carbon, plant)
```
where `carbon` is a pandas.DataFrame as returned by `generate_carbon_stats` and
`grid` is a powersimdata.input.grid.Grid object.

### E. Curtailment Analysis
The level of curtailment for a Scenario may be calculated in several ways.

#### I. Calculating Time Series
To calculate the time-series curtailment for each solar and wind generator, call
```
postreise.analyze.curtailment.calculate_curtailment_time_series(scenario)
```
where `scenario` is a powersimdata.scenario.scenario.Scenario object in Analyze
state. To calculate the curtailment just for wind or solar, call
```
postreise.analyze.curtailment.calculate_curtailment_time_series(scenario, resources={'wind'})
```
or
```
postreise.analyze.curtailment.calculate_curtailment_time_series(scenario, resources={'solar'})
```

#### II. Summarizing Time Series: Plant => Bus/Location
A curtailment dataframe with plants as columns can be further summarized by bus
or by location (substation) with:
```
postreise.analyze.curtailment.summarize_curtailment_by_bus(curtailment, grid)
```
or
```
postreise.analyze.curtailment.summarize_curtailment_by_location(curtailment, grid)
```
where `curtailment` is a pandas.DataFrame as returned by
`calculate_curtailment_time_series` and `grid` is a
powersimdata.input.grid.Grid object.

#### III. Calculating Annual Curtailment Percentage
An annual average curtailment value can be found for all wind/solar plants with
```
postreise.analyze.curtailment.calculate_curtailment_percentage(scenario)
```
where `scenario` is a powersimdata.scenario.scenario.Scenario object in Analyze
state. To calculate the average curtailment just for wind or solar, call
```
postreise.analyze.curtailment.calculate_curtailment_percentage(scenario, resources={'wind'})
```
or
```
postreise.analyze.curtailment.calculate_curtailment_percentage(scenario, resources={'solar'})
```

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
* Tornado plot: Horizontal bar chart styled to show both positive and negative values cleanly

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