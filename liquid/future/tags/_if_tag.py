from liquid.builtin.tags.if_tag import IfTag
from liquid.mode import Mode


class LaxIfTag(IfTag):
    """An `if` tag that is lax in its handling of extra expressions and blocks."""

    mode = Mode.LAX
