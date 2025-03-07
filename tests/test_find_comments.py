"""Test that we can traverse a template's syntax tree to find comments."""

from typing import TYPE_CHECKING
from typing import Iterator

from liquid import BoundTemplate
from liquid import RenderContext
from liquid import Template
from liquid.builtin.tags.comment_tag import CommentNode

if TYPE_CHECKING:
    from liquid.ast import Node


def _find_comment_text(template: BoundTemplate) -> Iterator[tuple[int, str]]:
    static_context = RenderContext(template)

    def visit(node: "Node") -> Iterator[tuple[int, str]]:
        if isinstance(node, CommentNode) and node.text is not None:
            yield (node.token.start_index, node.text)
        for child in node.children(static_context, include_partials=False):
            yield from visit(child)

    for child in template.nodes:
        yield from visit(child)


def test_find_comment_tag_text() -> None:
    """Test that we can get text from comment tags."""
    template = Template(
        "\n".join(
            (
                "{% comment %}hello{% endcomment %}",
                "{% if false %}",
                "{% comment %}",
                "foo bar",
                "{% endcomment %}",
                "{% endif %}",
                "{% for x in (1..3) %}",
                "{% if true %}",
                "{% comment %}goodbye{% endcomment %}",
                "{% endif %}",
                "{% endfor %}",
                "{% comment %}world{% endcomment %}",
            )
        )
    )

    comments = list(_find_comment_text(template))
    assert len(comments) == 4
    assert comments == [
        (3, "hello"),
        (53, "\nfoo bar\n"),
        (140, "goodbye"),
        (202, "world"),
    ]


def test_find_inline_comment_tag_text() -> None:
    """Test that we can get text from inline comment tags."""
    template = Template(
        "\n".join(
            (
                "{% # hello %}",
                "{% if false %}",
                "{% #",
                "# foo bar",
                "# foo bar",
                "%}",
                "{% endif %}",
                "{% for x in (1..3) %}",
                "{% if true %}",
                "{% # goodbye %}",
                "{% endif %}",
                "{% endfor %}",
                "{% # world %}",
            )
        )
    )

    comments = list(_find_comment_text(template))
    assert len(comments) == 4
    assert comments == [
        (3, "hello"),
        (32, "# foo bar\n# foo bar"),
        (108, "goodbye"),
        (149, "world"),
    ]
