"""Filters that don't exist in the reference implementation."""
from __future__ import annotations
from typing import TYPE_CHECKING

try:
    from markupsafe import Markup
except ImportError:
    from liquid.exceptions import Markup  # type: ignore

from liquid.filter import string_filter
from liquid.filter import with_environment

if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment


@with_environment
@string_filter
def safe(val: str, *, environment: Environment) -> str:
    """Stringify and mark as safe."""
    if environment.autoescape:
        return Markup(val)
    return val
