[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![Tests](https://github.com/Breakthrough-Energy/PostREISE/workflows/Pytest/badge.svg)

# PostREISE
This package is dedicated to the analysis and plotting of the output data.


## 1. Setup/Install
In the PostREISE package, locate the ***setup.py*** file and type:
`pip3 install .`. The other option is to update the PYTHONPATH environment
variable.



## 2. Analyze
The `postreise.analyze` module encloses several analysis modules.

### A. Transmission Congestion (Utilization) Analysis
To carry out transmission congestion analyses per scenario:
1. download the power flow output;
2. calculate congestion statistics;
3. display the data.

The ***[utilization_demo.ipynb][utilization]*** notebook shows the steps for
downloading, calculating and plotting the various statistics. Note that since
the plot outputs are meant to be interactive, they may not render on GitHub.

### B. Transmission Congestion (Surplus) Analysis
The congestion surplus for each hour can be calculated by calling
```python
postreise.analyze.transmission.congestion.calculate_congestion_surplus(scenario)
```
where `scenario` is a powersimdata.scenario.scenario.Scenario object in Analyze
state.

### C. Carbon Analysis
The hourly CO<sub>2</sub> emissions from a scenario may be analyzed by calling

```python
postreise.analyze.generation.carbon.generate_carbon_stats(scenario)
```
where `scenario` is a powersimdata.scenario.scenario.Scenario instance in the
analyze state.

The resulting data frame can be summed by generator type and bus by calling
```python
postreise.analyze.generation.carbon.summarize_carbon_by_bus(carbon, plant)
```
where `carbon` is a pandas.DataFrame as returned by `generate_carbon_stats` and
`grid` is a powersimdata.input.grid.Grid instance.

### D. Curtailment Analysis
The level of curtailment for a Scenario may be calculated in several ways.



#### I. Calculating Time Series
To calculate the time-series curtailment for each solar and wind generator, call
```python
from postreise.analyze.generation.curtailment import calculate_curtailment_time_series
calculate_curtailment_time_series(scenario)
```
where `scenario` is a `powersimdata.scenario.scenario.Scenario` instance in the
analyze state. If you call:
```python
postreise.analyze.generation.curtailment import calculate_curtailment_time_series_by_resources
calculate_curtailment_time_series_by_resources(scenario, resources={"solar", "wind"})
```
you will obtain a dictionary where the keys are solar and wind and the values are
the curtailment time-series for the associated resource.

You can also get the curtailment time-series by areas by calling:
```python
from postreise.analyze.generation.curtailment import calculate_curtailment_time_series_by_areas
calculate_curtailment_time_series_by_areas(scenario,
  areas={"interconnect": {"Western", "Texas"},
         "state": {"Washington", "California", "Idaho"},
         "loadzone": {"Bay Area", "El Paso", "Far West"}})
```
this returns a dictionary where the keys are the areas and the values are the
curtailment time-series for solar and wind in the associated area.

Finally, you can group the curtailment time-series by areas and resources as follows:
```python
postreise.analyze.generation.curtailment import calculate_curtailment_time_series_by_areas_and_resources
calculate_curtailment_time_series_by_areas_and_resources(scenario,
  areas={"interconnect": {"Western", "Texas"},
         "state": {"Washington", "California", "Idaho"},
         "loadzone": {"Bay Area", "El Paso", "Far West"}},
  resources={"solar", "wind"})
```
in that case the it returns a dictionary where the keys are the areas and the values
are a dictionary where the keys are the resources and the values the curtailment
time-series for the associated area-resource pair.



#### II. Summarizing Time Series: Plant => Bus/Location
A curtailment data frame with plants as columns can be further summarized by bus
or by location (substation) with:
```python
postreise.analyze.generation.curtailment.summarize_curtailment_by_bus(scenario)
```
or
```python
postreise.analyze.generation.curtailment.summarize_curtailment_by_location(scenario)
```



#### III. Calculating Annual Curtailment Percentage
An annual average curtailment value can be found for all wind/solar plants with

```python
postreise.analyze.generation.curtailment.calculate_curtailment_percentage(scenario)
```
where `scenario` is a `powersimdata.scenario.scenario.Scenario` instance in the
analyze state. To calculate the average curtailment just for wind or solar, call
```python
from postreise.analyze.generation.curtailment import calculate_curtailment_percentage
calculate_curtailment_percentage(scenario, resources={'wind'})
```
or
```python
from ostreise.analyze.generation.curtailment import calculate_curtailment_percentage
calculate_curtailment_percentage(scenario, resources={'solar'})
```


## 3. Plot
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
* Tornado plot: Horizontal bar chart styled to show both positive and negative
values cleanly.

Check out the notebooks within the [demo][plot_notebooks] folder.

[plot_notebooks]: https://github.com/Breakthrough-Energy/PostREISE/blob/develop/postreise/plot/demo/
[utilization]: https://github.com/Breakthrough-Energy/PostREISE/tree/develop/postreise/analyze/transmission/demo/utilization_demo.ipynb
[shadowprice]: https://github.com/Breakthrough-Energy/PostREISE/tree/develop/postreise/plot/demo/plot_shadowprice_demo.ipynb

The `plot_carbon_map` module is used to plot carbon emissions on a map.
There are two ways it can be used:
* Map carbon emissions per bus, size scaled to emissions quantity (tons) and
color coded by fuel type.
* Map carbon emissions per bus for two scenarios and compare.
Comparison map color codes by increase vs. decrease from first to second
scenario analyzed.

The `plot_carbon_bar` module is used to make barcharts comparing carbon
emissions of two scenarios.

The `projection_helpers.py` module contains helper functions such as
re-projection, necessary for mapping.
