"""Template static analysis test cases."""

from __future__ import annotations

import asyncio
import itertools
from typing import TYPE_CHECKING

import pytest

from liquid import Environment
from liquid.builtin import DictLoader
from liquid.exceptions import TemplateNotFound
from liquid.span import Span
from liquid.static_analysis import Variable

if TYPE_CHECKING:
    from liquid import BoundTemplate
    from liquid.static_analysis import TemplateAnalysis


class MockEnv(Environment):
    ternary_expressions = True


@pytest.fixture
def env() -> Environment:  # noqa: D103
    return MockEnv(extra=True)


def _assert(
    template: BoundTemplate,
    *,
    locals: dict[str, list[Variable]],  # noqa: A002
    globals: dict[str, list[Variable]],  # noqa: A002
    variables: dict[str, list[Variable]] | None = None,
    filters: dict[str, list[Span]] | None = None,
    tags: dict[str, list[Span]] | None = None,
) -> None:
    variables = {**globals} if variables is None else variables

    async def coro() -> TemplateAnalysis:
        return await template.analyze_async()

    def _assert_refs(got: TemplateAnalysis) -> None:
        assert got.locals == locals
        assert got.globals == globals
        assert got.variables == variables

        if filters:
            assert got.filters == filters
        else:
            assert len(got.filters) == 0

        if tags:
            assert got.tags == tags
        else:
            assert len(got.tags) == 0

    _assert_refs(template.analyze())
    _assert_refs(asyncio.run(coro()))


def test_analyze_output(env: Environment) -> None:
    source = r"{{ x | default: y, allow_false: z }}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "x": [Variable(["x"], Span("", 3))],
            "y": [Variable(["y"], Span("", 16))],
            "z": [Variable(["z"], Span("", 32))],
        },
        filters={
            "default": [Span("", 7)],
        },
    )


def test_bracketed_query_notation(env: Environment) -> None:
    source = r"{{ x['y'].title }}"

    _assert(
        env.from_string(source),
        locals={},
        globals={"x": [Variable(["x", "y", "title"], Span("", 3))]},
    )


def test_quoted_name_notation(env: Environment) -> None:
    source = r"{{ some['foo.bar'] }}"

    _assert(
        env.from_string(source),
        locals={},
        globals={"some": [Variable(["some", "foo.bar"], Span("", 3))]},
    )


def test_nested_queries(env: Environment) -> None:
    source = r"{{ x[y.z].title }}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "x": [Variable(["x", ["y", "z"], "title"], Span("", 3))],
            "y": [Variable(["y", "z"], Span("", 5))],
        },
    )


def test_nested_root_query(env: Environment) -> None:
    source = r"{{ [a.b] }}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "['a', 'b']": [Variable([["a", "b"]], Span("", 3))],
            "a": [Variable(["a", "b"], Span("", 4))],
        },
    )


def test_analyze_ternary(env: Environment) -> None:
    source = r"{{ a if b.c else d }}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "a": [Variable(["a"], Span("", 3))],
            "b": [Variable(["b", "c"], Span("", 8))],
            "d": [Variable(["d"], Span("", 17))],
        },
    )


def test_analyze_ternary_filters(env: Environment) -> None:
    source = r"{{ a | upcase if b.c else d | default: 'x' || append: y }}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "a": [Variable(["a"], Span("", 3))],
            "b": [Variable(["b", "c"], Span("", 17))],
            "d": [Variable(["d"], Span("", 26))],
            "y": [Variable(["y"], Span("", 54))],
        },
        filters={
            "default": [Span("", 30)],
            "append": [Span("", 46)],
        },
    )


def test_analyze_assign(env: Environment) -> None:
    source = r"{% assign x = y | append: z %}"

    _assert(
        env.from_string(source),
        locals={"x": [Variable(["x"], Span("", 10))]},
        globals={
            "y": [Variable(["y"], Span("", 14))],
            "z": [Variable(["z"], Span("", 26))],
        },
        filters={"append": [Span("", 18)]},
        tags={"assign": [Span("", 3)]},
    )


def test_analyze_capture(env: Environment) -> None:
    source = r"{% capture x %}{% if y %}z{% endif %}{% endcapture %}"

    _assert(
        env.from_string(source),
        locals={"x": [Variable(["x"], Span("", 11))]},
        globals={
            "y": [Variable(["y"], Span("", 21))],
        },
        tags={
            "capture": [Span("", 3)],
            "if": [Span("", 18)],
        },
    )


