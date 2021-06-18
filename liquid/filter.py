"""Filter function helpers."""

from __future__ import annotations

import collections.abc
import warnings

from abc import ABC, abstractmethod
from functools import wraps

from typing import Tuple
from typing import Any
from typing import Callable
from typing import Union
from typing import Optional
from typing import TYPE_CHECKING

from liquid.context import Undefined

from liquid.exceptions import FilterArgumentError
from liquid.exceptions import FilterValueError

if TYPE_CHECKING:
    from liquid import Environment

    FilterT = Callable[..., Any]
    N = Union[float, int]


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
        if not isinstance(val, (list, tuple, Undefined)):
            raise FilterValueError(f"expected an array, found {type(val).__name__}")

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
        return int(val)
    except ValueError as err:
        if default is not None:
            return default
        raise FilterArgumentError(
            f"expected an int or string, found {type(val).__name__}"
        ) from err


def num_arg(val: Any, default: Optional[N] = None) -> N:
    """Return the ``val`` as an int or float. If ``val`` can't be cast to an
    int or float, return ``default`."""
    if isinstance(val, (int, float)):
        return val

    if isinstance(val, str):
        if val.isdecimal():
            return int(val)

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
    """A filter function that raises a FilterArgumentError if the filter value is not
    a number."""

    @wraps(_filter)
    def wrapper(val: object, *args: Any, **kwargs: Any) -> Any:
        val = num_arg(val, default=0)

        try:
            return _filter(val, *args, **kwargs)
        except TypeError as err:
            raise FilterArgumentError(err) from err

    return wrapper


# NOTE: Everything from here on is depreciated and will be removed in Liquid 0.9.


class Filter(ABC):
    """Base class for all filters.

    If with_context is True, the current render context will be passed as a
    keyword argument every time the filter is called.
    """

    __slots__ = ("env",)

    with_context: bool = False
    name: str = "filter"

    def __init__(self, env: Environment):
        warnings.warn(
            "class-based filters are depreciated in favour of decorated functions. "
            ":class:`liquid.filter.Filter` will be removed in Liquid 0.9",
            DeprecationWarning,
            stacklevel=2,
        )

        self.env = env

    @abstractmethod
    def __call__(self, *args, **kwargs):  # type: ignore
        """Call the filter where `val` is the left hand expression of an output
        statement."""


def expect_number(name: str, val: object) -> N:
    """Return `val` as an integer or float. Raise a FilterArgumentError
    if `val` can't be cast to an integer or float."""
    if isinstance(val, (int, float)):
        num = val
    elif isinstance(val, str):
        if val.isdecimal():
            num = int(val)
        try:
            num = float(val)
        except ValueError as err:
            raise FilterArgumentError(
                f"{name}: could not cast string '{val}' to a number"
            ) from err
    else:
        raise FilterArgumentError(
            f"expected an int, float or string, found {type(val).__name__}"
        )
    return num


def expect_integer(name: str, val: object) -> int:
    """Return `val` as an integer. Raise a FilterArgumentError if `val` can't
    be cast to an integer."""
    if isinstance(val, int):
        num = val
    elif isinstance(val, str):
        if val.isdecimal():
            num = int(val)
        else:
            raise FilterArgumentError(
                f"{name}: could not cast string '{val}' to an integer"
            )
    else:
        raise FilterArgumentError(
            f"expected an int or string, found {type(val).__name__}"
        )
    return num


def expect_string(name: str, val: object) -> None:
    """Raise a FilterArgumentError is val is not a string."""
    if not isinstance(val, str):
        raise FilterArgumentError(f"{name}: expected a string, found {type(val)}")


def expect_string_or_array(name: str, val: object) -> None:
    """Raise a FilterArgumentError is val is not a string or a list."""
    if not isinstance(val, (str, list)):
        raise FilterArgumentError(
            f"{name}: expected a string or array, found {type(val)}"
        )


def expect_n_args(name: str, n: int, args: Any, kwargs: Any) -> None:
    """Raise a FilterArgumentError if args does not have `n` elements, and
    kwargs is not empty."""
    length = len(args)
    if length != n:
        raise FilterArgumentError(
            f"{name} expects a one positional argument, found {length}"
        )
    if kwargs:
        raise FilterArgumentError(
            f"{name}: expected zero keyword arguments, found {len(kwargs)}"
        )


