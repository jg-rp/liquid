# type: ignore
"""Legacy implementations of non-standard filters."""

try:
    from markupsafe import Markup
except ImportError:
    from liquid.exceptions import Markup

from .string import StringFilter

# pylint: disable=too-few-public-methods arguments-differ


class Safe(StringFilter):
    """Stringify and mark as safe."""

    __slots__ = ()

    name = "safe"

    def filter(self, val):
        if self.env.autoescape:
            return Markup(val)
        return val
