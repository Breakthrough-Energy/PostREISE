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


class BorderPlotter:
    json_filename = None
    url_base = None
    bokeh_borders = None
    area_type = None

    @classmethod
    def download_borders_json(cls):
        """Downloads json file containing coordinates for borders.

        :return: (*str*) -- path to json file.
        """
        shapes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shapes")
        os.makedirs(shapes_path, exist_ok=True)
        filepath = os.path.join(shapes_path, cls.json_filename)
        if not os.path.isfile(filepath):
            r = urllib.request.urlopen(f"{cls.url_base}{cls.json_filename}")
            with open(filepath, "wb") as f:
                f.write(r.read())
        return filepath

    @classmethod
    def get_borders(cls):
        """Get borders as a dictionary of coordinate arrays.

        :return: (*dict*) -- dictionary with keys from the specified shapefile column,
            values are dict with keys of {"lat", "lon"}, values are coordinates, padded by
            nan values to indicate the end of each polygon before the start of the next one.
        """
        try:
            json_filepath = cls.download_borders_json()
            with open(json_filepath, "r") as f:
                borders_dat = json.load(f)
        except Exception:
            # In case we can't get the json file, use the bokeh shapes
            borders_dat = cls.bokeh_borders
        return borders_dat

    @classmethod
    def expand_data_source(cls, patches, area2data, key_name):
        """Add data to a bokeh patch object

        :param bokeh.models.renderers.GlyphRenderer patches: areas as glyphs.
        :param dict area2data: keys are area name abbreviations and values are data.
        :param str key_name: name to use for the key in data source.
        :return: (*bokeh.models.renderers.GlyphRenderer*) -- updated patches.
        :raises TypeError:
            if ``area2data`` is not a dict.
            if ``key_name`` is not a str.
        :raises ValueError:
            if areas in ``area2data`` and  ``patches`` differ.
        """
        if not isinstance(area2data, dict):
            raise TypeError("area2data must be a dict")
        if not isinstance(key_name, str):
            raise TypeError("key_name must be a str")

        if len(set(patches.data_source.data["area_name"]) - set(area2data.keys())) != 0:
            raise ValueError("areas in patches are missing from area2data")

        patches.data_source.data[key_name] = [
            area2data[s] for s in patches.data_source.data["area_name"]
        ]
        return patches

    @classmethod
    def get_area_set(borders_dat):
        """Get set of abbreviated area names

        :param dict borders_dat: dictionary with keys from the specified shapefile column,
            values are dict with keys of {"lat", "lon"}, values are coordinates, padded by
            nan values to indicate the end of each polygon before the start of the next one.
        :return: (*set*) Set of abbreviated area names
        """
        return set(borders_dat.keys())

    @classmethod
    def add_borders(
        cls,
        canvas,
        area_list=None,
        background_map=False,
        line_color="grey",
        line_width=1,
        fill_alpha=1,
    ):
        """Add borders onto canvas.

        :param bokeh.plotting.figure canvas: canvas.
        :param list area_list: list of areas to display
        :param bool background_map: add background behind borders.
        :param str line_color: color of outlines.
        :param int/float line_width: thickness of outlines.
        :param int/float fill_alpha: opaqueness for patches.
        :return: (*bokeh.plotting.figure.Figure*) -- canvas with borders.
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

        borders_dat = cls.get_borders()
        if area_list is None:
            area_list = cls.get_area_set(borders_dat)
        all_border_xs, all_border_ys = project_borders(
            borders_dat, state_list=area_list
        )

        if background_map:
            canvas.add_tile(get_provider(Vendors.CARTODBPOSITRON_RETINA))

        canvas.patches(
            "xs",
            "ys",
            source=ColumnDataSource(
                {
                    "xs": all_border_xs,
                    "ys": all_border_ys,
                    "area_color": ["white"] * len(area_list),
                    "area_name": list(area_list),
                }
            ),
            fill_color="area_color",
            line_color=line_color,
            fill_alpha=fill_alpha,
            line_width=line_width,
            name="areas",
        )

        return canvas

    @classmethod
    def add_tooltips(cls, canvas, tooltip_title, area2label):
        """Add tooltip to areas.

        :param bokeh.plotting.figure canvas: canvas.
        :param dict area2label: keys are area name abbreviations and values are labels.
        :return: (*bokeh.plotting.figure.Figure*) -- canvas with toolips.
        """
        if not isinstance(tooltip_title, str):
            raise TypeError("tooltip title must be a str")

        patches = canvas.select_one({"name": "areas"})
        patches = cls.expand_data_source(patches, area2label, "area_label")

        hover = HoverTool(
            tooltips=[
                (cls.area_type, "@area_name"),
                (f"{tooltip_title}", "@area_label"),
            ],
            renderers=[patches],
        )
        canvas.add_tools(hover)

        return canvas

    @classmethod
    def add_area_colors(cls, canvas, area2color):
        """Color areas.

        :param bokeh.plotting.figure canvas: canvas.
        :param dict area2color: keys are area name abbreviations and values are colors.
        :return: (*bokeh.plotting.figure.Figure*) -- canvas with colored area.
        """
        patches = canvas.select_one({"name": "areas"})
        patches = cls.expand_data_source(patches, area2color, "area_color")

        return canvas

    @classmethod
    def add_area_legends(
        cls,
        canvas,
        area2label=None,
        title=None,
        location="bottom_right",
        title_size="12pt",
        label_size="12pt",
    ):
        """Add legend.

        :param bokeh.plotting.figure canvas: canvas.
        :param dict area2label: keys are area name abbreviations and values are labels.
        :param str title: title for legend.
        :param str location: legend location on canvas. Default is bottom right.
        :param str title_size: legend title font size. Default is 12pt.
        :param str label_size: legend labels font size. Default is 12pt.
        :return: (*bokeh.plotting.figure.Figure*) -- canvas with colored area.
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

        patches = canvas.select_one({"name": "areas"})
        patches = cls.expand_data_source(patches, area2label, "area_legend")

        group_legend = (
            pd.DataFrame({"legend": patches.data_source.data["area_legend"]})
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

    @classmethod
    def plot_borders(
        cls,
        figsize=(1400, 800),
        borders_kwargs=None,
        area_colors_args=None,
        area_tooltips_args=None,
        area_legends_kwargs=None,
    ):
        """Add borders on canvas and optionally add colors, tooltips and legends.

        :param tuple figsize: size of the bokeh figure (in pixels).
        :param dict borders_kwargs: keyword argument(s) to be passed to
            :func:`postreise.add_borders`.
        :param dict area_colors_args: arguments to be passed to
            :func:`postreise.add_area_colors`.
        :param dict area_tooltips_args: argument(s) to be passed to
            :func:`postreise.add_tooltips`.
        :param dict area_legends_kwargs: keyword argument(s) to be passed to
            :func:`postreise.add_area_legends`.
        :raises TypeError:
            if ``borders_kwargs`` is not None or dict.
            if ``area_colors_args`` is not None or dict.
            if ``area_tooltips_args`` is not None or dict.
            if ``area_legends_kwargs`` is not None or dict.
        :return: (*bokeh.plotting.figure.Figure*) -- map of area borders.
        """
        for label in [
            "borders_kwargs",
            "area_colors_args",
            "area_tooltips_args",
            "area_legends_kwargs",
        ]:
            var = eval(label)
            if var is not None and not isinstance(var, dict):
                raise TypeError(f"{label} must be a dict")

        # create canvas
        canvas = create_map_canvas(figsize)

        # add borders
        if borders_kwargs is not None:
            _check_func_kwargs(cls.add_borders, set(borders_kwargs), "borders_kwargs")
            canvas = cls.add_borders(canvas, **borders_kwargs)
        else:
            canvas = cls.add_borders(canvas)

        if area_colors_args is not None:
            canvas = cls.add_area_colors(canvas, area_colors_args)

        if area_tooltips_args is not None:
            canvas = cls.add_tooltips(
                canvas, area_tooltips_args["title"], area_tooltips_args["label"]
            )

        if area_legends_kwargs is not None:
            _check_func_kwargs(
                cls.add_area_legends, set(area_legends_kwargs), "area_legends_kwargs"
            )
            canvas = cls.add_area_legends(canvas, **area_legends_kwargs)

        return canvas


class StatesBorderPlotter(BorderPlotter):
    json_filename = "state_shapes.json"
    url_base = "https://besciences.blob.core.windows.net/us-shapefiles/"
    bokeh_borders = us_states.data
    area_type = "State"

    @classmethod
    def get_area_set(cls, borders_dat):
        """Get set of abbreviated area names

        :param dict borders_dat: dictionary with keys from the specified shapefile column,
            values are dict with keys of {"lat", "lon"}, values are coordinates, padded by
            nan values to indicate the end of each polygon before the start of the next one.
        :return: (*set*) Set of abbreviated area names
        """
        return set(borders_dat.keys()) - {"AK", "HI", "DC", "PR"}


class EuropeBorderPlotter(BorderPlotter):
    json_filename = "continental_europe_country_borders.json"
    url_base = "https://besciences.blob.core.windows.net/shapefiles/EUROPE/continental_europe_country_borders/"
    # There is no bokeh sample data for Europe
    bokeh_borders = {}
    area_type = "Country"

    @classmethod
    def get_area_set(cls, borders_dat):
        """Get set of abbreviated area names

        :param dict borders_dat: dictionary with keys from the specified shapefile column,
            values are dict with keys of {"lat", "lon"}, values are coordinates, padded by
            nan values to indicate the end of each polygon before the start of the next one.
        :return: (*set*) Set of abbreviated area names
        """
        return set(borders_dat.keys()) - {"TR"}


def add_borders(grid_model, canvas, borders_kwargs=None):
    """Calls add_borders for either StatesBorderPlotter or EuropeBorderPlotter
        based on grid model

    :param str grid_model: the grid model, either usa_tamu or europe_tub
    :param bokeh.plotting.figure canvas: canvas.
    :param dict borders_kwargs: keyword arguments to be passed to
        :func:`postreise.plot.plot_borders.add_borders`
    :raises ValueError:
        if grid model is not supported.
    :return: (*bokeh.plotting.figure.Figure*) -- canvas with borders.
    """
    if grid_model == "usa_tamu":
        return StatesBorderPlotter.add_borders(canvas, **borders_kwargs)
    elif grid_model == "europe_tub":
        return EuropeBorderPlotter.add_borders(canvas, **borders_kwargs)
    else:
        raise ValueError("grid model is not supported")


def add_tooltips(grid_model, canvas, tooltip_title, area2label):
    """Calls add_tooltips for either StatesBorderPlotter or EuropeBorderPlotter
        based on grid model

    :param str grid_model: the grid model, either usa_tamu or europe_tub
    :param bokeh.plotting.figure canvas: canvas.
    :param str tooltip_title: title to be added to tooltips
    :param dict area2label: keys are area name abbreviations and values are labels.
    :raises ValueError:
        if grid model is not supported.
    :return: (*bokeh.plotting.figure.Figure*) -- canvas with tooltips.
    """
    if grid_model == "usa_tamu":
        return StatesBorderPlotter.add_tooltips(canvas, tooltip_title, area2label)
    elif grid_model == "europe_tub":
        # TODO: tooltips currently broken for europe because shapefile
        # countries do not line up with europe grid data
        return canvas
    else:
        raise ValueError("grid model is not supported")
