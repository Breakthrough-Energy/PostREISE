# This plotting module has a corresponding demo notebook in
#   PostREISE/postreise/plot/demo: plot_lmp.ipynb

import pandas as pd
from bokeh.layouts import row
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.tile_providers import Vendors, get_provider
from bokeh.sampledata import us_states
from bokeh.palettes import Turbo256
from postreise.plot.projection_helpers import project_bus
from postreise.plot.plot_carbon_map import get_borders

# make default states list for drawing of state borders
default_states_dict = us_states.data.copy()
del default_states_dict["HI"]
del default_states_dict["AK"]
default_states_list = list(default_states_dict.keys())


def map_lmp(s_grid, lmp,
             us_states_dat=us_states.data):
    """ Plot average LMP by color coding buses

    :param s_grid: scenario grid
    :type s_grid: pandas.DataFrame
    :param lmp: lmps (locational marginal prices) calculated for the scenario
    :type lmp: pandas.DataFrame
    :param file_name: name for output png file
    :type file_name: str
    :param us_states_dat: us_states data file, imported from bokeh
    :type us_states_dat: dict
    """

    bus = project_bus(s_grid.bus)
    lmp_split_points = list(range(0, 256, 1))
    bus_segments = _construct_bus_data(bus, lmp, lmp_split_points)
    return _construct_shadowprice_visuals(
        lmp_split_points, bus_segments, us_states_dat)


def _construct_bus_data(bus_map, lmp, lmp_split_points):
    """Adds lmp data to each bus, splits buses into lmp segments for coloring

    :param bus_map: bus dataframe with location data
    :type bus_map: pandas.DataFrame
    :param lmp: lmp dataframe
    :type lmp: pandas.DataFrame
    :param lmp_split_points: lmp values to split the bus data.
    :type lmp_split_points: list(float)
    :return: bus data split into segments
    :rtype: list(pandas.DataFrame)
    """
    # Add mean lmp to bus dataframe
    lmp_mean = pd.DataFrame(lmp.mean())
    lmp_mean = lmp_mean.rename(columns={lmp_mean.columns[0]: 'lmp'})

    # min and max values for 'continuous' color scale, in $MW/h
    min_lmp_clamp = 20
    max_lmp_clamp = 45

    lmp_mean['lmp_norm'] = (lmp_mean.lmp -
                            min_lmp_clamp) / (
                                   max_lmp_clamp-min_lmp_clamp) * 256
    bus_map = pd.concat([bus_map, lmp_mean], axis=1)
    bus_map_agg = group_lat_lon(bus_map)

    # set a min and a max so all values are assigned a color
    bus_map_agg.loc[(bus_map_agg.lmp_norm <= 0), 'lmp_norm'] = 0.01
    bus_map_agg.loc[(bus_map_agg.lmp_norm > 255), 'lmp_norm'] = 255
    bus_map_agg = pd.DataFrame(bus_map_agg)

    return bus_map_agg


def group_lat_lon(bus_map):
    """Groups data and sums values, based on coordinates.
        Takes mean of means of buses at same coordinates
        Rounds locations for grouping to nearest latlon decimal (1/10) degrees

    :param pandas.DataFrame bus_map: data frame bus location and lmp means
    :return: (pandas.DataFrame) -- data frame, aggregated by rounded lat lon
        coordinates
    """
    bus_map1 = bus_map.copy()

    bus_map1.lat = bus_map1.lat.round(1)
    bus_map1.lon = bus_map1.lon.round(1)

    bus_map2 = bus_map1.groupby(["lat", "lon"]).agg(
        {'lmp_norm': 'mean', 'lmp': 'mean', 'x': 'mean', 'y': 'mean'})

    return bus_map2


