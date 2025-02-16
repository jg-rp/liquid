"""Filters that don't exist in the reference implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from liquid import Markup
from liquid.filter import string_filter
from liquid.filter import with_environment

if TYPE_CHECKING:
    from liquid import Environment


@with_environment
@string_filter
def safe(val: str, *, environment: Environment) -> str:
    """Return a copy of _val_ that will not be automatically HTML escaped on output."""
    if environment.autoescape:
        return Markup(val)
    return val
