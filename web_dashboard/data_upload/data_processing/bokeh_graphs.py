from postreise.analyze.transmission.utilization import (
    get_utilization,
    generate_cong_stats,
)
from postreise.plot.plot_lmp_map import map_lmp
from postreise.plot.plot_utilization_map import map_utilization, map_risk_bind
from postreise.analyze.generation.emissions import (
    summarize_emissions_by_bus,
    generate_emissions_stats,
)
from postreise.plot.plot_carbon_map import (
    map_carbon_emission,
    map_carbon_emission_comparison,
    combine_bus_info_and_emission,
)
from powersimdata.scenario.scenario import Scenario

# Useful for when you already have a figure ready
def upload_bokeh_fig(fig_name, fig, scenario_id, blob_client, path, version):
    """Takes a bokeh figure and uploads it to azure blob storage. Mostly a
    wrapper to upload_bokeh_figure_as_json_gzip() but it also does some filename
    formatting.
    :param str fig_name: name of the figure to upload
    :param TODO fig: the bokeh figure to upload
    :param str scenario_id: scenario id of the figure to upload
    :param TODO blob_client: the azure blob client that will upload the figure
    :param str path: a local file path where the figure will be saved
    :param str version: the version number of the figure
    """
    print(f"Uploading {fig_name}")

    filename = f"{scenario_id}_{fig_name}"
    blob_client.upload_bokeh_figure_as_json_gzip(
        figure=fig,
        string_identifier=filename,
        local_save_path=f"{path}{filename}.json.gzip",
        blob_path=f"{version}/{scenario_id}/{fig_name}.json.gzip",
    )


# Take a single scenario and create all bokeh graphs and upload
def create_and_upload_bokeh_figs_for_scenario(
    scenario_id, graph_types, blob_client, path, version, busmap_hist=None
):
    """Automates creation of bokeh figures for a single scenario and uploads
    them to azure blob storage.
    :param str scenario_id: scenario id of the figure to upload
    :param TODO graph_types: list of graphs to create
    :param TODO blob_client: the azure blob client that will upload the figure
    :param str path: a local file path where the figure will be saved
    :param str version: the version number of the figure
    :param TODO busmap_hist: historical data used to create the carbon diff
    graphs. busmap_hist will be compared to the current scenario.
    """
    print(f"\nLoading data for scenario {scenario_id}")

    scenario = Scenario(scenario_id)
    grid = scenario.state.get_grid()

    # Fetch data now to avoid duplicate fetching / work
    if (
        "transmission_utilization_map"
        or "transmission_risk_map"
        or "transmission_bind_map" in graph_types
    ):
        branch = grid.branch
        pf = scenario.state.get_pf()
        if "transmission_utilization_map" in graph_types:
            pf_med = get_utilization(branch, pf, median=True)
        if "transmission_risk_map" or "transmission_bind_map" in graph_types:
            cong_stats = generate_cong_stats(pf, branch)
    if "lmp_map" in graph_types:
        lmp = scenario.state.get_lmp()
    if "carbon_map" or "carbon_diff_map" in graph_types:
        carbon_by_bus = summarize_emissions_by_bus(
            generate_emissions_stats(scenario), grid
        )
        busmap = combine_bus_info_and_emission(grid.bus, carbon_by_bus)

    # Map each graph type to a function to create the correct figure
    # We use a function because otherwise all the figs will be created at once
    # fmt: off
    # Cheating black here because this is way more readable as-is
    generate_fig = {
        'transmission_utilization_map': lambda: map_utilization(pf_med, branch, is_website=True),
        'transmission_risk_map': lambda: map_risk_bind('risk', cong_stats, branch, is_website=True),
        'transmission_bind_map': lambda: map_risk_bind('bind', cong_stats, branch, is_website=True),
        'lmp_map': lambda: map_lmp(grid, lmp, is_website=True),
        'carbon_map': lambda: map_carbon_emission(busmap),
        'carbon_diff_map': lambda: map_carbon_emission_comparison(busmap_hist, busmap),
    }
    # fmt: on

    # Create bokeh_figures
    print(f"Creating bokeh figures for {scenario_id}")
    for graph_type in graph_types:
        if graph_type not in generate_fig:
            print(f"ERROR: graph type {graph_type} does not exist")
            return -1

        print(f"\n{graph_type}\n")
        fig = generate_fig[graph_type]()
        upload_bokeh_fig(graph_type, fig, scenario_id, blob_client, path, version)

    print("\nFigures upload complete")
