from liquid.builtin.tags.unless_tag import UnlessTag
from liquid.mode import Mode


class LaxUnlessTag(UnlessTag):
    """An `unless` tag that is lax in its handling of extra expressions and blocks."""

    mode = Mode.LAX