def test_analyze_case(env: Environment) -> None:
    source = "\n".join(
        [
            "{% case x %}",
            "{% when y %}",
            "  {{ a }}",
            "{% when z %}",
            "  {{ b }}",
            "{% else %}",
            "  {{ c }}",
            "{% endcase %}",
        ]
    )

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "x": [Variable(["x"], Span("", 8))],
            "y": [Variable(["y"], Span("", 21))],
            "a": [Variable(["a"], Span("", 31))],
            "z": [Variable(["z"], Span("", 44))],
            "b": [Variable(["b"], Span("", 54))],
            "c": [Variable(["c"], Span("", 75))],
        },
        tags={"case": [Span("", 3)]},
    )


def test_analyze_cycle(env: Environment) -> None:
    source = r"{% cycle x: a, b %}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "a": [Variable(["a"], Span("", 12))],
            "b": [Variable(["b"], Span("", 15))],
            "x": [Variable(["x"], Span("", 9))],
        },
        tags={"cycle": [Span("", 3)]},
    )


def test_analyze_decrement(env: Environment) -> None:
    source = r"{% decrement x %}"

    _assert(
        env.from_string(source),
        locals={"x": [Variable(["x"], Span("", 13))]},
        globals={},
        tags={"decrement": [Span("", 3)]},
    )


def test_analyze_echo(env: Environment) -> None:
    source = r"{% echo x | default: y, allow_false: z %}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "x": [Variable(["x"], Span("", 8))],
            "y": [Variable(["y"], Span("", 21))],
            "z": [Variable(["z"], Span("", 37))],
        },
        filters={
            "default": [Span("", 12)],
        },
        tags={"echo": [Span("", 3)]},
    )


def test_analyze_for(env: Environment) -> None:
    source = "\n".join(
        [
            r"{% for x in (1..y) %}",
            r"  {{ x }}",
            r"{% break %}",
            r"{% else %}",
            r"  {{ z }}",
            r"{% continue %}",
            r"{% endfor %}",
        ]
    )

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "y": [Variable(["y"], Span("", 16))],
            "z": [Variable(["z"], Span("", 60))],
        },
        variables={
            "y": [Variable(["y"], Span("", 16))],
            "x": [Variable(["x"], Span("", 27))],
            "z": [Variable(["z"], Span("", 60))],
        },
        filters={},
        tags={
            "for": [Span("", 3)],
            "break": [Span("", 35)],
            "continue": [Span("", 68)],
        },
    )


def test_analyze_if(env: Environment) -> None:
    source = "\n".join(
        [
            r"{% if x %}",
            r"  {{ a }}",
            r"{% elsif y %}",
            r"  {{ b }}",
            r"{% else %}",
            r"  {{ c }}",
            r"{% endif %}",
        ]
    )

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "x": [Variable(["x"], Span("", 6))],
            "a": [Variable(["a"], Span("", 16))],
            "y": [Variable(["y"], Span("", 30))],
            "b": [Variable(["b"], Span("", 40))],
            "c": [Variable(["c"], Span("", 61))],
        },
        filters={},
        tags={
            "if": [Span("", 3)],
        },
    )


def test_analyze_increment(env: Environment) -> None:
    source = r"{% increment x %}"

    _assert(
        env.from_string(source),
        locals={"x": [Variable(["x"], Span("", 13))]},
        globals={},
        tags={"increment": [Span("", 3)]},
    )


def test_analyze_liquid(env: Environment) -> None:
    source = """\
{% liquid
if product.title
    echo foo | upcase
else
    echo 'product-1' | upcase
endif

for i in (0..5)
    echo i
endfor %}"""

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "product": [Variable(["product", "title"], Span("", 13))],
            "foo": [Variable(["foo"], Span("", 36))],
        },
        variables={
            "product": [Variable(["product", "title"], Span("", 13))],
            "foo": [Variable(["foo"], Span("", 36))],
            "i": [Variable(["i"], Span("", 116))],
        },
        filters={"upcase": [Span("", 42), Span("", 77)]},
        tags={
            "liquid": [Span("", 3)],
            "echo": [Span("", 31), Span("", 58), Span("", 111)],
            "for": [Span("", 91)],
            "if": [Span("", 10)],
        },
    )


def test_analyze_unless(env: Environment) -> None:
    source = """\
{% unless x %}
  {{ a }}
{% elsif y %}
  {{ b }}
{% else %}
  {{ c }}
{% endunless %}"""

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "x": [Variable(["x"], Span("", 10))],
            "a": [Variable(["a"], Span("", 20))],
            "y": [Variable(["y"], Span("", 34))],
            "b": [Variable(["b"], Span("", 44))],
            "c": [Variable(["c"], Span("", 65))],
        },
        tags={
            "unless": [Span("", 3)],
        },
    )


