import json
import os
import urllib

import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool, Legend, LegendItem
from bokeh.sampledata import us_states
from bokeh.tile_providers import Vendors, get_provider

from postreise.plot.canvas import create_map_canvas
from postreise.plot.check import _check_func_kwargs
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


def expand_data_source(patches, state2data, key_name):
    """Add data to a bokeh patch object

    :param bokeh.models.renderers.GlyphRenderer patches: states as glyphs.
    :param dict state2data: keys are states abbreviation and values are data.
    :param str key_name: name to use for the key in data source.
    :return: (*bokeh.models.renderers.GlyphRenderer*) -- updated patches.
    :raises TypeError:
        if ``state2data`` is not a dict.
        if ``key_name`` is not a str.
    :raises ValueError:
        if states in ``state2data`` and  ``patches`` differ.
    """
    if not isinstance(state2data, dict):
        raise TypeError("state2data must be a dict")
    if not isinstance(key_name, str):
        raise TypeError("key_name must be a str")

    if len(set(patches.data_source.data["state_name"]) - set(state2data.keys())) != 0:
        raise ValueError("states in patches are missing from state2data")

    patches.data_source.data[key_name] = [
        state2data[s] for s in patches.data_source.data["state_name"]
    ]
    return patches


def add_state_borders(
    canvas,
    state_list=None,
    background_map=False,
    line_color="grey",
    line_width=1,
    fill_alpha=1,
):
    """Add state borders onto canvas.

    :param bokeh.plotting.figure canvas: canvas.
    :param list state_list: list of states to display, default to continental US.
    :param bool background_map: add background behind state borders.
    :param str line_color: color of state outlines.
    :param int/float line_width: thickness of state outlines.
    :param int/float fill_alpha: opaqueness for state patches.
    :return: (*bokeh.plotting.figure.Figure*) -- canvas with state borders.
    :raises TypeError:
        if ``background_map`` is not a boolean.
        if ``line_color`` is not a str.
        if ``line_width`` is not a int or float.
        if ``fill_alpha`` is not a int or float.
    """
    if not isinstance(background_map, bool):
        raise TypeError("background map must be a bool")
    if not isinstance(line_color, str):
        raise TypeError("line_color must be a str")
    if not isinstance(line_width, (int, float)):
        raise TypeError("line_width must be a int or float")
    if not isinstance(fill_alpha, (int, float)):
        raise TypeError("fill_alpha must be a int or float")

    us_states_dat = get_state_borders()
    if state_list is None:
        state_list = set(us_states_dat.keys()) - {"AK", "HI", "DC", "PR"}
    all_state_xs, all_state_ys = project_borders(us_states_dat, state_list=state_list)

    if background_map:
        canvas.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))

    canvas.patches(
        "xs",
        "ys",
        source=ColumnDataSource(
            {
                "xs": all_state_xs,
                "ys": all_state_ys,
                "state_color": ["white"] * len(state_list),
                "state_name": list(state_list),
            }
        ),
        fill_color="state_color",
        line_color=line_color,
        fill_alpha=fill_alpha,
        line_width=line_width,
        name="states",
    )

    return canvas


def add_state_tooltips(canvas, tooltip_title, state2label):
    """Add tooltip to states.

    :param bokeh.plotting.figure canvas: canvas.
    :param dict state2label: keys are states abbreviation and values are labels.
    :return: (*bokeh.plotting.figure.Figure*) -- canvas with toolips.
    """
    if not isinstance(tooltip_title, str):
        raise TypeError("tooltip title must be a str")

    patches = canvas.select_one({"name": "states"})
    patches = expand_data_source(patches, state2label, "state_label")

    hover = HoverTool(
        tooltips=[("State", "@state_name"), (f"{tooltip_title}", "@state_label")],
        renderers=[patches],
    )
    canvas.add_tools(hover)

    return canvas


def add_state_colors(canvas, state2color):
    """Color states.

    :param bokeh.plotting.figure canvas: canvas.
    :param dict state2color: keys are states abbreviation and values are colors.
    :return: (*bokeh.plotting.figure.Figure*) -- canvas with colored state.
    """
    patches = canvas.select_one({"name": "states"})
    patches = expand_data_source(patches, state2color, "state_color")

    return canvas


