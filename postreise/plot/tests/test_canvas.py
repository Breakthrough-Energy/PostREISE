import bokeh.plotting as plt
import pytest

from postreise.plot.canvas import create_map_canvas


def test_create_map_canvas_argument_type():
    with pytest.raises(TypeError) as excinfo:
        create_map_canvas(figsize=[1400, 800])
    assert "figsize must be a tuple" in str(excinfo.value)


def test_create_map_canvas_argument_size():
    with pytest.raises(ValueError) as excinfo:
        create_map_canvas(x_range=(1, 2, 3))
    assert "x_range must have two elements" in str(excinfo.value)


def test_create_map_canvas_figsize():
    with pytest.raises(TypeError) as excinfo:
        create_map_canvas(figsize=(1400.1, 800))
    assert "all elements of figsize must be int" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        create_map_canvas(figsize=(1400, -800))
    assert "all elements of figsize must be positive" in str(excinfo.value)


def test_create_map_canvas_range():
    with pytest.raises(TypeError) as excinfo:
        create_map_canvas(y_range=(-1, "1"))
    assert "all elements of y_range must be int or float" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        create_map_canvas(y_range=(100, -100))
    assert "y_range: 1st element must be lower than 2nd" in str(excinfo.value)


def test_create_map_canvas():
    canvas = create_map_canvas(
        figsize=(1200, 600), x_range=(-100, 100), y_range=(-10, 10)
    )
    assert isinstance(canvas, plt.Figure) is True
