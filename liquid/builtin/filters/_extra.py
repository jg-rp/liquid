"""Filters that don't exist in the reference implementation."""

try:
    from markupsafe import Markup
except ImportError:
    from liquid.exceptions import Markup  # type: ignore

from liquid.filter import string_filter
from liquid.filter import with_environment


@with_environment
@string_filter
def safe(val, *, environment):
    """Stringify and mark as safe."""
    if environment.autoescape:
        return Markup(val)
    return val
