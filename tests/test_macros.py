"""Test cases for `macro` and `call` tags."""
import asyncio
from unittest import TestCase

from typing import Mapping
from typing import NamedTuple
from typing import Any
from typing import Dict

from liquid.context import StrictUndefined
from liquid.environment import Environment
from liquid.exceptions import UndefinedError
from liquid.extra import add_macro_tags
from liquid.loaders import DictLoader


class Case(NamedTuple):
    """Table-driven test helper."""

    description: str
    template: str
    expect: str
    globals: Mapping[str, Any]
    partials: Dict[str, str]


class MacroRenderTestCase(TestCase):
    """Test cases for rendering the `macro` and `call` tags."""

    def test_render_macro(self) -> None:
        """Test that we can render `macro` and `call` tags."""
        test_cases = [
            Case(
                description="basic macro no call",
                template=r"{% macro 'func' %}Hello, World!{% endmacro %}",
                expect="",
                globals={},
                partials={},
            ),
            Case(
                description="call basic macro",
                template=(
                    r"{% macro 'func' %}Hello, World!{% endmacro %}"
                    r"{% call 'func' %}"
                ),
                expect="Hello, World!",
                globals={},
                partials={},
            ),
            Case(
                description="unquoted macro names are ok",
                template=(
                    r"{% macro func %}Hello, World!{% endmacro %}"
                    r"{% call func %}"
                    r"{% call 'func' %}"
                ),
                expect="Hello, World!Hello, World!",
                globals={},
                partials={},
            ),
            Case(
                description="call basic macro multiple times",
                template=(
                    r"{% macro 'func' %}Hello, World!{% endmacro %}"
                    r"{% call 'func' %}"
                    r"{% call 'func' %}"
                ),
                expect="Hello, World!Hello, World!",
                globals={},
                partials={},
            ),
            Case(
                description="call macro with argument",
                template=(
                    r"{% macro 'func', you %}Hello, {{ you }}!{% endmacro %}"
                    r"{% call 'func', 'you' %} "
                    r"{% call 'func', 'World' %}"
                ),
                expect="Hello, you! Hello, World!",
                globals={},
                partials={},
            ),
            Case(
                description="call macro with default argument",
                template=(
                    r"{% macro 'func' you: 'brian' %}Hello, {{ you }}!{% endmacro %}"
                    r"{% call 'func' %} "
                    r"{% call 'func' you: 'World' %}"
                ),
                expect="Hello, brian! Hello, World!",
                globals={},
                partials={},
            ),
            Case(
                description="boolean literal default argument",
                template=(
                    r"{% macro 'func' foo: false %}"
                    r"{% if foo %}Hello, World!{% endif %}"
                    r"{% endmacro %}"
                    r"{% call 'func' %}"
                    r"{% call 'func' foo: true %}"
                ),
                expect="Hello, World!",
                globals={},
                partials={},
            ),
            Case(
                description="chained default argument from context",
                template=(
                    r"{% macro 'func' greeting: foo.bar %}"
                    r"{{ greeting }}, World!"
                    r"{% endmacro %}"
                    r"{% call 'func' %}"
                    r"{% call 'func' greeting: 'Goodbye' %}"
                ),
                expect="Hello, World!Goodbye, World!",
                globals={"foo": {"bar": "Hello"}},
                partials={},
            ),
            Case(
                description="excess arguments",
                template=(
                    r"{% macro 'func' %}"
                    r"{{ args | join: '-' }}"
                    r"{% endmacro %}"
                    r"{% call 'func' 1, 2 %}"
                ),
                expect="1-2",
                globals={},
                partials={},
            ),
            Case(
                description="excess keyword arguments",
                template=(
                    r"{% macro 'func' %}"
                    r"{% for arg in kwargs %}"
                    r"{{ arg[0] }} => {{ arg[1] }}, "
                    r"{% endfor %}"
                    r"{% endmacro %}"
                    r"{% call 'func', a: 1, b: 2 %}"
                ),
                expect="a => 1, b => 2, ",
                globals={},
                partials={},
            ),
            Case(
                description="missing argument",
                template=(
                    r"{% macro 'func', foo %}"
                    r"{{ foo }}"
                    r"{% endmacro %}"
                    r"{% call 'func' %}"
                ),
                expect="",
                globals={},
                partials={},
            ),
            Case(
                description="undefined macro",
                template=(r"{% call 'func' %}"),
                expect="",
                globals={},
                partials={},
            ),
            Case(
                description="default before positional",
                template=(
                    r"{% macro 'func' you: 'brian', greeting %}"
                    r"{{ greeting }}, {{ you }}!"
                    r"{% endmacro %}"
                    r"{% call 'func' %} "
                    r"{% call 'func' you: 'World', greeting: 'Goodbye' %}"
                ),
                expect=", brian! Goodbye, World!",
                globals={},
                partials={},
            ),
        ]

        for case in test_cases:
            env = Environment(loader=DictLoader(case.partials))
            add_macro_tags(env)

            template = env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                result = template.render()
                self.assertEqual(result, case.expect)

    def test_render_macro_strict_undefined(self) -> None:
        """Test that missing arguments and undefined macros are `Undefined`."""
        test_cases = [
            Case(
                description="missing argument",
                template=(
                    r"{% macro 'func', foo %}"
                    r"{{ foo }}"
                    r"{% endmacro %}"
                    r"{% call 'func' %}"
                ),
                expect="'foo' is undefined, on line 1",
                globals={},
                partials={},
            ),
            Case(
                description="undefined macro",
                template=(r"{% call 'func' %}"),
                expect="'func' is undefined, on line 1",
                globals={},
                partials={},
            ),
        ]

        for case in test_cases:
            env = Environment(
                loader=DictLoader(case.partials),
                undefined=StrictUndefined,
            )
            add_macro_tags(env)

            template = env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                with self.assertRaises(UndefinedError) as raised:
                    template.render()
                self.assertEqual(case.expect, str(raised.exception))

    def test_render_macro_async(self) -> None:
        """Test that we can render a macro asynchronously."""
        env = Environment()
        add_macro_tags(env)

        template = env.from_string(
            r"{% macro 'foo', you: 'World' %}"
            r"Hello, {{ you }}!"
            r"{% endmacro %}"
            r"{% call 'foo' %}"
            r"{% call 'foo', you: 'you' %}"
            r"{% call 'nosuchthing' %}"
        )

        async def coro() -> str:
            return await template.render_async()

        result = asyncio.run(coro())
        self.assertEqual(result, "Hello, World!Hello, you!")


