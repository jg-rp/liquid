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
            Case(
                description="parent variables are in scope",
                template=(
                    "{% extends 'foo' %}"
                    "{% block bar %}goodbye, {{ you }}{{ something }}{% endblock %}"
                ),
                expect="goodbye, world",
                globals={},
                partials={
                    "foo": (
                        "{% assign you = 'world' %}"
                        "{% block bar %}hello, {{ you }}!{% endblock %}"
                        "{% assign something = 'other' %}"
                    )
                },
            ),
            Case(
                description="child variables are in scope",
                template=(
                    "{% extends 'foo' %}"
                    "{% block bar %}"
                    "{% assign something = '/other' %}"
                    "goodbye, {{ you }}"
                    "{% endblock %}"
                ),
                expect="goodbye, world/other",
                globals={},
                partials={
                    "foo": (
                        "{% assign you = 'world' %}"
                        "{% block bar %}{% endblock %}"
                        "{{ something }}"
                    )
                },
            ),
            Case(
                description="nested outer nested block",
                template="{% extends 'foo' %}{% block bar %}Goodbye{% endblock %}",
                expect="Goodbye!",
                globals={"you": "world"},
                partials={
                    "foo": (
                        "{% block bar %}"
                        "{% block greeting %}Hello{% endblock %}"
                        ", {{ you }}!"
                        "{% endblock %}"
                        "!"
                    )
                },
            ),
            Case(
                description="override nested block",
                template=(
                    "{% extends 'foo' %}{% block greeting %}Goodbye{% endblock %}"
                ),
                expect="Goodbye, world!",
                globals={"you": "world"},
                partials={
                    "foo": (
                        "{% block bar %}"
                        "{% block greeting %}Hello{% endblock %}"
                        ", {{ you }}!"
                        "{% endblock %}"
                    )
                },
            ),
            Case(
                description="super nested blocks",
                template=(
                    "{% extends 'foo' %}"
                    "{% block bar %}{{ block.super }}!!{% endblock %}"
                ),
                expect="Hello, world!!!",
                globals={"you": "world"},
                partials={
                    "foo": (
                        "{% block bar %}"
                        "{% block greeting %}Hello{% endblock %}"
                        ", {{ you }}!"
                        "{% endblock %}"
                    )
                },
            ),
            Case(
                description="include an extended template",
                template="{% include 'bar' %}",
                expect="foo bar",
                globals={"you": "world"},
                partials={
                    "foo": (
                        "{% block bar %}"
                        "{% block greeting %}Hello{% endblock %}"
                        ", {{ you }}!"
                        "{% endblock %}"
                    ),
                    "bar": "{% extends 'foo' %}{% block bar %}foo bar{% endblock %}",
                },
            ),
            Case(
                description="include in an overridden block",
                template=(
                    "{% extends 'foo' %}"
                    "{% block greeting %}{% include 'bar' %}{% endblock %}"
                ),
                expect="I am included, world!",
                globals={"you": "world"},
                partials={
                    "foo": (
                        "{% block bar %}"
                        "{% block greeting %}Hello{% endblock %}"
                        ", {{ you }}!"
                        "{% endblock %}"
                    ),
                    "bar": "I am included",
                },
            ),
            Case(
                description="render an extended template",
                template="{% render 'bar' %}",
                expect="foo bar",
                globals={"you": "world"},
                partials={
                    "foo": (
                        "{% block bar %}"
                        "{% block greeting %}Hello{% endblock %}"
                        ", {{ you }}!"
                        "{% endblock %}"
                    ),
                    "bar": "{% extends 'foo' %}{% block bar %}foo bar{% endblock %}",
                },
            ),
            Case(
                description="render in an overridden block",
                template=(
                    "{% extends 'foo' %}"
                    "{% block greeting %}{% render 'bar' %}{% endblock %}"
                ),
                expect="I am rendered, world!",
                globals={"you": "world"},
                partials={
                    "foo": (
                        "{% block bar %}"
                        "{% block greeting %}Hello{% endblock %}"
                        ", {{ you }}!"
                        "{% endblock %}"
                    ),
                    "bar": "I am rendered",
                },
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
