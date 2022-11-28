"""Test cases for `macro` and `call` tags."""
# pylint: disable=missing-class-docstring,missing-function-docstring

import asyncio
from unittest import TestCase

from typing import Mapping
from typing import NamedTuple
from typing import Any
from typing import Dict

from liquid.context import StrictUndefined
from liquid.environment import Environment
from liquid.exceptions import UndefinedError
from liquid.loaders import DictLoader

from liquid.token import Token
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA

from liquid.extra.tags import MacroTag
from liquid.extra.tags import CallTag
from liquid.extra.tags.macro import tokenize_macro_expression


class LexerCase(NamedTuple):
    description: str
    source: str
    expect: Any


class RenderCase(NamedTuple):
    description: str
    template: str
    expect: str
    globals: Mapping[str, Any]
    partials: Dict[str, str]


class MacroLexerTestCase(TestCase):
    def test_lex_macro_expression(self) -> None:
        """Test that we can tokenize `macro` tags."""
        test_cases = [
            LexerCase(
                description="no args macro",
                source="'func'",
                expect=[
                    Token(1, TOKEN_STRING, "func"),
                ],
            ),
            LexerCase(
                description="positional args macro",
                source="'func', foo, bar",
                expect=[
                    Token(1, TOKEN_STRING, "func"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "foo"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "bar"),
                ],
            ),
            LexerCase(
                description="positional args macro no leading comma",
                source="'func' foo, bar",
                expect=[
                    Token(1, TOKEN_STRING, "func"),
                    Token(1, TOKEN_IDENTIFIER, "foo"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "bar"),
                ],
            ),
            LexerCase(
                description="keyword args macro",
                source="'func', foo: 1, bar: 2",
                expect=[
                    Token(1, TOKEN_STRING, "func"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "foo"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "1"),
                    Token(1, TOKEN_COMMA, ","),
                    Token(1, TOKEN_IDENTIFIER, "bar"),
                    Token(1, TOKEN_COLON, ":"),
                    Token(1, TOKEN_INTEGER, "2"),
                ],
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_macro_expression(case.source))
                self.assertTrue(len(tokens), len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)


class MacroRenderTestCase(TestCase):
    def test_render_macro(self) -> None:
        """Test that we can render `macro` and `call` tags."""
        test_cases = [
            RenderCase(
                description="basic macro no call",
                template=r"{% macro 'func' %}Hello, World!{% endmacro %}",
                expect="",
                globals={},
                partials={},
            ),
            RenderCase(
                description="call basic macro",
                template=(
                    r"{% macro 'func' %}Hello, World!{% endmacro %}"
                    r"{% call 'func' %}"
                ),
                expect="Hello, World!",
                globals={},
                partials={},
            ),
            RenderCase(
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
            RenderCase(
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
            RenderCase(
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
            RenderCase(
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
            RenderCase(
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
            RenderCase(
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
            RenderCase(
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
            RenderCase(
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
            RenderCase(
                description="undefined macro",
                template=(r"{% call 'func' %}"),
                expect="",
                globals={},
                partials={},
            ),
            RenderCase(
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
            env.add_tag(MacroTag)
            env.add_tag(CallTag)

            template = env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                result = template.render()
                self.assertEqual(result, case.expect)

    def test_render_macro_strict_undefined(self) -> None:
        """Test that missing arguments and undefined macros are `Undefined`."""
        test_cases = [
            RenderCase(
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
            RenderCase(
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
            env.add_tag(MacroTag)
            env.add_tag(CallTag)

            template = env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                with self.assertRaises(UndefinedError) as raised:
                    template.render()
                self.assertEqual(case.expect, str(raised.exception))

    def test_render_macro_async(self) -> None:
        """Test that we can render a macro asynchronously."""
        env = Environment()
        env.add_tag(MacroTag)
        env.add_tag(CallTag)

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
    def test_analyze_macro_tag(self) -> None:
        """Test that we can statically analyze macro and call tags."""
        env = Environment()
        env.add_tag(MacroTag)
        env.add_tag(CallTag)

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

        analysis = template.analyze()

        self.assertEqual(analysis.local_variables, expected_template_locals)
        self.assertEqual(analysis.global_variables, expected_template_globals)
        self.assertEqual(analysis.variables, expected_refs)
