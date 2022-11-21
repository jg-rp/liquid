"""System wide limits.

Ideally these limits would be configurable from a liquid.Environment, but our
template parser functions, filter decorators and expression objects don't have
access to an Environment. Changing that would require significant refactoring
resulting in too many breaking changes.
"""

import os
import sys

from typing import Any

from liquid.exceptions import LiquidValueError


_MIN_STR_INT = 640
_DEFAULT_MAX_STR_INT = 4300


def _init_int_max_str_digits() -> int:
    var = "LIQUIDINTMAXSTRDIGITS"
    env = os.environ.get(var)

    if env is None:
        if hasattr(sys, "get_int_max_str_digits"):
            return sys.get_int_max_str_digits()  # type: ignore

        var = "PYTHONINTMAXSTRDIGITS"
        env = os.environ.get(var)

    if env is None:
        return _DEFAULT_MAX_STR_INT

    if not env.isdigit():
        raise TypeError(
            f"{var}: invalid limit; must be >= " f"{_MIN_STR_INT} or 0 for unlimited"
        )

    max_digits = int(env)

    if max_digits == 0 or max_digits >= _MIN_STR_INT:
        return max_digits

    raise ValueError(
        f"{var}: invalid limit; must be >= {_MIN_STR_INT} or 0 for unlimited"
    )


MAX_STR_INT = _init_int_max_str_digits()


def to_int(val: Any) -> int:
    """Prevent DoS by very large str to int conversion.

    See https://github.com/python/cpython/issues/95778
    """
    if (
        isinstance(val, (str, bytes, bytearray))
        and MAX_STR_INT != 0
        and len(val) > MAX_STR_INT
    ):
        raise LiquidValueError(
            f"integer string conversion limit ({MAX_STR_INT}) reached: "
            f"value has {len(val)} digits"
        )
    return int(val)
