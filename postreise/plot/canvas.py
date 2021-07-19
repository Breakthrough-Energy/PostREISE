from bokeh.plotting import figure


def create_map_canvas(figsize=None, x_range=None, y_range=None):
    """Create canvas for maps.

    :param tuple figsize: size of the bokeh figure (in pixels).
    :param tuple x_range: x range to zoom plot to (EPSG:3857).
    :param tuple y_range: y range to zoom plot to (EPSG:3857).
    :return: (*bokeh.plotting.figure*) -- empty canvas.
    :raises TypeError:
        if ``figsize`` is not a tuple and elements are not int.
        if ``x_range`` or``y_range`` are not tuple and elements are not int/float.
    :raises ValueError:
        if ``figsize``, ``x_range`` or``y_range`` don't have exactly two elements.
        if elements of ``figsize`` are negative.
        if first element of ``x_range`` or``y_range`` is greater than the second one.
    """
    if figsize is None:
        figsize = (1400, 800)

    for label in ["figsize", "x_range", "y_range"]:
        var = eval(label)
        if var is not None:
            if not isinstance(var, tuple):
                raise TypeError(f"{label} must be a tuple")
            if len(var) != 2:
                raise ValueError(f"{label} must have two elements")
            for i in var:
                if label == "figsize":
                    if not isinstance(i, int):
                        raise TypeError(f"all elements of {label} must be int")
                    if i < 0:
                        raise ValueError(f"all elements of {label} must be positive")
                else:
                    if not isinstance(i, (int, float)):
                        raise TypeError(f"all elements of {label} must be int or float")
            if label != "figsize":
                if var[0] >= var[1]:
                    raise ValueError(f"{label}: 1st element must be lower than 2nd")

    canvas = figure(
        tools="pan,wheel_zoom,reset,save",
        x_axis_location=None,
        y_axis_location=None,
        plot_width=figsize[0],
        plot_height=figsize[1],
        output_backend="webgl",
        sizing_mode="scale_both",
        match_aspect=True,
        x_range=x_range,
        y_range=y_range,
    )
    canvas.xgrid.visible = False
    canvas.ygrid.visible = False

    return canvas