class AnalyzeMacroTestCase(TestCase):
    """Test cases for analyzing `macro` and `call` tags."""

    def test_analyze_macro_tag(self) -> None:
        """Test that we can statically analyze macro and call tags."""
        env = Environment()
        add_macro_tags(env)

        template = env.from_string(
            r"{% macro 'foo', you: 'World', arg: n %}"
            r"Hello, {{ you }}!"
            r"{% endmacro %}"
            r"{% call 'foo' %}"
            r"{% assign x = 'you' %}"
            r"{% call 'foo', you: x %}"
        )

        expected_template_globals = {
            "n": [("<string>", 1)],
        }
        expected_template_locals = {"x": [("<string>", 1)]}
        expected_refs = {
            "n": [("<string>", 1)],
            "you": [("<string>", 1)],
            "x": [("<string>", 1)],
        }
        expected_filters = {}
        expected_tags = {
            "macro": [("<string>", 1)],
            "call": [("<string>", 1), ("<string>", 1)],
            "assign": [("<string>", 1)],
        }

        analysis = template.analyze()

        self.assertEqual(analysis.local_variables, expected_template_locals)
        self.assertEqual(analysis.global_variables, expected_template_globals)
        self.assertEqual(analysis.variables, expected_refs)
        self.assertEqual(analysis.filters, expected_filters)
        self.assertEqual(analysis.tags, expected_tags)
