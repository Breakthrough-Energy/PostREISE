import json
import os
import urllib

from bokeh.models import ColumnDataSource, HoverTool, Label
from bokeh.plotting import figure
from bokeh.sampledata import us_states
from bokeh.tile_providers import Vendors, get_provider

from postreise.plot.projection_helpers import project_borders


def download_states_shapefile():
    """Downloads shapefile for U.S. states.

    :return: (*str*) -- path to shapefile.
    """
    shapes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shapes")
    os.makedirs(shapes_path, exist_ok=True)
    url_base = "https://besciences.blob.core.windows.net/us-shapefiles/"
    shape_filename = "cb_2018_us_state_20m"
    shape_entensions = ["cpg", "dbf", "prj", "shp", "shx"]
    for ext in shape_entensions:
        filepath = os.path.join(shapes_path, f"{shape_filename}.{ext}")
        if not os.path.isfile(filepath):
            r = urllib.request.urlopen(f"{url_base}{shape_filename}.{ext}")
            with open(filepath, "wb") as f:
                f.write(r.read())
    filename = os.path.join(shapes_path, f"{shape_filename}.shp")
    return filename


def download_states_json():
    """Downloads json file containing coordinates for U.S. state outlines.

    :return: (*str*) -- path to json file.
    """
    shapes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shapes")
    os.makedirs(shapes_path, exist_ok=True)
    json_filename = "state_shapes.json"
    filepath = os.path.join(shapes_path, json_filename)
    if not os.path.isfile(filepath):
        url_base = "https://besciences.blob.core.windows.net/us-shapefiles/"
        r = urllib.request.urlopen(f"{url_base}{json_filename}")
        with open(filepath, "wb") as f:
            f.write(r.read())
    return filepath


def get_state_borders():
    """Get state borders as a dictionary of coordinate arrays.

    :return: (*dict*) -- dictionary with keys from the specified shapefile column,
        values are dict with keys of {"lat", "lon"}, values are coordinates, padded by
        nan values to indicate the end of each polygon before the start of the next one.
    """
    try:
        json_filepath = download_states_json()
        with open(json_filepath, "r") as f:
            us_states_dat = json.load(f)
    except Exception:
        # In case we can't get the json file, use the bokeh shapes
        us_states_dat = us_states.data
    return us_states_dat


def plot_states(
    state_list=None,
    colors=None,
    line_color="grey",
    line_width=1,
    fill_alpha=1,
    labels_list=None,
    legend_colors=None,
    legend_labels=None,
    legend_title=None,
    font_size="10pt",
    bokeh_figure=None,
    web=True,
    us_states_dat=None,
    background_map=True,
):
    """Plots US state borders and allows color coding by state,
        for example to represent different emissions goals.

    :param list state_list: list of us states to color code.
    :param str/iterable colors: color or colors associated with states in state_list.
    :param str line_color: color of state outlines.
    :param int/float line_width: thickness of state outlines.
    :param int/float fill_alpha: fill opaqueness for state patches.
    :param iterable labels_list: list of labels for us states.
    :param iterable legend_colors: list of colors for legend.
    :param iterable legend_labels: list of labels for colors in legend.
    :param str legend_title: title for legend.
    :param float font_size: citation font size, for non web version only
    :param bokeh.plotting.figure.Figure bokeh_figure: figure to plot onto, if provided.
        If not, a new figure will be created.
    :param bool web: if true, formats for website with hover tips
    :param dict us_states_dat: dictionary of state border lats/lons. If None, get
        from :func:`postreise.plot.plot_states.get_state_borders`.
    :param bool background_map: if True, plot a map background behind state borders.
    :raises TypeError: if inputs are wrong type.
    :raises ValueError: if inputs have wrong values.
    :return: (*bokeh.plotting.figure.Figure*) -- map of us states with option to color
        by value.
    """
    # Get state borders data if necessary
    if us_states_dat is None:
        us_states_dat = get_state_borders()
    if state_list is None:
        # Default to continental US from state borders data, w/ no colors, no labels.
        if labels_list is not None:
            raise TypeError("Cannot specify labels_list without state_list")
        if colors is not None and not isinstance(colors, str):
            raise TypeError("Cannot specify list of colors without state_list")
        state_list = list(set(us_states_dat.keys()) - {"AK", "HI", "DC", "PR"})
    else:
        if colors is not None:
            if not isinstance(colors, str):
                try:
                    if len(state_list) != len(colors):
                        raise ValueError("state_list and colors must be same length")
                except TypeError:
                    raise TypeError("colors must be str or iterable")
        if labels_list is not None:
            try:
                if len(state_list) != len(labels_list):
                    raise ValueError("State_list and labels_list must be same length")
            except TypeError:
                raise TypeError("labels_list must be an iterable")
    if legend_colors is not None or legend_labels is not None:
        try:
            if len(legend_colors) != len(legend_labels):
                raise ValueError("Length of legend_colors and legend_labels must match")
        except TypeError:
            raise TypeError("legend_colors and legend_labels must be iterables or None")
    # If no color specified, default to white. Either way, apply to all states.
    colors = "white" if colors is None else colors
    colors = [colors for s in state_list] if isinstance(colors, str) else colors
    all_state_xs, all_state_ys = project_borders(us_states_dat, state_list=state_list)
    # Initialize figure if necessary
    if bokeh_figure is None:
        p = figure(
            tools="pan,wheel_zoom,reset,save",
            x_axis_location=None,
            y_axis_location=None,
            plot_width=800,
            plot_height=800,
            output_backend="webgl",
            sizing_mode="stretch_both",
            match_aspect=True,
        )
    else:
        p = bokeh_figure
    # if legend info is passed, plot legend squares behind graph so they're hidden
    if legend_colors is not None:
        for i, c in enumerate(legend_colors):
            p.square(
                -8.1e6,
                [5.2e6, 5.3e6],
                fill_color=c,
                color=c,
                size=300,
                legend_label=legend_labels[i],
            )
    # Tiles for map background
    if background_map:
        p.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))
    # State patches
    state_patch_info = {
        "xs": all_state_xs,
        "ys": all_state_ys,
        "color": colors,
        "state_name": state_list,
    }
    if labels_list is not None:
        state_patch_info["label"] = labels_list
    patch = p.patches(
        "xs",
        "ys",
        source=ColumnDataSource(state_patch_info),
        fill_alpha=fill_alpha,
        fill_color="color",
        line_color=line_color,
        line_width=line_width,
    )
    if labels_list is not None:
        if web:
            # For the web, add hover-over functionality
            hover = HoverTool(
                tooltips=[("State", "@state_name"), ("Goal", "@label")],
                renderers=[patch],
            )
            p.add_tools(hover)
        else:
            # For not the web, add static labels
            for i, state in enumerate(state_list):
                a1, b1 = project_borders(us_states_dat, state_list=[state])
                citation = Label(
                    x=min(a1[0]) + 100000,
                    y=(max(b1[0]) + min(b1[0])) / 2,
                    x_units="data",
                    y_units="data",
                    text_font_size=font_size,
                    text=labels_list[i],
                    render_mode="css",
                    border_line_color="black",
                    border_line_alpha=0,
                    background_fill_color="white",
                    background_fill_alpha=0.8,
                )
                p.add_layout(citation)

    if legend_colors is not None:
        if legend_title is not None:
            p.legend.title = legend_title
        p.legend.location = "bottom_right"
        p.legend.label_text_font_size = "12pt"
        p.legend.title_text_font_size = "12pt"
    return p