def test_analyze_include() -> None:
    loader = DictLoader({"a": "{{ x }}"})
    env = Environment(loader=loader)
    source = "{% include 'a' %}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "x": [Variable(["x"], Span("a", 3))],
        },
        tags={
            "include": [Span("", 3)],
        },
    )


def test_analyze_included_assign() -> None:
    loader = DictLoader({"a": "{{ x }}{% assign y = 42 %}"})
    env = Environment(loader=loader)
    source = "{% include 'a' %}{{ y }}"

    _assert(
        env.from_string(source),
        locals={
            "y": [Variable(["y"], Span("a", 17))],
        },
        globals={
            "x": [Variable(["x"], Span("a", 3))],
        },
        variables={
            "x": [Variable(["x"], Span("a", 3))],
            "y": [Variable(["y"], Span("", 20))],
        },
        tags={
            "include": [Span("", 3)],
            "assign": [Span("a", 10)],
        },
    )


def test_analyze_include_once() -> None:
    loader = DictLoader({"a": "{{ x }}"})
    env = Environment(loader=loader)
    source = "{% include 'a' %}{% include 'a' %}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "x": [Variable(["x"], Span("a", 3))],
        },
        tags={
            "include": [Span("", 3), Span("", 20)],
        },
    )


def test_analyze_include_recursive() -> None:
    loader = DictLoader({"a": "{{ x }}{% include 'a' %}"})
    env = Environment(loader=loader)
    source = "{% include 'a' %}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "x": [Variable(["x"], Span("a", 3))],
        },
        tags={
            "include": [
                Span("", 3),
                Span("a", 10),
            ],
        },
    )


def test_analyze_include_with_bound_variable() -> None:
    loader = DictLoader({"a": "{{ x | append: y }}{{ a }}"})
    env = Environment(loader=loader)
    source = "{% include 'a' with z %}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "z": [Variable(["z"], Span("", 20))],
            "x": [Variable(["x"], Span("a", 3))],
            "y": [Variable(["y"], Span("a", 15))],
        },
        variables={
            "z": [Variable(["z"], Span("", 20))],
            "x": [Variable(["x"], Span("a", 3))],
            "y": [Variable(["y"], Span("a", 15))],
            "a": [Variable(["a"], Span("a", 22))],
        },
        tags={"include": [Span("", 3)]},
        filters={"append": [Span("a", 7)]},
    )


def test_analyze_include_with_bound_alias() -> None:
    loader = DictLoader({"a": "{{ x | append: y }}"})
    env = Environment(loader=loader)
    source = "{% include 'a' with z as y %}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "z": [Variable(["z"], Span("", 20))],
            "x": [Variable(["x"], Span("a", 3))],
        },
        variables={
            "z": [Variable(["z"], Span("", 20))],
            "x": [Variable(["x"], Span("a", 3))],
            "y": [Variable(["y"], Span("a", 15))],
        },
        tags={"include": [Span("", 3)]},
        filters={"append": [Span("a", 7)]},
    )


def test_analyze_include_with_arguments() -> None:
    loader = DictLoader({"a": "{{ x | append: y }}"})
    env = Environment(loader=loader)
    source = "{% include 'a', x:y, z:42 %}{{ x }}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "y": [
                Variable(["y"], Span("", 18)),
                Variable(["y"], Span("a", 15)),
            ],
            "x": [Variable(["x"], Span("", 31))],
        },
        variables={
            "y": [
                Variable(["y"], Span("", 18)),
                Variable(["y"], Span("a", 15)),
            ],
            "x": [
                Variable(["x"], Span("a", 3)),
                Variable(["x"], Span("", 31)),
            ],
        },
        tags={"include": [Span("", 3)]},
        filters={"append": [Span("a", 7)]},
    )


def test_analyze_include_with_variable_name(env: Environment) -> None:
    source = "{% include b %}{{ x }}"
    template = env.from_string(source)

    with pytest.raises(TemplateNotFound):
        template.analyze()


def test_analyze_include_string_template_not_found(env: Environment) -> None:
    source = "{% include 'nosuchthing' %}{{ x }}"
    template = env.from_string(source)

    with pytest.raises(TemplateNotFound):
        template.analyze()


def test_analyze_render_assign() -> None:
    loader = DictLoader({"a": "{{ x }}{% assign y = 42 %}"})
    env = Environment(loader=loader)
    source = "{% render 'a' %}{{ y }}"

    _assert(
        env.from_string(source),
        locals={
            "y": [Variable(["y"], Span("a", 17))],
        },
        globals={
            "x": [Variable(["x"], Span("a", 3))],
            "y": [Variable(["y"], Span("", 19))],
        },
        tags={
            "render": [Span("", 3)],
            "assign": [Span("a", 10)],
        },
    )


