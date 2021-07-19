from powersimdata import Scenario

from postreise.plot.plot_generation_ts_stack import plot_generation_time_series_stack

t2c = {
    "nuclear": "#173FA5",
    "hydro": "#0090FF",
    "geothermal": "#CC67F3",
    "other": "#8B36FF",
    "dfo": "#31E8CB",
    "coal": "#37404C",
    "ng": "#72818F",
    "solar": "#FFBB45",
    "wind": "#78D911",
    "solar_curtailment": "#FFBB45",
    "wind_curtailment": "#78D911",
}

t2l = {
    "nuclear": "Nuclear",
    "hydro": "Hydro",
    "geothermal": "Geothermal",
    "other": "Other",
    "dfo": "Distillate Fuel Oil",
    "coal": "Coal",
    "ng": "Natural Gas",
    "solar": "Solar",
    "wind": "Wind",
    "wind_offshore": "Wind Offshore",
    "biomass": "Biomass",
    "storage": "Storage",
    "solar_curtailment": "Solar Curtailment",
    "wind_curtailment": "Wind Curtailment",
    "wind_offshore_curtailment": "Offshore Wind Curtailment",
}

t2hc = {"solar_curtailment": "#996100", "wind_curtailment": "#4e8e0b"}

scenario = Scenario(1171)

resources = [
    "nuclear",
    "coal",
    "hydro",
    "geothermal",
    "other",
    "dfo",
    "ng",
    "solar",
    "wind",
    "storage",
    "solar_curtailment",
    "wind_curtailment",
]

plot_generation_time_series_stack(
    scenario,
    "Western",
    resources,
    time_freq="D",
    normalize=True,
    t2c=t2c,
    t2l=t2l,
    t2hc=t2hc,
)
