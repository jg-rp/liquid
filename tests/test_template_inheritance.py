"""Test cases for `extends` and `block` tags."""
import asyncio
from unittest import TestCase

from typing import Mapping
from typing import NamedTuple
from typing import Any
from typing import Dict

from liquid import BoundTemplate
from liquid import Environment
from liquid.extra import add_inheritance_tags
from liquid.loaders import DictLoader


class Case(NamedTuple):
    """Table-driven test helper."""

    description: str
    template: str
    expect: str
    globals: Mapping[str, Any]
    partials: Dict[str, str]


class TemplateInheritanceTestCase(TestCase):
    """Test cases for rendering the `extends` and `block` tags."""

    def test_extend_template(self) -> None:
        """Test that we can extend a template."""
        test_cases = [
            Case(
                description="no blocks",
                template="{% extends 'foo' %} this should not be rendered",
                expect="hello, world!",
                globals={"you": "world!"},
                partials={"foo": "hello, {{ you }}"},
            ),
            Case(
                description="no parent block",
                template=(
                    "{% extends 'foo' %}"
                    "{% block bar %}this should not be rendered{% endblock %}"
                ),
                expect="hello, world!",
                globals={"you": "world!"},
                partials={"foo": "hello, {{ you }}"},
            ),
            Case(
                description="no child block",
                template="{% extends 'foo' %} this should not be rendered",
                expect="hello, world!",
                globals={"you": "world!"},
                partials={"foo": "hello, {% block bar %}{{ you }}{% endblock %}"},
            ),
            Case(
                description="override parent block",
                template="{% extends 'foo' %}{% block bar %}sue{% endblock %}",
                expect="hello, sue",
                globals={"you": "world!"},
                partials={"foo": "hello, {% block bar %}{{ you }}{% endblock %}"},
            ),
            Case(
                description="render base template directly",
                template="hello, {% block bar %}{{ you }}{% endblock %}",
                expect="hello, world!",
                globals={"you": "world!"},
                partials={},
            ),
            Case(
                description="output super block",
                template=(
                    "{% extends 'foo' %}"
                    "{% block bar %}{{ block.super }} and sue{% endblock %}"
                ),
                expect="hello, world! and sue",
                globals={"you": "world!"},
                partials={"foo": "hello, {% block bar %}{{ you }}{% endblock %}"},
            ),
        ]

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        for case in test_cases:
            env = Environment(loader=DictLoader(case.partials))
            add_inheritance_tags(env)
            template = env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                result = template.render()
                self.assertEqual(result, case.expect)

            with self.subTest(msg=case.description, asynchronous=True):
                result = asyncio.run(coro(template))
                self.assertEqual(result, case.expect)