def test_analyze_render_once() -> None:
    loader = DictLoader({"a": "{{ x }}"})
    env = Environment(loader=loader)
    source = "{% render 'a' %}{% render 'a' %}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "x": [Variable(["x"], Span("a", 3))],
        },
        tags={
            "render": [Span("", 3), Span("", 19)],
        },
    )


def test_analyze_render_recursive() -> None:
    loader = DictLoader({"a": "{{ x }}{% render 'a' %}"})
    env = Environment(loader=loader)
    source = "{% render 'a' %}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "x": [Variable(["x"], Span("a", 3))],
        },
        tags={
            "render": [
                Span("", 3),
                Span("a", 10),
            ],
        },
    )


def test_analyze_render_with_bound_variable() -> None:
    loader = DictLoader({"a": "{{ x | append: y }}{{ a }}"})
    env = Environment(loader=loader)
    source = "{% render 'a' with z %}"

    # Defaults to binding the value at `z` to the rendered template's name.

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "z": [Variable(["z"], Span("", 19))],
            "x": [Variable(["x"], Span("a", 3))],
            "y": [Variable(["y"], Span("a", 15))],
        },
        variables={
            "z": [Variable(["z"], Span("", 19))],
            "x": [Variable(["x"], Span("a", 3))],
            "y": [Variable(["y"], Span("a", 15))],
            "a": [Variable(["a"], Span("a", 22))],
        },
        tags={"render": [Span("", 3)]},
        filters={"append": [Span("a", 7)]},
    )


def test_analyze_render_with_bound_alias() -> None:
    loader = DictLoader({"a": "{{ x | append: y }}"})
    env = Environment(loader=loader)
    source = "{% render 'a' with z as y %}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "z": [Variable(["z"], Span("", 19))],
            "x": [Variable(["x"], Span("a", 3))],
        },
        variables={
            "z": [Variable(["z"], Span("", 19))],
            "x": [Variable(["x"], Span("a", 3))],
            "y": [Variable(["y"], Span("a", 15))],
        },
        tags={"render": [Span("", 3)]},
        filters={"append": [Span("a", 7)]},
    )


def test_analyze_render_with_arguments() -> None:
    loader = DictLoader({"a": "{{ x | append: y }}"})
    env = Environment(loader=loader)
    source = "{% render 'a', x:y, z:42 %}{{ x }}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "x": [Variable(["x"], Span("", 30))],
            "y": [
                Variable(["y"], Span("", 17)),
                Variable(["y"], Span("a", 15)),
            ],
        },
        variables={
            "x": [
                Variable(["x"], Span("a", 3)),
                Variable(["x"], Span("", 30)),
            ],
            "y": [
                Variable(["y"], Span("", 17)),
                Variable(["y"], Span("a", 15)),
            ],
        },
        tags={"render": [Span("", 3)]},
        filters={"append": [Span("a", 7)]},
    )


def test_analyze_render_template_not_found(env: Environment) -> None:
    source = "{% render 'nosuchthing' %}{{ x }}"
    template = env.from_string(source)

    with pytest.raises(TemplateNotFound):
        template.analyze()


def test_variable_segments(env: Environment) -> None:
    source = "{{ a['b.c'] }}{{ d[e.f][4] }}"

    _assert(
        env.from_string(source),
        locals={},
        globals={
            "a": [Variable(["a", "b.c"], Span("", 3))],
            "d": [Variable(["d", ["e", "f"], 4], Span("", 17))],
            "e": [Variable(["e", "f"], Span("", 19))],
        },
    )

    analysis = env.from_string(source).analyze()
    variables = list(itertools.chain.from_iterable(analysis.variables.values()))
    assert len(variables) == 3  # noqa: PLR2004
    assert variables[0].segments == ["a", "b.c"]
    assert variables[1].segments == ["d", ["e", "f"], 4]
    assert variables[2].segments == ["e", "f"]
    assert str(analysis.globals["a"][0]) == "a['b.c']"
    assert str(analysis.globals["d"][0]) == "d[e.f][4]"


