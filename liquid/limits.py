"""System wide limits.

Ideally these limits would be configurable from a liquid.Environment, but our
template parser functions, filter decorators and expression objects don't have
access to an Environment. Changing that would require significant refactoring
resulting in too many breaking changes.
"""

import os
from typing import Any

from liquid.exceptions import LiquidValueError


MAX_STR_INT = int(
    os.environ.get(
        "LIQUIDINTMAXSTRDIGITS",
        os.environ.get("PYTHONINTMAXSTRDIGITS", "4300"),
    )
)


def to_int(val: Any) -> int:
    """Prevent DoS by very large str to int conversion.

    See https://github.com/python/cpython/issues/95778
    """
    if isinstance(val, (str, bytes, bytearray)) and len(val) > MAX_STR_INT:
        raise LiquidValueError(
            f"integer string conversion limit ({MAX_STR_INT}) reached: "
            f"value has {len(val)} digits"
        )
    return int(val)
