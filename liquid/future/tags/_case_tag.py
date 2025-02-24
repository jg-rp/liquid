from __future__ import annotations

from liquid.builtin.tags.case_tag import CaseNode
from liquid.builtin.tags.case_tag import CaseTag


class LaxCaseNode(CaseNode):
    """Parse tree node for the lax "case" tag."""

    # TODO


class LaxCaseTag(CaseTag):
    """A `case` tag that is lax in its handling of extra `else` and `when` blocks."""

    # TODO
