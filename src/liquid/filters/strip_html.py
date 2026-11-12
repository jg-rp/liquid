import re

import markupsafe

from .._filter import FilterContext

RE_HTML_BLOCKS = re.compile(
    r"<script.*?</script>|<!--.*?-->|<style.*?</style>", re.DOTALL
)

RE_HTML_TAGS = re.compile("<.*?>", re.DOTALL)


def strip_html(context: FilterContext, left: object) -> str:
    left = context.to_str(left, "")
    stripped = RE_HTML_TAGS.sub("", RE_HTML_BLOCKS.sub("", context.to_str(left, "")))
    return (
        markupsafe.Markup(stripped) if isinstance(left, markupsafe.Markup) else stripped
    )
