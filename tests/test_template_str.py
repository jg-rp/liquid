"""Test that templates can be serialized back to a string."""

from liquid import parse


def test_content_str() -> None:
    template = parse("Hello\n")
    assert str(template) == "Hello\n"


def test_output_str() -> None:
    template = parse("{{ a.b }}")
    assert str(template) == "{{ a.b }}"


def test_assign_str() -> None:
    template = parse("{% assign x = y %}")
    assert str(template) == "{% assign x = y %}"


def test_capture_str() -> None:
    source = "{% capture foo %}Hello, {{ you }}!{% endcapture %}"
    template = parse(source)
    assert str(template) == source


def test_case_str() -> None:
    source = "{% case 'a' %}{% when 'b', c %}c{% when 'd' %}e{% else %}f{% endcase %}"
    template = parse(source)
    assert str(template) == source


def test_case_str_whitespace() -> None:
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
    template = parse(source)
    assert str(template) == source


def test_cycle_str() -> None:
    source = "{% cycle 1, 2, 3 %}"
    template = parse(source)
    assert str(template) == source


def test_cycle_str_with_name() -> None:
    source = "{% cycle foo: 1, 2, 3 %}"
    template = parse(source)
    assert str(template) == source


def test_decrement_str() -> None:
    source = "{% decrement foo %}"
    template = parse(source)
    assert str(template) == source


def test_increment_str() -> None:
    source = "{% increment foo %}"
    template = parse(source)
    assert str(template) == source


def test_echo_str() -> None:
    source = "{% echo foo | upcase if bar else baz %}"
    template = parse(source)
    assert str(template) == source


def test_extends_str() -> None:
    source = "{% extends 'foo' %}"
    template = parse(source)
    assert str(template) == source


def test_block_str() -> None:
    template = parse("{% block b required %}{{ greeting }}, {{ x }}! {% endblock %}")
    assert (
        str(template)
        == "{% block b required %}{{ greeting }}, {{ x }}! {% endblock b %}"
    )


def test_for_str() -> None:
    source = "{% for a in b %}{{ a }},{% else %}c{% endfor %}"
    template = parse(source)
    assert str(template) == source

    source = "{%- for a in b ~%}{{ a }},{%~ else -%}c{%~ endfor %}"
    template = parse(source)
    assert str(template) == source


def test_break_and_continue_str() -> None:
    source = (
        "{% for a in b %}"
        "{% if true %}{% continue %}{% else %}{% break %}{% endif %}"
        "{% endfor %}"
    )
    template = parse(source)
    assert str(template) == source


def test_if_str() -> None:
    source = "{% if false %}a{% elsif false %}b{% else %}c{% endif %}"
    template = parse(source)
    assert str(template) == source


def test_unless_str() -> None:
    source = "{% unless false %}a{% elsif false %}b{% else %}c{% endunless %}"
    template = parse(source)
    assert str(template) == source


def test_include_str() -> None:
    source = "{% include foo %}"
    template = parse(source)
    assert str(template) == source


def test_include_str_with_alias() -> None:
    source = "{% include 'a' with b.c[1] as x, y:42 %}"
    template = parse(source)
    assert str(template) == source


def test_render_str() -> None:
    source = "{% render 'foo' %}"
    template = parse(source)
    assert str(template) == source


def test_render_str_with_alias() -> None:
    source = "{% render 'a' for b.c[1] as x, y:42 %}"
    template = parse(source)
    assert str(template) == source


def test_liquid_str() -> None:
    source = "{% liquid echo 'a'\nassign b = 'c'\necho b %}"
    template = parse(source)
    assert str(template) == source


def test_liquid_comment_str() -> None:
    source = "{% liquid echo 'a'\n# some comment\nassign b = 'c'\necho b %}"
    template = parse(source)
    assert str(template) == source


def test_liquid_block_comment_str() -> None:
    source = "{% liquid\ncomment\necho 'b'\nendcomment %}"
    template = parse(source)
    assert str(template) == source


def test_liquid_str_with_trailing_newline() -> None:
    template = parse("{% liquid echo 'a'\nassign b = 'c'\necho b\n\n%}")
    assert str(template) == "{% liquid echo 'a'\nassign b = 'c'\necho b %}"


def test_raw_str() -> None:
    source = "{% raw %}{{ a }}{% endraw %}"
    template = parse(source)
    assert str(template) == source


def test_logical_expression_str() -> None:
    template = parse(
        "{% if not (true and (false and (false or a < b))) %}Hello{% endif %}"
    )
    assert (
        str(template)
        == "{% if not (true and false and (false or a < b)) %}Hello{% endif %}"
    )


def test_ternary_str() -> None:
    source = "{{ foo | upcase if bar else baz || append: '!' }}"
    template = parse(source)
    assert str(template) == source


def test_ternary_str_no_alternative() -> None:
    source = "{{ foo | upcase if a <= b }}"
    template = parse(source)
    assert str(template) == source


def test_inline_comment_str() -> None:
    source = "{% # this is a comment %}"
    template = parse(source)
    assert str(template) == source


def test_block_comment_str() -> None:
    source = "{% comment %}don't render me{% endcomment %}"
    template = parse(source)
    assert str(template) == source


# def test_translate_str() -> None:
#     source = "\n".join(
#         [
#             "{% translate x:'foo', y:'bar' %}",
#             "  Hello, {{ you }}{% plural %}  Hello, {{ you }}s{% endtranslate %}",
#         ]
#     )
#     template = parse(source)
#     assert str(template) == source


# def test_macro_and_call_str() -> None:
#     source = "\n".join(
#         [
#             "{% macro func greeting, you:a.b %}",
#             "  {{ greeting }}, {{ you }}!",
#             "{% endmacro %}",
#             "{% call func 'Hello' %}",
#             "{% call func 'Goodbye', you:'Liquid' %}",
#         ]
#     )
#     template = parse(source)
#     assert str(template) == source


# def test_with_str() -> None:
#     source = "\n".join(
#         [
#             "{% with a:1, b:3.4 %}",
#             "  {{ a }} + {{ b }} = {{ a | plus: b }}",
#             "{% endwith %}",
#         ]
#     )
#     template = parse(source)
#     assert str(template) == source
