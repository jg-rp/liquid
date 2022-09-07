"""Filter function helpers."""

from __future__ import annotations

from functools import wraps

from typing import Any
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Union
from typing import Optional
from typing import TYPE_CHECKING

from liquid.context import Undefined

from liquid.exceptions import FilterArgumentError
from liquid.exceptions import FilterValueError

from liquid.limits import to_int

if TYPE_CHECKING:  # pragma: no cover
    FilterT = Callable[..., Any]
    NumberT = Union[float, int]


def with_context(_filter: FilterT) -> FilterT:
    """Pass the active :class:`liquid.context.Context` as the named argument
    ``context`` to the decorated filter function.

    :param _filter: The filter function to decorate.
    :type _filter: Callable[..., Any]
    """
    _filter.with_context = True  # type: ignore
    return _filter


def with_environment(_filter: FilterT) -> FilterT:
    """Pass the active :class:`liquid.Environment` as the named argument
    ``environment`` to the decorated filter function.

    :param _filter: The filter function to decorate.
    :type _filter: Callable[..., Any]
    """
    _filter.with_environment = True  # type: ignore
    return _filter


def string_filter(_filter: FilterT) -> FilterT:
    """A filter function decorator that converts the first positional argument to a
    string."""

    @wraps(_filter)
    def wrapper(val: object, *args: Any, **kwargs: Any) -> Any:
        if not isinstance(val, str):
            val = str(val)
        try:
            return _filter(val, *args, **kwargs)
        except TypeError as err:
            raise FilterArgumentError(err) from err

    return wrapper


def array_filter(_filter: FilterT) -> FilterT:
    """A filter function decorator that raises a FilterValueError if the filter value
    is not array-like."""

    @wraps(_filter)
    def wrapper(val: object, *args: Any, **kwargs: Any) -> Any:
        if not isinstance(val, (list, tuple, Undefined, range)):
            raise FilterValueError(f"expected an array, found {type(val).__name__}")

        try:
            return _filter(val, *args, **kwargs)
        except TypeError as err:
            raise FilterArgumentError(err) from err

    return wrapper


def sequence_filter(_filter: FilterT) -> FilterT:
    """A filter function decorator that raises a FilterValueError if the filter value
    can not be coerced into an array-like object.

    This is intended to mimic the semantics of the reference implementation's
    ``InputIterator`` class.
    """

    @wraps(_filter)
    def wrapper(val: object, *args: Any, **kwargs: Any) -> Any:
        if isinstance(val, (list, tuple)):
            val = flatten(val)
        elif isinstance(val, (dict, str)) or not isinstance(val, Iterable):
            val = [val]

        try:
            return _filter(val, *args, **kwargs)
        except TypeError as err:
            raise FilterArgumentError(err) from err

    return wrapper


def liquid_filter(_filter: FilterT) -> FilterT:
    """A filter function decorator that wraps `TypeError` in `FilterArgumentError`."""

    @wraps(_filter)
    def wrapper(val: object, *args: Any, **kwargs: Any) -> Any:
        try:
            return _filter(val, *args, **kwargs)
        except TypeError as err:
            raise FilterArgumentError(err) from err

    return wrapper


def int_arg(val: Any, default: Optional[int] = None) -> int:
    """Return the ``val`` as an int or ``default`` if ``val`` can't be cast to an
    int."""
    try:
        return to_int(val)
    except ValueError as err:
        if default is not None:
            return default
        raise FilterArgumentError(
            f"expected an int or string, found {type(val).__name__}"
        ) from err


def num_arg(val: Any, default: Optional[NumberT] = None) -> NumberT:
    """Return the ``val`` as an int or float. If ``val`` can't be cast to an
    int or float, return ``default`."""
    if isinstance(val, (int, float)):
        return val

    if isinstance(val, str):
        try:
            return to_int(val)
        except ValueError:
            pass

        try:
            return float(val)
        except ValueError as err:
            if default is not None:
                return default
            raise FilterArgumentError(
                f"could not cast string '{val}' to a number"
            ) from err

    elif default is not None:
        return default

    raise FilterArgumentError(
        f"expected an int, float or string, found {type(val).__name__}"
    )


def math_filter(_filter: FilterT) -> FilterT:
    """A filter function decorator that raises a FilterArgumentError if the filter value
    is not a number."""

    @wraps(_filter)
    def wrapper(val: object, *args: Any, **kwargs: Any) -> Any:
        val = num_arg(val, default=0)

        try:
            return _filter(val, *args, **kwargs)
        except TypeError as err:
            raise FilterArgumentError(err) from err

    return wrapper


def flatten(it: Iterable[Any], level: int = 5) -> List[object]:
    """Flatten nested "liquid arrays" into a list."""

    def _flatten(it: Iterable[Any], level: int = 5) -> Iterator[object]:
        for obj in it:
            if not level or not isinstance(obj, (list, tuple)):
                yield obj
            else:
                yield from _flatten(obj, level=level - 1)

    return list(_flatten(it, level))
