"""Test that we can traverse a template's syntax tree to find comments"""
# pylint: disable=missing-class-docstring missing-function-docstring

import unittest

from typing import Iterator
from typing import Tuple

from liquid import Template
from liquid.ast import Node
from liquid.builtin.tags.comment_tag import CommentNode
from liquid.template import BoundTemplate


class FindCommentsTestCase(unittest.TestCase):
    def _find_comment_text(self, template: BoundTemplate) -> Iterator[Tuple[int, str]]:
        def visit(node: Node) -> Iterator[Tuple[int, str]]:
            if isinstance(node, CommentNode) and node.text is not None:
                yield (node.tok.linenum, node.text)
            for child in node.children():
                if child.node:
                    yield from visit(child.node)

        for child in template.tree.statements:
            yield from visit(child)

    def test_find_comment_tag_text(self):
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

        comments = list(self._find_comment_text(template))
        self.assertEqual(len(comments), 4)
        self.assertEqual(
            comments,
            [
                (1, "hello"),
                (3, "\nfoo bar\n"),
                (9, "goodbye"),
                (12, "world"),
            ],
        )

    def test_find_inline_comment_tag_text(self):
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

        comments = list(self._find_comment_text(template))
        self.assertEqual(len(comments), 4)
        self.assertEqual(
            comments,
            [
                (1, "hello"),
                (3, "# foo bar\n# foo bar"),
                (10, "goodbye"),
                (13, "world"),
            ],
        )