def expect_one_arg(name: str, args: Any, kwargs: Any) -> None:
    """Raise a FilterArgumentError if args is not a single element tuple, and
    kwargs is not empty."""
    expect_n_args(name, 1, args, kwargs)


def maybe_one_arg(name: str, args: Any, kwargs: Any) -> bool:
    """Raise a FilterArgumentError if args is not empty or a single element tuple,
    and kwargs is not empty."""
    if kwargs:
        raise FilterArgumentError(
            f"{name}: expected zero keyword arguments, found {len(kwargs)}"
        )

    length = len(args)
    if length == 1:
        return True
    if length == 0:
        return False

    raise FilterArgumentError(
        f"{name}: expected zero or one positional arguments, found {length}"
    )


def one_maybe_two_args(name: str, args: Any, kwargs: Any) -> Tuple[Any, ...]:
    """Return (args[0], args[1]) or None if the args aren't there."""
    if kwargs:
        raise FilterArgumentError(
            f"{name}: expected zero keyword arguments, found {len(kwargs)}"
        )

    length = len(args)
    if length == 2:
        return args[0], args[1]
    if length == 1:
        return args[0], None

    raise FilterArgumentError(
        f"{name}: expected one or two positional arguments, found {length}"
    )


def expect_no_args(name: str, args: Any, kwargs: Any) -> None:
    """Raise a FilterArgumentError if args and kwargs are not empty."""
    if args:
        raise FilterArgumentError(
            f"{name}: expected zero positional arguments, found {len(args)}"
        )
    if kwargs:
        raise FilterArgumentError(
            f"{name}: expected zero keyword arguments, found {len(kwargs)}"
        )


def expect_array(name: str, val: object) -> None:
    """Raise a FilterArgumentError is val is not an array/list."""
    if not isinstance(val, (list, tuple)):
        raise FilterArgumentError(f"{name}: expected an array, found {type(val)}")


def array_required(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        expect_array(instance.name, val)
        return func(instance, val, *args, **kwargs)

    return wrapper


def array_or_string_required(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        expect_string_or_array(instance.name, val)
        return func(instance, val, *args, **kwargs)

    return wrapper


def array_of_strings_required(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        expect_array(instance.name, val)
        for item in val:
            if not isinstance(item, str):
                raise FilterArgumentError(
                    f"{instance.name}: expected an array of strings, "
                    f"found a {type(item)}"
                )
        return func(instance, val, *args, **kwargs)

    return wrapper


def array_of_hashable_required(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        expect_array(instance.name, val)
        for item in val:
            if not isinstance(item, collections.abc.Hashable):
                raise FilterArgumentError(
                    f"{instance.name}: expected an array of hashable items, "
                    f"found a {type(item)}"
                )
        return func(instance, val, *args, **kwargs)

    return wrapper


def string_required(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        expect_string(instance.name, val)
        return func(instance, val, *args, **kwargs)

    return wrapper


def number_required(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        num = expect_number(instance.name, val)
        return func(instance, num, *args, **kwargs)

    return wrapper


def one_arg_required(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        expect_one_arg(instance.name, args, kwargs)
        return func(instance, val, args[0], **kwargs)

    return wrapper


def maybe_one_arg_required(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        maybe_one_arg(instance.name, args, kwargs)
        return func(instance, val, *args, **kwargs)

    return wrapper


def one_maybe_two_args_required(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        one_maybe_two_args(instance.name, args, kwargs)
        return func(instance, val, *args, **kwargs)

    return wrapper


def one_array_arg_required(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        expect_one_arg(instance.name, args, kwargs)
        expect_array(instance.name, args[0])
        return func(instance, val, args[0], **kwargs)

    return wrapper


def one_number_arg_required(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        expect_one_arg(instance.name, args, kwargs)
        num = expect_number(instance.name, args[0])
        return func(instance, val, num, **kwargs)

    return wrapper


def one_string_arg_required(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        expect_one_arg(instance.name, args, kwargs)
        expect_string(instance.name, args[0])
        return func(instance, val, args[0], **kwargs)

    return wrapper


def two_string_args_required(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        expect_n_args(instance.name, 2, args, kwargs)
        expect_string(instance.name, args[0])
        expect_string(instance.name, args[1])
        return func(instance, val, args[0], args[1], **kwargs)

    return wrapper


def no_args(func):  # type: ignore
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):  # type: ignore
        expect_no_args(instance.name, args, kwargs)
        return func(instance, val, *args, **kwargs)

    return wrapper
