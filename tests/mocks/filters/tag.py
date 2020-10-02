from liquid.filter import (
    Filter,
    one_maybe_two_args_required,
    string_required,
)

# pylint: disable=arguments-differ, too-few-public-methods


class LinkToTag(Filter):

    __slots__ = ()

    name = "link_to_tag"
    with_context = True

    def __call__(self, label, tag, *, context):
        handle = context.resolve("handle", default="")
        return (
            f'<a title="Show tag {tag}" href="/collections/{handle}/{tag}">{label}</a>'
        )


class HighlightActiveTag(Filter):

    __slots__ = ()

    name = "highlight_active_tag"

    @one_maybe_two_args_required
    @string_required
    def __call__(self, tag, css_class="active"):
        return f'<span class="{css_class}">{tag}</span>'


class LinkToAddTag(Filter):

    __slots__ = ()

    name = "link_to_add_tag"
    with_context = True

    def __call__(self, label, tag, *, context):
        handle = context.resolve("handle", default="")
        tags = "+".join(set(context.resolve("current_tags", default=[]) + [tag]))
        return (
            f'<a title="Show tag {tag}" href="/collections/{handle}/{tags}">{label}</a>'
        )


class LinkToRemoveTag(Filter):

    __slots__ = ()

    name = "link_to_remove_tag"
    with_context = True

    def __call__(self, label, tag, *, context):
        handle = context.resolve("handle", default="")
        current_tags = set(context.resolve("current_tags", default=[]))
        tags = "+".join(t for t in current_tags if t != tag)
        return (
            f'<a title="Hide tag {tag}" href="/collections/{handle}/{tags}">{label}</a>'
        )
