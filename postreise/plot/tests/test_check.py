import pytest

from postreise.plot.check import _check_func_kwargs, _get_func_kwargs


def test_get_func_kwargs_error():
    with pytest.raises(TypeError):
        _get_func_kwargs("dummy")


def test_get_func_kwargs():
    assert _get_func_kwargs(lambda: True) is None
    assert _get_func_kwargs(lambda x: x) is None
    assert set(_get_func_kwargs(lambda a=1, b=2, c=3: True)) == set(["a", "b", "c"])
    assert set(_get_func_kwargs(lambda x, a=1, b=2, c=3: True)) == set(["a", "b", "c"])


def test_check_func_kwargs_errors():
    def func(a=1, b=2, c=3):
        return a + b + c

    arg = (
        ("a", "dummy"),
        (["a"], ["dummy"]),
        ([1, "b", "c"], "dummy"),
        ({"d", "e"}, "dummy"),
    )
    for a in arg:
        with pytest.raises(TypeError):
            assert _check_func_kwargs(func, a[0], a[1])


def test_check_func_kwargs():
    def func(a=1, b=2, c=3):
        return a * b * c

    assert _check_func_kwargs(func, ["a", "b"], "dummy") is None
    assert _check_func_kwargs(func, ["a", "b", "c"], "dummy") is None