def test_analyze_inheritance_chain() -> None:
    loader = DictLoader(
        {
            "base": (
                "Hello, "
                "{% assign x = 'foo' %}"
                "{% block content %}{{ x | upcase }}{% endblock %}!"
                "{% block foo %}{% endblock %}!"
            ),
            "other": (
                "{% extends 'base' %}"
                "{% block content %}{{ x | downcase }}{% endblock %}"
                "{% block foo %}{% assign z = 7 %}{% endblock %}"
            ),
            "some": (
                "{% extends 'other' %}{{ y | append: x }}{% block foo %}{% endblock %}"
            ),
        }
    )

    env = Environment(extra=True, loader=loader)

    _assert(
        env.get_template("some"),
        locals={
            "x": [Variable(["x"], Span("base", 17))],
            "z": [Variable(["z"], Span("other", 96))],
        },
        globals={
            "y": [Variable(["y"], Span("some", 24))],
        },
        variables={
            "x": [
                Variable(["x"], Span("base", 51)),
                Variable(["x"], Span("other", 42)),
                Variable(["x"], Span("some", 36)),
            ],
            "y": [Variable(["y"], Span("some", 24))],
        },
        tags={
            "assign": [
                Span("base", 10),
                Span("other", 89),
            ],
            "extends": [
                Span("some", 3),
                Span("other", 3),
            ],
            "block": [
                Span("base", 32),
                Span("base", 82),
                Span("other", 23),
                Span("other", 74),
                Span("some", 43),
            ],
        },
        filters={
            "append": [Span("some", 28)],
            "downcase": [Span("other", 46)],
            "upcase": [Span("base", 55)],
        },
    )


def test_analyze_recursive_extends() -> None:
    loader = DictLoader(
        {
            "some": "{% extends 'other' %}",
            "other": "{% extends 'some' %}",
        }
    )
    env = Environment(extra=True, loader=loader)
    template = env.get_template("some")

    _assert(
        template,
        locals={},
        globals={},
        tags={
            "extends": [
                Span("some", 3),
                Span("other", 3),
            ],
        },
    )


def test_analyze_super() -> None:
    loader = DictLoader(
        {
            "base": "Hello, {% block content %}{{ foo | upcase }}{% endblock %}!",
            "some": (
                "{% extends 'base' %}"
                "{% block content %}{{ block.super }}!{% endblock %}"
            ),
        }
    )

    env = Environment(extra=True, loader=loader)

    _assert(
        env.get_template("some"),
        locals={},
        globals={
            "foo": [Variable(["foo"], Span("base", 29))],
        },
        variables={
            "foo": [Variable(["foo"], Span("base", 29))],
            "block": [Variable(["block", "super"], Span("some", 42))],
        },
        tags={
            "extends": [
                Span("some", 3),
            ],
            "block": [
                Span("base", 10),
                Span("some", 23),
            ],
        },
        filters={
            "upcase": [Span("base", 35)],
        },
    )


def test_analyze_macro_and_call(env: Environment) -> None:
    source = (
        r"{% macro 'foo', you: 'World', arg: n %}"
        r"Hello, {{ you }}!"
        r"{% endmacro %}"
        r"{% call 'foo' %}"
        r"{% assign x = 'you' %}"
        r"{% call 'foo', you: x %}"
    )

    n = [Variable(["n"], Span("", 35))]
    you = [Variable(["you"], Span("", 49))]

    _assert(
        env.from_string(source),
        locals={"x": [Variable(["x"], Span("", 96))]},
        globals={"n": n},
        variables={"n": n, "you": you, "x": [Variable(["x"], Span("", 128))]},
        tags={
            "macro": [Span("", 3)],
            "call": [Span("", 73), Span("", 111)],
            "assign": [Span("", 89)],
        },
    )


def test_span_line_and_col(env: Environment) -> None:
    source = "\n".join(
        [
            r"{% for x in (1..y) %}",
            r"  {{ x }}",
            r"{% break %}",
            r"{% else %}",
            r"  {{ z }}",
            r"{% continue %}",
            r"{% endfor %}",
        ]
    )

    analysis = env.from_string(source).analyze()
    assert analysis.globals["y"][0].span.line_col(source) == (1, 16)
    assert analysis.variables["x"][0].span.line_col(source) == (2, 5)


# TODO:
# def test_analyze_translate(env: Environment) -> None:
#     source = (
#         "{%- translate, context: 'greeting', you: someone, count: 2 -%}"
#         "    Hello, {{ you }}!"
#         "{%- plural -%}"
#         "    Hello, {{ you }}s!"
#         "{%- endtranslate -%}"
#     )

#     someone = [Variable(["someone"], Span("", 41))]

#     _assert(
#         env.from_string(source),
#         locals={},
#         globals={"someone": someone},
#         variables={
#             "someone": someone,
#             "you": [
#                 Variable(["you"], Span("", 76)),
#                 Variable(["you"], Span("", 111)),
#             ],
#         },
#         tags={
#             "translate": [Span("", 0)],
#         },
#     )