def add_state_legends(
    canvas,
    state2label=None,
    title=None,
    location="bottom_right",
    title_size="12pt",
    label_size="12pt",
):
    """Add legend.

    :param bokeh.plotting.figure canvas: canvas.
    :param dict state2label: keys are states abbreviation and values are labels.
    :param str title: title for legend.
    :param str location: legend location on canvas. Default is bottom right.
    :param str title_size: legend title font size. Default is 12pt.
    :param str label_size: legend labels font size. Default is 12pt.
    :return: (*bokeh.plotting.figure.Figure*) -- canvas with colored state.
    :raises TypeError:
        if ``title`` is not None or str.
        if ``location`` is not a str.
        if ``title_size`` is not a str.
        if ``label_size`` is not a str.
    """
    if title is not None and not isinstance(title, str):
        raise TypeError("title must be a str")
    if location is not None and not isinstance(location, str):
        raise TypeError("location must be a str")
    if title_size is not None and not isinstance(title_size, str):
        raise TypeError("title_size must be a str")
    if label_size is not None and not isinstance(label_size, str):
        raise TypeError("label_size must be a str")

    patches = canvas.select_one({"name": "states"})
    patches = expand_data_source(patches, state2label, "state_legend")

    group_legend = (
        pd.DataFrame({"legend": patches.data_source.data["state_legend"]})
        .groupby(["legend"])
        .groups
    )

    legend = Legend(
        items=[
            LegendItem(index=i[0], label=l, renderers=[patches])
            for l, i in group_legend.items()
        ]
    )
    canvas.add_layout(legend)

    if title is not None:
        canvas.legend.title = title
    canvas.legend.location = location
    canvas.legend.label_text_font_size = label_size
    canvas.legend.title_text_font_size = title_size

    return canvas


def plot_states(
    figsize=(1400, 800),
    state_borders_kwargs=None,
    state_colors_args=None,
    state_tooltips_args=None,
    state_legends_kwargs=None,
):
    """Add states on canvas and optionally add colors, tooltips and legends.

    :param tuple figsize: size of the bokeh figure (in pixels).
    :param dict state_borders_kwargs: keyword argument(s) to be passed to
        :func:`postreise.add_state_borders`.
    :param dict state_colors_args: arguments to be passed to
        :func:`postreise.add_state_colors`.
    :param dict state_tooltips_args: argument(s) to be passed to
        :func:`postreise.add_state_tooltips`.
    :param dict state_legends_kwargs: keyword argument(s) to be passed to
        :func:`postreise.add_state_legends`.
    :raises TypeError:
        if ``state_borders_kwargs`` is not None or dict.
        if ``state_colors_args`` is not None or dict.
        if ``state_tooltips_args`` is not None or dict.
        if ``state_legends_kwargs`` is not None or dict.
    :return: (*bokeh.plotting.figure.Figure*) -- map of us states.
    """
    for label in [
        "state_borders_kwargs",
        "state_colors_args",
        "state_tooltips_args",
        "state_legends_kwargs",
    ]:
        var = eval(label)
        if var is not None and not isinstance(var, dict):
            raise TypeError(f"{label} must be a dict")

    # create canvas
    canvas = create_map_canvas(figsize)

    # add state borders
    if state_borders_kwargs is not None:
        _check_func_kwargs(
            add_state_borders, set(state_borders_kwargs), "state_borders_kwargs"
        )
        canvas = add_state_borders(canvas, **state_borders_kwargs)
    else:
        canvas = add_state_borders(canvas)

    if state_colors_args is not None:
        canvas = add_state_colors(canvas, state_colors_args)

    if state_tooltips_args is not None:
        canvas = add_state_tooltips(
            canvas, state_tooltips_args["title"], state_tooltips_args["label"]
        )

    if state_legends_kwargs is not None:
        _check_func_kwargs(
            add_state_legends, set(state_legends_kwargs), "state_legends_kwargs"
        )
        canvas = add_state_legends(canvas, **state_legends_kwargs)

    return canvas
