"""Test cases for `extends` and `block` tags."""
import asyncio
from unittest import TestCase

from typing import Mapping
from typing import NamedTuple
from typing import Any
from typing import Dict

from liquid import BoundTemplate
from liquid import Environment
from liquid import StrictUndefined
from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import RequiredBlockError
from liquid.exceptions import UndefinedError
from liquid.exceptions import TemplateInheritanceError
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
                description="block scoped parent variables are in scope",
                template=(
                    "{% extends 'foo' %}"
                    "{% block bar %}"
                    "goodbye, {{ you }} #{{ i }}{{ something }} "
                    "{% endblock %}"
                ),
                expect="goodbye, world #1 goodbye, world #2 ",
                globals={},
                partials={
                    "foo": (
                        "{% assign you = 'world' %}"
                        "{% for i in (1..2) %}"
                        "{% block bar %}hello, {{ you }}!{% endblock %}"
                        "{% endfor %}"
                        "{% assign something = 'other' %}"
                    )
                },
            ),
            Case(
                description="nested block scoped parent variables are in scope",
                template=(
                    "{% extends 'some' %}"
                    "{% block baz %}"
                    "Hello, {{ you }} {{ other }} {{ i }}:{{ x }} "
                    "{% endblock %}"
                ),
                expect=(
                    "Hello, world banana 1:1 Hello, world banana 1:2 "
                    "Hello, world banana 2:1 Hello, world banana 2:2 "
                ),
                globals={},
                partials={
                    "base": (
                        "{% assign you = 'world' %}"
                        "{% for i in (1..2) %}"
                        "{% block bar %}hello, {{ you }}!{% endblock %}"
                        "{% endfor %}"
                    ),
                    "some": (
                        "{% extends 'base' %}"
                        "{% block bar %}"
                        "{% assign other = 'banana' %}"
                        "{% for x in (1..2) %}"
                        "{% block baz %}"
                        "{% endblock baz %}"
                        "{% endfor %}"
                        "{% endblock bar %}"
                    ),
                },
            ),
            Case(
                description="child variables are out of scope",
                template=(
                    "{% extends 'foo' %}"
                    "{% block bar %}"
                    "{% assign something = '/other' %}"
                    "goodbye, {{ you }}"
                    "{% assign you = 'sue' %}"
                    "{% endblock %}"
                ),
                expect="goodbye, world",
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
                description="nested outer block",
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
                description="override a parent's parent block",
                template=(
                    "{% extends 'bar' %}{% block greeting %}Goodbye,{% endblock %}"
                ),
                expect="Goodbye, world",
                globals={"you": "world"},
                partials={
                    "foo": "{% block greeting %}Hello{% endblock %} {{ you }}",
                    "bar": "{% extends 'foo' %}",
                },
            ),
            Case(
                description="multi-level super",
                template=(
                    "{% extends 'baz' %}"
                    "{% block bar %}{{ block.super }}!!{% endblock %}"
                ),
                expect="Hello, world!**!!",
                globals={"you": "world"},
                partials={
                    "foo": (
                        "{% block bar %}"
                        "{% block greeting %}Hello{% endblock %}"
                        ", {{ you }}!"
                        "{% endblock %}"
                    ),
                    "baz": (
                        "{% extends 'foo' %}"
                        "{% block bar %}{{ block.super }}**{% endblock %}"
                    ),
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

    def test_missing_required_block(self) -> None:
        """Test that we raise an exception if a required block is missing."""
        template = "{% extends 'foo' %}{% block baz %}{% endblock %}"
        partials = {"foo": "{% block bar required %}{% endblock %}"}

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=DictLoader(partials))
        add_inheritance_tags(env)
        template = env.from_string(template)

        with self.assertRaises(RequiredBlockError):
            template.render()

        with self.subTest(asynchronous=True):
            with self.assertRaises(RequiredBlockError):
                asyncio.run(coro(template))

    def test_missing_required_block_long_stack(self) -> None:
        """Test that we raise an exception if a required block is missing in a long
        stack."""
        template = "{% extends 'bar' %}"
        partials = {
            "foo": "{% block baz required %}{% endblock %}",
            "bar": "{% extends 'foo' %}{% block some %}hello{% endblock %}",
        }

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=DictLoader(partials))
        add_inheritance_tags(env)
        template = env.from_string(template)

        with self.assertRaises(RequiredBlockError):
            template.render()

        with self.subTest(asynchronous=True):
            with self.assertRaises(RequiredBlockError):
                asyncio.run(coro(template))

    def test_immediate_override_required_block(self) -> None:
        """Test that we can override a required block in the immediate child."""
        template = "{% extends 'foo' %}{% block bar %}hello{% endblock %}"
        partials = {"foo": "{% block bar required %}{% endblock %}"}
        expect = "hello"

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=DictLoader(partials))
        add_inheritance_tags(env)
        template = env.from_string(template)

        result = template.render()
        self.assertEqual(result, expect)

        with self.subTest(asynchronous=True):
            result = asyncio.run(coro(template))
            self.assertEqual(result, expect)

    def test_override_required_block_in_leaf(self) -> None:
        """Test that we can override a required block."""
        template = "{% extends 'foo' %}{% block baz %}hello{% endblock %}"
        partials = {
            "foo": "{% block baz required %}{% endblock %}",
            "bar": "{% extends 'foo' %}",
        }
        expect = "hello"

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=DictLoader(partials))
        add_inheritance_tags(env)
        template = env.from_string(template)

        result = template.render()
        self.assertEqual(result, expect)

        with self.subTest(asynchronous=True):
            result = asyncio.run(coro(template))
            self.assertEqual(result, expect)

    def test_override_required_block_in_stack(self) -> None:
        """Test that we can override a required block somewhere on the block stack."""
        template = "{% extends 'bar' %}"
        partials = {
            "foo": "{% block baz required %}{% endblock %}",
            "bar": "{% extends 'foo' %}{% block baz %}hello{% endblock %}",
        }
        expect = "hello"

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=DictLoader(partials))
        add_inheritance_tags(env)
        template = env.from_string(template)

        result = template.render()
        self.assertEqual(result, expect)

        with self.subTest(asynchronous=True):
            result = asyncio.run(coro(template))
            self.assertEqual(result, expect)

    def test_override_required_block_not_in_base(self) -> None:
        """Test that we can override a required block from a non-base template."""
        template = "{% extends 'bar' %}{% block content %}hello{% endblock %}"
        partials = {
            "foo": "{% block content %}{% endblock %}",
            "bar": "{% extends 'foo' %}{% block content required %}{% endblock %}",
        }
        expect = "hello"

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=DictLoader(partials))
        add_inheritance_tags(env)
        template = env.from_string(template)

        result = template.render()
        self.assertEqual(result, expect)

        with self.subTest(asynchronous=True):
            result = asyncio.run(coro(template))
            self.assertEqual(result, expect)

    def test_missing_required_block_not_in_base(self) -> None:
        """Test that we raise an exception when missing a required block from a non-base
        template."""
        template = "{% extends 'bar' %}"
        partials = {
            "foo": "{% block content %}{% endblock %}",
            "bar": "{% extends 'foo' %}{% block content required %}{% endblock %}",
        }

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=DictLoader(partials))
        add_inheritance_tags(env)
        template = env.from_string(template)

        with self.assertRaises(RequiredBlockError):
            template.render()

        with self.subTest(asynchronous=True):
            with self.assertRaises(RequiredBlockError):
                asyncio.run(coro(template))

    def test_override_required_block_directly(self) -> None:
        """Test that we raise an exception if rendering a required block directly."""
        template = "{% block foo required %}{% endblock %}"

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment()
        add_inheritance_tags(env)
        template = env.from_string(template)

        with self.assertRaises(RequiredBlockError):
            template.render()

        with self.subTest(asynchronous=True):
            with self.assertRaises(RequiredBlockError):
                asyncio.run(coro(template))

    def test_too_many_extends(self) -> None:
        """Test that we raise an exception if more than one `extends` tag exists."""
        template = "{% extends 'foo' %}{% extends 'bar' %}"

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment()
        add_inheritance_tags(env)
        template = env.from_string(template)

        with self.assertRaises(TemplateInheritanceError):
            template.render()

        with self.subTest(asynchronous=True):
            with self.assertRaises(TemplateInheritanceError):
                asyncio.run(coro(template))

    def test_invalid_block_name(self) -> None:
        """Test that we raise an exception given an invalid block name."""
        template = "{% extends 'foo' %}"
        partials = {
            "foo": "{% block 47 %}{% endblock %}",
        }

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=DictLoader(partials))
        add_inheritance_tags(env)
        template = env.from_string(template)

        with self.assertRaises(LiquidSyntaxError):
            template.render()

        with self.subTest(asynchronous=True):
            with self.assertRaises(LiquidSyntaxError):
                asyncio.run(coro(template))

    def test_block_drop_properties(self) -> None:
        """Test that we handle undefined block drop properties"""
        template = (
            "{% extends 'foo' %}"
            "{% block bar %}{{ block.nosuchthing }} and sue{% endblock %}"
        )
        partials = {"foo": "hello, {% block bar %}{{ you }}{% endblock %}"}

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=DictLoader(partials), undefined=StrictUndefined)
        add_inheritance_tags(env)
        template = env.from_string(template)

        with self.assertRaises(UndefinedError):
            template.render()

        with self.subTest(asynchronous=True):
            with self.assertRaises(UndefinedError):
                asyncio.run(coro(template))

    def test_block_no_super_block(self) -> None:
        """Test that we handle undefined block.super"""
        template = "hello, {% block bar %}{{ block.super }}{{ you }}{% endblock %}"

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(undefined=StrictUndefined)
        add_inheritance_tags(env)
        template = env.from_string(template)

        with self.assertRaises(UndefinedError):
            template.render()

        with self.subTest(asynchronous=True):
            with self.assertRaises(UndefinedError):
                asyncio.run(coro(template))

    def test_duplicate_block_names(self) -> None:
        """Test that we raise an exception when a template has duplicate block names."""
        template = (
            "{% extends 'foo' %}"
            "{% block bar %}{% endblock %}{% block bar %}{% endblock %}"
        )
        partials = {"foo": "{% block bar %}{% endblock %}"}

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=DictLoader(partials))
        add_inheritance_tags(env)
        template = env.from_string(template)

        with self.assertRaises(TemplateInheritanceError):
            template.render()

        with self.subTest(asynchronous=True):
            with self.assertRaises(TemplateInheritanceError):
                asyncio.run(coro(template))

    def test_endblock_name(self) -> None:
        """Test that we can name `endblock` tags."""
        template = "{% extends 'foo' %}"
        partials = {"foo": "{% block baz %}hello{% endblock baz %}"}
        expect = "hello"

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=DictLoader(partials))
        add_inheritance_tags(env)
        template = env.from_string(template)

        result = template.render()
        self.assertEqual(result, expect)

        with self.subTest(asynchronous=True):
            result = asyncio.run(coro(template))
            self.assertEqual(result, expect)

    def test_mismatched_endblock_name(self) -> None:
        """Test that we raise an exception if an endblock label does not match."""
        template = "{% extends 'foo' %}"
        partials = {"foo": "{% block baz %}hello{% endblock something %}"}

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=DictLoader(partials))
        add_inheritance_tags(env)

        template = env.from_string(template)

        with self.assertRaises(TemplateInheritanceError):
            template.render()

        with self.subTest(asynchronous=True):
            with self.assertRaises(TemplateInheritanceError):
                asyncio.run(coro(template))

        with self.subTest(direct_render=True):
            with self.assertRaises(TemplateInheritanceError):
                env.from_string(partials["foo"])

    def test_override_nested_block_and_outer_block(self) -> None:
        """Test that we can override a nested block and its outer block."""
        template = (
            '{% extends "foo" %}'
            "{% block title %}Home{% endblock %}"
            "{% block head %}{{ block.super }}Hello{% endblock %}"
        )
        partials = {
            "foo": (
                "{% block head %}"
                "<title>{% block title %}{% endblock %} - Welcome</title>"
                "{% endblock %}"
            )
        }
        expect = "<title>Home - Welcome</title>Hello"

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=DictLoader(partials))
        add_inheritance_tags(env)
        template = env.from_string(template)

        result = template.render()
        self.assertEqual(result, expect)

        with self.subTest(asynchronous=True):
            result = asyncio.run(coro(template))
            self.assertEqual(result, expect)

    def test_recursive_extends(self) -> None:
        """Test that we handle recursive extends."""
        loader = DictLoader(
            {
                "some": "{% extends 'other' %}",
                "other": "{% extends 'some' %}",
            }
        )

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=loader)
        add_inheritance_tags(env)
        template = env.get_template("some")

        with self.assertRaises(TemplateInheritanceError):
            template.render()

        with self.subTest(asynchronous=True):
            with self.assertRaises(TemplateInheritanceError):
                asyncio.run(coro(template))

    def test_overridden_block_to_many_blocks(self) -> None:
        """Test that we can override a block with many sub-blocks."""
        loader = DictLoader(
            {
                "base": "{% block head %}Hello - Welcome{% endblock %}",
                "other": (
                    "{% extends 'base' %}"
                    "{% block head %}"
                    "{{ block.super }}:"
                    "{% block foo %}!{% endblock %} - "
                    "{% block bar %}{% endblock %}"
                    "{% endblock %}"
                ),
                "some": (
                    "{% extends 'other' %}"
                    "{% block foo %}foo{{ block.super }}{% endblock %}"
                    "{% block bar %}bar{% endblock %}"
                ),
            }
        )
        expect = "Hello - Welcome:foo! - bar"

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        env = Environment(loader=loader)
        add_inheritance_tags(env)
        template = env.get_template("some")

        result = template.render()
        self.assertEqual(result, expect)

        with self.subTest(asynchronous=True):
            result = asyncio.run(coro(template))
            self.assertEqual(result, expect)
