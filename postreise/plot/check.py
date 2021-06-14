import types
from inspect import getfullargspec


def _get_func_kwargs(func):
    """Get keyword arguments of a function.

    :param function func: function to get keyword arguments from.
    :return: (*list*) -- keyword arguments of the function.
    :raises TypeError: if ``func`` is not a function
    """
    if not isinstance(func, types.FunctionType):
        raise TypeError("func must be a function")

    argspec = getfullargspec(func)

    return None if argspec.defaults is None else argspec.args[-len(argspec.defaults) :]


def _check_func_kwargs(func, kwargs, name):
    """Ensure that only valid keyword arguments are passed to a function.

    :param function func: function to test.
    :param iterable kwargs: keyword arguments.
    :param str name: name of variable enclosing keyword arguments.
    :raises TypeError:
        if ``kwargs`` is not an iterable.
        if ``name`` is not a str.
        if ``kwargs`` are invalid keyword arguments of ``func``.
        if elements of ``kwargs`` are not str.
    """
    if not isinstance(kwargs, (list, set, tuple)):
        raise TypeError("kwargs must be an iterable")
    for e in kwargs:
        if not isinstance(e, str):
            raise TypeError("elements of kwargs must be a str")
    if not isinstance(name, str):
        raise TypeError("name must be a str")

    valid_kwargs = set(_get_func_kwargs(func))
    invalid_kwargs = set(kwargs) - valid_kwargs
    if len(invalid_kwargs) != 0:
        raise TypeError(
            "invalid entry in '%s': %s \n"
            "valid keyword arguments of %s(): %s"
            % (
                name,
                " | ".join(invalid_kwargs),
                func.__name__,
                " | ".join(valid_kwargs),
            )
        )
