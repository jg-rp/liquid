"""Filter function helpers."""

from __future__ import annotations

import collections.abc

from abc import ABC, abstractmethod
from functools import wraps

from typing import Tuple
from typing import Any
from typing import TYPE_CHECKING

from liquid.exceptions import FilterArgumentError

if TYPE_CHECKING:
    from liquid import Environment


class Filter(ABC):
    """Base class for all filters.

    If with_context is True, the current render context will be passed as a
    keyword argument every time the filter is called.
    """

    __slots__ = ("env",)

    with_context: bool = False
    name: str = "filter"

    def __init__(self, env: Environment):
        self.env = env

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """Call the filter where `val` is the left hand expression of an output
        statement."""


def expect_number(name: str, val: object):
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
            f"expected an int, float or string, found {type(val)}"
        )
    return num


def expect_integer(name: str, val: object):
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
        raise FilterArgumentError(f"expected an int or string, found {type(val)}")
    return num


def expect_string(name: str, val: object):
    """Raise a FilterArgumentError is val is not a string."""
    if not isinstance(val, str):
        raise FilterArgumentError(f"{name}: expected a string, found {type(val)}")


def expect_string_or_array(name: str, val: object):
    """Raise a FilterArgumentError is val is not a string or a list."""
    if not isinstance(val, (str, list)):
        raise FilterArgumentError(
            f"{name}: expected a string or array, found {type(val)}"
        )


def expect_n_args(name: str, n: int, args: ..., kwargs: ...):
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


def expect_one_arg(name: str, args: ..., kwargs: ...):
    """Raise a FilterArgumentError if args is not a single element tuple, and
    kwargs is not empty."""
    expect_n_args(name, 1, args, kwargs)


def maybe_one_arg(name: str, args: ..., kwargs: ...):
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


def one_maybe_two_args(name: str, args: ..., kwargs: ...) -> Tuple[Any, ...]:
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


def expect_no_args(name: str, args: ..., kwargs: ...):
    """Raise a FilterArgumentError if args and kwargs are not empty."""
    if args:
        raise FilterArgumentError(
            f"{name}: expected zero positional arguments, found {len(args)}"
        )
    if kwargs:
        raise FilterArgumentError(
            f"{name}: expected zero keyword arguments, found {len(kwargs)}"
        )


def expect_array(name: str, val: object):
    """Raise a FilterArgumentError is val is not an array/list."""
    if not isinstance(val, (list, tuple)):
        raise FilterArgumentError(f"{name}: expected an array, found {type(val)}")


def array_required(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        expect_array(instance.name, val)
        return func(instance, val, *args, **kwargs)

    return wrapper


def array_or_string_required(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        expect_string_or_array(instance.name, val)
        return func(instance, val, *args, **kwargs)

    return wrapper


def array_of_strings_required(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        expect_array(instance.name, val)
        for item in val:
            if not isinstance(item, str):
                raise FilterArgumentError(
                    f"{instance.name}: expected an array of strings, found a {type(item)}"
                )
        return func(instance, val, *args, **kwargs)

    return wrapper


def array_of_hashable_required(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        expect_array(instance.name, val)
        for item in val:
            if not isinstance(item, collections.abc.Hashable):
                raise FilterArgumentError(
                    f"{instance.name}: expected an array of hashable items, "
                    f"found a {type(item)}"
                )
        return func(instance, val, *args, **kwargs)

    return wrapper


def string_required(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        expect_string(instance.name, val)
        return func(instance, val, *args, **kwargs)

    return wrapper


def number_required(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        num = expect_number(instance.name, val)
        return func(instance, num, *args, **kwargs)

    return wrapper


def one_arg_required(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        expect_one_arg(instance.name, args, kwargs)
        return func(instance, val, args[0], **kwargs)

    return wrapper


def maybe_one_arg_required(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        maybe_one_arg(instance.name, args, kwargs)
        return func(instance, val, *args, **kwargs)

    return wrapper


def one_maybe_two_args_required(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        one_maybe_two_args(instance.name, args, kwargs)
        return func(instance, val, *args, **kwargs)

    return wrapper


def one_array_arg_required(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        expect_one_arg(instance.name, args, kwargs)
        expect_array(instance.name, args[0])
        return func(instance, val, args[0], **kwargs)

    return wrapper


def one_number_arg_required(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        expect_one_arg(instance.name, args, kwargs)
        num = expect_number(instance.name, args[0])
        return func(instance, val, num, **kwargs)

    return wrapper


def one_string_arg_required(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        expect_one_arg(instance.name, args, kwargs)
        expect_string(instance.name, args[0])
        return func(instance, val, args[0], **kwargs)

    return wrapper


def two_string_args_required(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        expect_n_args(instance.name, 2, args, kwargs)
        expect_string(instance.name, args[0])
        expect_string(instance.name, args[1])
        return func(instance, val, args[0], args[1], **kwargs)

    return wrapper


def no_args(func):
    @wraps(func)
    def wrapper(instance, val, *args, **kwargs):
        expect_no_args(instance.name, args, kwargs)
        return func(instance, val, *args, **kwargs)

    return wrapper
