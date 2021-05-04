from liquid.filter import string_filter
from liquid.filter import liquid_filter
from liquid.filter import with_context


@liquid_filter
@with_context
def link_to_tag(label, tag, *, context):
    handle = context.resolve("handle", default="")
    return f'<a title="Show tag {tag}" href="/collections/{handle}/{tag}">{label}</a>'


@string_filter
def highlight_active_tag(tag, css_class="active"):
    return f'<span class="{css_class}">{tag}</span>'


@liquid_filter
@with_context
def link_to_add_tag(label, tag, *, context):
    handle = context.resolve("handle", default="")
    tags = "+".join(set(context.resolve("current_tags", default=[]) + [tag]))
    return f'<a title="Show tag {tag}" href="/collections/{handle}/{tags}">{label}</a>'


@liquid_filter
@with_context
def link_to_remove_tag(label, tag, *, context):
    handle = context.resolve("handle", default="")
    current_tags = set(context.resolve("current_tags", default=[]))
    tags = "+".join(t for t in current_tags if t != tag)
    return f'<a title="Hide tag {tag}" href="/collections/{handle}/{tags}">{label}</a>'
