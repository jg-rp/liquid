"""Non-standard filters."""

try:
    from markupsafe import Markup
except ImportError:
    from liquid.exceptions import Markup  # type: ignore

from .string import StringFilter

# pylint: disable=arguments-differ too-few-public-methods


class Safe(StringFilter):
    """Stringify and mark as safe."""

    __slots__ = ()

    name = "safe"

    def filter(self, val):
        if self.env.autoescape:
            return Markup(val)
        return val