def _construct_shadowprice_visuals(lmp_split_points,
                                   bus_segments, us_states_dat ):
    """Use bokeh to plot formatted data. Make map showing congestion,
        with green dot for transformer winding, blue dot transformer,
        and lines for congested branches with varying color and thickness
        indicating degree of congestion


    :param lmp_split_points: the lmp vals we have chosen to split bus data
    :type lmp_split_points: list(float)
    :param bus_segments: bus data split by lmp
    :type bus_segments: list(pandas.DataFrame)
    :param us_states_dat: us_states data file, imported from bokeh
    :type us_states_dat: dict
    :param file_name: name for output png file
    :type file_name: str
    """

    tools = "pan,wheel_zoom,reset,hover,save"
    p = figure(tools=tools,
               x_axis_location=None, y_axis_location=None, plot_width=800,
               plot_height=800, output_backend="webgl")

    # Add USA map
    p.add_tile(get_provider(Vendors.CARTODBPOSITRON))
    # state borders
    a, b = get_borders(us_states_dat.copy())
    p.patches(a, b, fill_alpha=0.0,
              line_color="black", line_width=2)
    # Add colored circles for bus locations

    bus_segments.lmp_norm = bus_segments.lmp_norm.astype(int)
    bus_segments['col'] = bus_segments['lmp_norm'].apply(lambda x: Turbo256[x])
    bus_cds = ColumnDataSource({'x': bus_segments['x'],
                                'y': bus_segments['y'],
                                'col': bus_segments['col']})
    p.circle('x', 'y', color='col', size=2,
             source=bus_cds)

    # Add legend
    bus_legend = _construct_bus_legend(lmp_split_points)
    return row(bus_legend, p)


def _construct_bus_legend(lmp_split_points):
    """Construct the legend for lmp at each bus

    :param lmp_split_points: the lmp values we have chosen to
        split the bus data
    :type lmp_split_points: list(float)
    :return: the legend showing lmp for each bus
    :rtype: bokeh.plotting.figure
    """
    x_range = ['']
    bars, bar_len_sum, labels = _get_bus_legend_bars_and_labels(
        lmp_split_points, x_range)

    # Make legend
    p = figure(x_range=x_range, plot_height=800, plot_width=110,
               toolbar_location=None, tools="", output_backend="webgl")
    p.vbar_stack(list(bars.keys())[1:], x='x_range', width=0.9,
                 color=Turbo256[:(len(bars)-1)], source=bars)

    p.y_range.start = -1
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    p.yaxis.ticker = list(labels.keys())
    p.yaxis.major_label_overrides = labels

    p.text(x=[-0.05], y=[bar_len_sum * 1.01], text=[f' $/MWh'],
           text_font_size='12pt')

    return p


def _get_bus_legend_bars_and_labels(lmp_split_points, x_range):
    """get the bar lengths and labels for the bus legend

    :param lmp_split_points: the lmp vs we have chosen to split the bus data
    :type lmp_split_points: list(float)
    :param x_range: the x-range for the vbar_stack
    :type x_range: list(string)
    :return: bar lengths and labels for the bus legend
    :rtype: dict, float, dict
    """
    bars = {'x_range': x_range}
    bar_length_sum = 0
    labels = {}  # { y-position: label_text, ... }
    for i in range(len(lmp_split_points)-2):
        bar_length = 0
        if i == 0 or i == len(lmp_split_points)-1:
            # For first and last bars, clamp bar length
            # to prevent extreme min, max vals from overwhelming the legend
            lmp_diff = lmp_split_points[i+1]-lmp_split_points[i]
            bar_length = 1 if lmp_diff < 1 else 5 if lmp_diff > 5 else lmp_diff
        elif i != len(lmp_split_points)-1:
            # max_lmp has a label but no bar
            lmp_diff = lmp_split_points[i+1]-lmp_split_points[i]
            # Min bar length of 1 to ensure small bars are visible
            bar_length = max(1, round(lmp_diff, 1))

        labels[round(bar_length_sum, -1)] = \
            str(round(((lmp_split_points[i]-1) * (45-20) / 256+20), 0))
        if i != len(lmp_split_points)-1:
            bars[str(i)] = [bar_length]
            bar_length_sum += bar_length

    return bars, bar_length_sum, labels
