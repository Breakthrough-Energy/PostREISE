mpl = {
    "single": {
        "curtailment_eastern": (
            "curtailment_solar_eastern_ts.png",
            "curtailment_wind_eastern_ts.png",
        ),
        "capacity_vs_cf_solar_western_scatter": "capacity_vs_cf_solar_western_scatter.png",
        "capacity_vs_cost_curve_slope_coal_eastern_scatter": "capacity_vs_cost_curve_slope_coal_eastern_scatter.png",
        "capacity_vs_curtailment_solar_western_scatter": "capacity_vs_curtailment_solar_western_scatter.png",
        "curtailment_usa_heatmap": "curtailment_usa_heatmap.png",
        "generation_stack_western_ts": "generation_stack_western_ts.png",
    },
    "comp": {
        "capacity_vs_generation_bar": (
            "capacity_vs_generation_ca_bar.png",
            "capacity_vs_generation_western_bar.png",
        ),
        "capacity_vs_generation_pie": (
            "capacity_vs_generation_wa_pie.png",
            "capacity_vs_generation_western_pie.png",
        ),
        "energy_emission_stack_bar": "energy_emission_stack_bar.png",
        "shortfall_nv": "shortfall_nv.png",
        "emission_bar": "emission_bar.png",
        "shortfall_nv": "shortfall_nv.png",
    },
}


def save_matplotlib(result, filename):
    for i, output in enumerate(result.outputs):
        with open(filename[i], "wb") as f:
            f.write(output.data["image/png"])
