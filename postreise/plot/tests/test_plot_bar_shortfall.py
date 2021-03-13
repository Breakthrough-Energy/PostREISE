import pandas as pd
import pytest

from postreise.plot.plot_bar_shortfall import plot_bar_shortfall


def test_plot_bar_shortfall_throws_error_for_target_df_not_a_pandas_dataframe():
    with pytest.raises(TypeError):
        plot_bar_shortfall(
            areas="all",
            scenario_ids=[823, 824],
            target_df="not a dataframe",
        )


def test_plot_bar_shortfall_throws_error_for_strategy_not_a_dictionary():
    with pytest.raises(TypeError):
        plot_bar_shortfall(
            areas="all",
            scenario_ids=[823, 824],
            target_df=pd.DataFrame(),
            strategy="collaborative",
        )


def test_plot_bar_shortfall_throws_error_for_different_length_of_scenario_ids_and_scenario_names():
    with pytest.raises(ValueError):
        plot_bar_shortfall(
            areas="all",
            scenario_ids=[823, 824],
            target_df=pd.DataFrame(),
            strategy={823: "collaborative"},
            scenario_names=["USA 2016"],
        )


def test_plot_bar_shortfall_throws_error_for_baseline_scenario_not_a_string_or_integer():
    with pytest.raises(TypeError):
        plot_bar_shortfall(
            areas="all",
            scenario_ids=[823, 824],
            target_df=pd.DataFrame(),
            strategy={823: "collaborative"},
            scenario_names=["USA 2016", "USA 2020"],
            baseline_scenario=["1", "2", "3"],
        )


def test_plot_bar_shortfall_throws_error_for_baseline_scenario_name_not_a_string():
    with pytest.raises(TypeError):
        plot_bar_shortfall(
            areas="all",
            scenario_ids=[823, 824],
            target_df=pd.DataFrame(),
            strategy={823: "collaborative"},
            scenario_names=["USA 2016", "USA 2020"],
            baseline_scenario=823,
            baseline_scenario_name=888,
        )
