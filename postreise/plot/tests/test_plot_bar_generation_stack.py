import pytest

from postreise.plot.plot_bar_generation_stack import plot_bar_generation_stack


def test_plot_bar_generation_stack_throws_error_for_scenario_ids_not_a_list():
    with pytest.raises(TypeError):
        plot_bar_generation_stack(
            "Western",
            {823, 824},
            ["wind", "solar", "coal"],
        )


def test_plot_bar_generation_stack_throws_error_for_resources_not_a_list():
    with pytest.raises(TypeError):
        plot_bar_generation_stack(
            "Western",
            [823, 824],
            {"wind", "solar", "coal"},
        )


def test_plot_bar_generation_stack_throws_error_for_different_length_of_areas_and_area_types():
    with pytest.raises(ValueError):
        plot_bar_generation_stack(
            ["Western", "Eastern"],
            [823, 824],
            ["wind", "solar", "coal"],
            area_types="interconnect",
        )


def test_plot_bar_generation_stack_throws_error_for_different_length_of_scenario_ids_and_scenario_names():
    with pytest.raises(ValueError):
        plot_bar_generation_stack(
            ["Western", "Eastern"],
            [823, 824],
            ["wind", "solar", "coal"],
            scenario_names="USA Basecase",
        )


def test_plot_bar_generation_stack_throws_error_for_titles_not_a_dict():
    with pytest.raises(TypeError):
        plot_bar_generation_stack(
            ["Western", "Eastern"],
            [823, 824],
            ["wind", "solar", "coal"],
            titles=["WECC", "EI"],
        )


def test_plot_bar_generation_stack_throws_error_for_filenames_not_a_dict():
    with pytest.raises(TypeError):
        plot_bar_generation_stack(
            ["Western", "Eastern"],
            [823, 824],
            ["wind", "solar", "coal"],
            save=True,
            filenames=["WECC", "EI"],
        )
