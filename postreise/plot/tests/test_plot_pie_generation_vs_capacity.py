import pytest

from postreise.plot.plot_pie_generation_vs_capacity import (
    plot_pie_generation_vs_capacity,
)


def test_plot_pie_generation_vs_capacity_throws_error_for_different_length_of_areas_and_area_types():
    with pytest.raises(ValueError):
        plot_pie_generation_vs_capacity(
            areas=["all", "Western", "Texas", "Eastern"],
            area_types=["interconnect"],
            scenario_ids=[823, 824],
            scenario_names=["USA 2016", "USA 2020"],
            min_percentage=2.5,
        )


def test_plot_pie_generation_vs_capacity_throws_error_for_different_length_of_scenario_ids_and_scenario_names():
    with pytest.raises(ValueError):
        plot_pie_generation_vs_capacity(
            areas=["all", "Western", "Texas", "Eastern"],
            area_types=[None, "interconnect", None, None],
            scenario_ids=[823, 824],
            scenario_names=["USA 2016"],
            min_percentage=2.5,
        )


def test_plot_pie_generation_vs_capacity_throws_error_for_less_than_two_scenario_ids_and_custom_data_is_provided():
    with pytest.raises(ValueError):
        plot_pie_generation_vs_capacity(
            areas=["all", "Western", "Texas", "Eastern"],
            area_types=[None, "interconnect", None, None],
            scenario_ids=[823],
            scenario_names=["USA 2016"],
            min_percentage=2.5,
        )


def test_plot_pie_generation_vs_capacity_throws_error_for_resource_labels_not_in_a_dictionary_format():
    with pytest.raises(TypeError):
        plot_pie_generation_vs_capacity(
            areas=["all", "Western", "Texas", "Eastern"],
            area_types=[None, "interconnect", None, None],
            scenario_ids=[823, 824],
            scenario_names=["USA 2016", "USA 2020"],
            resource_labels=["My Natural Gas", "My Coal"],
            min_percentage=2.5,
        )


def test_plot_pie_generation_vs_capacity_throws_error_for_resource_colors_not_in_a_dictionary_format():
    with pytest.raises(TypeError):
        plot_pie_generation_vs_capacity(
            areas=["all", "Western", "Texas", "Eastern"],
            area_types=[None, "interconnect", None, None],
            scenario_ids=[823, 824],
            scenario_names=["USA 2016", "USA 2020"],
            resource_labels={"ng": "My Natural Gas", "coal": "My Coal"},
            resource_colors=["red", "blue", "yellow"],
            min_percentage=2.5,
        )
