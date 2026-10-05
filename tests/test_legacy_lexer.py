from liquid._lexer_legacy import LegacyLexer
from liquid._tokens import *
from liquid._tokens import TokenKind, token_value
from liquid.environment import LiquidEnvironment


def tokenize(source: str) -> list[tuple[TokenKind, str]]:
    env = LiquidEnvironment()
    tokens = LegacyLexer.tokenize(env, source)
    return [(token[0], token_value(token, source)) for token in tokens]


def test_empty() -> None:
    assert tokenize("") == []


def test_just_text() -> None:
    assert tokenize("Hello, World!") == [(TOKEN_TEXT, "Hello, World!")]


def test_just_output() -> None:
    assert tokenize("{{ hello }}") == [
        (TOKEN_OUT_START, "{{"),
        (TOKEN_IDENT, "hello"),
        (TOKEN_OUT_END, "}}"),
    ]


def test_hello_liquid() -> None:
    assert tokenize("Hello, {{ you }}!") == [
        (TOKEN_TEXT, "Hello, "),
        (TOKEN_OUT_START, "{{"),
        (TOKEN_IDENT, "you"),
        (TOKEN_OUT_END, "}}"),
        (TOKEN_TEXT, "!"),
    ]


def test_output_whitespace_control() -> None:
    assert tokenize("Hello, {{- you -}}!") == [
        (TOKEN_TEXT, "Hello, "),
        (TOKEN_OUT_START, "{{"),
        (TOKEN_WC, "-"),
        (TOKEN_IDENT, "you"),
        (TOKEN_WC, "-"),
        (TOKEN_OUT_END, "}}"),
        (TOKEN_TEXT, "!"),
    ]


def test_output_single_quoted_string_literal() -> None:
    assert tokenize("{{ 'Hello, World!' }}") == [
        (TOKEN_OUT_START, "{{"),
        (TOKEN_SINGLE_QUOTE, "'"),
        (TOKEN_SINGLE_QUOTED, "Hello, World!"),
        (TOKEN_SINGLE_QUOTE, "'"),
        (TOKEN_OUT_END, "}}"),
    ]


def test_output_double_quoted_string_literal() -> None:
    assert tokenize('{{ "Hello, World!" }}') == [
        (TOKEN_OUT_START, "{{"),
        (TOKEN_DOUBLE_QUOTE, '"'),
        (TOKEN_DOUBLE_QUOTED, "Hello, World!"),
        (TOKEN_DOUBLE_QUOTE, '"'),
        (TOKEN_OUT_END, "}}"),
    ]


def test_output_filter() -> None:
    assert tokenize("{{ 42 | plus: 3 }}") == [
        (TOKEN_OUT_START, "{{"),
        (TOKEN_INT, "42"),
        (TOKEN_PIPE, "|"),
        (TOKEN_IDENT, "plus"),
        (TOKEN_COLON, ":"),
        (TOKEN_INT, "3"),
        (TOKEN_OUT_END, "}}"),
    ]


def test_output_float_literal() -> None:
    assert tokenize("{{ 42.2 | plus: 3.0 }}") == [
        (TOKEN_OUT_START, "{{"),
        (TOKEN_FLOAT, "42.2"),
        (TOKEN_PIPE, "|"),
        (TOKEN_IDENT, "plus"),
        (TOKEN_COLON, ":"),
        (TOKEN_FLOAT, "3.0"),
        (TOKEN_OUT_END, "}}"),
    ]


def test_output_range_literal() -> None:
    assert tokenize("{{ (1..5) | join: ', ' }}") == [
        (TOKEN_OUT_START, "{{"),
        (TOKEN_LPAREN, "("),
        (TOKEN_INT, "1"),
        (TOKEN_DOUBLE_DOT, ".."),
        (TOKEN_INT, "5"),
        (TOKEN_RPAREN, ")"),
        (TOKEN_PIPE, "|"),
        (TOKEN_IDENT, "join"),
        (TOKEN_COLON, ":"),
        (TOKEN_SINGLE_QUOTE, "'"),
        (TOKEN_SINGLE_QUOTED, ", "),
        (TOKEN_SINGLE_QUOTE, "'"),
        (TOKEN_OUT_END, "}}"),
    ]


def test_output_variable_with_trailing_question_mark() -> None:
    assert tokenize("{{ eh? }}") == [
        (TOKEN_OUT_START, "{{"),
        (TOKEN_IDENT, "eh?"),
        (TOKEN_OUT_END, "}}"),
    ]


def test_raw() -> None:
    assert tokenize("Hello, {% raw %}{{ you }}{% endraw %}!") == [
        (TOKEN_TEXT, "Hello, "),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "raw"),
        (TOKEN_TAG_END, "%}"),
        (TOKEN_TEXT, "{{ you }}"),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "endraw"),
        (TOKEN_TAG_END, "%}"),
        (TOKEN_TEXT, "!"),
    ]


def test_raw_at_eos() -> None:
    assert tokenize("Hello, {% raw %}{{ you }}{% endraw %}") == [
        (TOKEN_TEXT, "Hello, "),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "raw"),
        (TOKEN_TAG_END, "%}"),
        (TOKEN_TEXT, "{{ you }}"),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "endraw"),
        (TOKEN_TAG_END, "%}"),
    ]


def test_raw_whitespace_control() -> None:
    assert tokenize("Hello, {%- raw -%}{{ you }}{%- endraw -%}!") == [
        (TOKEN_TEXT, "Hello, "),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_WC, "-"),
        (TOKEN_TAG_NAME, "raw"),
        (TOKEN_WC, "-"),
        (TOKEN_TAG_END, "%}"),
        (TOKEN_TEXT, "{{ you }}"),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_WC, "-"),
        (TOKEN_TAG_NAME, "endraw"),
        (TOKEN_WC, "-"),
        (TOKEN_TAG_END, "%}"),
        (TOKEN_TEXT, "!"),
    ]


def test_tag_inline() -> None:
    assert tokenize("{% assign x = true %}") == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "assign"),
        (TOKEN_IDENT, "x"),
        (TOKEN_ASSIGN, "="),
        (TOKEN_TRUE, "true"),
        (TOKEN_TAG_END, "%}"),
    ]


# These test cases are derived from:
#
# https://github.com/Shopify/liquid/blob/a9c85622ddd784078c2eed34b19a351fe57362cf/test/unit/tags/comment_tag_unit_test.rb
#
# See https://github.com/Shopify/liquid/blob/main/LICENSE


def test_line_statements():
    source = """{% liquid
        if 1 != 1
        comment
        else
          echo 123
        endcomment
        endif
      %}"""

    assert tokenize(source) == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "liquid"),
        (TOKEN_TAG_START, ""),
        (TOKEN_TAG_NAME, "if"),
        (TOKEN_INT, "1"),
        (TOKEN_NE, "!="),
        (TOKEN_INT, "1"),
        (TOKEN_TAG_END, ""),
        (TOKEN_TAG_START, ""),
        (TOKEN_TAG_NAME, "comment"),
        (TOKEN_TAG_END, ""),
        (TOKEN_COMMENT, "\n        else\n          echo 123"),
        (TOKEN_TAG_START, ""),
        (TOKEN_TAG_NAME, "endcomment"),
        (TOKEN_TAG_END, ""),
        (TOKEN_TAG_START, ""),
        (TOKEN_TAG_NAME, "endif"),
        (TOKEN_TAG_END, ""),
        (TOKEN_TAG_END, "%}"),
    ]


def test_line_statements_nested():
    source = """{% liquid
        if 1 != 1
        comment
        comment
        else
          echo 123
        endcomment
        endcomment
        endif
      %}"""

    assert tokenize(source) == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "liquid"),
        (TOKEN_TAG_START, ""),
        (TOKEN_TAG_NAME, "if"),
        (TOKEN_INT, "1"),
        (TOKEN_NE, "!="),
        (TOKEN_INT, "1"),
        (TOKEN_TAG_END, ""),
        (TOKEN_TAG_START, ""),
        (TOKEN_TAG_NAME, "comment"),
        (TOKEN_TAG_END, ""),
        (
            TOKEN_COMMENT,
            "\n        comment\n        else\n          echo 123\n        endcomment",
        ),
        (TOKEN_TAG_START, ""),
        (TOKEN_TAG_NAME, "endcomment"),
        (TOKEN_TAG_END, ""),
        (TOKEN_TAG_START, ""),
        (TOKEN_TAG_NAME, "endif"),
        (TOKEN_TAG_END, ""),
        (TOKEN_TAG_END, "%}"),
    ]


def test_complete_markup():
    source = """{% comment %}
        {% if true %}
        {% if ... %}
        {%- for ? -%}
        {% while true %}
        {%
          unless if
        %}
        {% endcase %}
      {% endcomment %}"""

    assert tokenize(source) == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "comment"),
        (TOKEN_TAG_END, "%}"),
        (
            TOKEN_COMMENT,
            "\n        {% if true %}\n        {% if ... %}\n        {%- for ? -%}\n        {% while true %}\n        {%\n          unless if\n        %}\n        {% endcase %}\n      ",
        ),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "endcomment"),
        (TOKEN_TAG_END, "%}"),
    ]


def test_incomplete_markup():
    # NOTE: Shopify/liquid throws a SyntaxError here.
    source = """{% comment %}
          {% assign foo = "1"
        {% endcomment %}"""

    assert tokenize(source) == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "comment"),
        (TOKEN_TAG_END, "%}"),
        (TOKEN_COMMENT, '\n          {% assign foo = "1"\n        '),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "endcomment"),
        (TOKEN_TAG_END, "%}"),
    ]


def test_start_delimiters():
    # NOTE: Shopify/liquid throws a SyntaxError here.
    source = """{% comment %}
        {% {{ {%- endcomment %}"""

    assert tokenize(source) == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "comment"),
        (TOKEN_TAG_END, "%}"),
        (TOKEN_COMMENT, "\n        {% {{ "),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_WC, "-"),
        (TOKEN_TAG_NAME, "endcomment"),
        (TOKEN_TAG_END, "%}"),
    ]


def test_nested_comment_blocks_balanced():
    source = """{% comment %}
        {% comment %}
          {% comment %}{%    endcomment     %}
        {% endcomment %}
      {% endcomment %}"""

    assert tokenize(source) == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "comment"),
        (TOKEN_TAG_END, "%}"),
        (
            TOKEN_COMMENT,
            "\n        {% comment %}\n          {% comment %}{%    endcomment     %}\n        {% endcomment %}\n      ",
        ),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "endcomment"),
        (TOKEN_TAG_END, "%}"),
    ]


def test_nested_comment_blocks_unbalanced():
    # NOTE: Shopify/liquid throws a SyntaxError here.
    source = """{% comment %}
          {% comment %}
            {% comment %}
          {% endcomment %}
        {% endcomment %}"""

    assert tokenize(source) == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "comment"),
        (TOKEN_TAG_END, "%}"),
        (
            TOKEN_UNKNOWN,
            "\n          {% comment %}\n            {% comment %}\n          {% endcomment %}\n        {% endcomment %}",
        ),
    ]


def test_raw_block_balanced():
    source = """{% comment %}
        {% raw %}
          {% endcomment %}
        {% endraw %}
      {% endcomment %}"""

    assert tokenize(source) == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "comment"),
        (TOKEN_TAG_END, "%}"),
        (
            TOKEN_COMMENT,
            "\n        {% raw %}\n          {% endcomment %}\n        {% endraw %}\n      ",
        ),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "endcomment"),
        (TOKEN_TAG_END, "%}"),
    ]


def test_raw_block_unbalanced():
    # NOTE: Shopify/liquid throws a SyntaxError here.
    source = """{% comment %}
          {% raw %}
          {% endcomment %}
        {% endcomment %}"""

    assert tokenize(source) == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "comment"),
        (TOKEN_TAG_END, "%}"),
        (
            TOKEN_UNKNOWN,
            "\n          {% raw %}\n          {% endcomment %}\n        {% endcomment %}",
        ),
    ]


def test_junk_between_nested_endcomment_and_delimiter():
    source = """{% comment %}
          {% comment %}
          {% endcomment
          {% if true %}
          {% endif %}
        {% endcomment %}"""

    assert tokenize(source) == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "comment"),
        (TOKEN_TAG_END, "%}"),
        (
            TOKEN_COMMENT,
            "\n          {% comment %}\n          {% endcomment\n          {% if true %}\n          {% endif %}\n        ",
        ),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "endcomment"),
        (TOKEN_TAG_END, "%}"),
    ]


def test_junk_between_nested_comment_and_delimiter():
    source = """{% comment %}
          {% comment
            {% assign foo = 1 %}
          {% endcomment
          {% assign foo = 1 %}
        {% endcomment %}"""

    assert tokenize(source) == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "comment"),
        (TOKEN_TAG_END, "%}"),
        (
            TOKEN_COMMENT,
            "\n          {% comment\n            {% assign foo = 1 %}\n          {% endcomment\n          {% assign foo = 1 %}\n        ",
        ),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "endcomment"),
        (TOKEN_TAG_END, "%}"),
    ]


def test_junk_between_endcomment_and_delimiter():
    source = "{% comment %}123{% endcomment\n   xyz  endcomment %}"

    assert tokenize(source) == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "comment"),
        (TOKEN_TAG_END, "%}"),
        (TOKEN_COMMENT, "123"),
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_NAME, "endcomment"),
        (TOKEN_IDENT, "xyz"),
        (TOKEN_IDENT, "endcomment"),
        (TOKEN_TAG_END, "%}"),
    ]


# These test cases are derived from:
#
# https://github.com/Shopify/liquid/blob/a9c85622ddd784078c2eed34b19a351fe57362cf/test/integration/tags/liquid_tag_test.rb
#
# See https://github.com/Shopify/liquid/blob/main/LICENSE


def test_liquid_tags() -> None:
    source = """{%- liquid
        echo array | join: " "
      -%}"""

    assert tokenize(source) == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_WC, "-"),
        (TOKEN_TAG_NAME, "liquid"),
        (TOKEN_TAG_START, ""),
        (TOKEN_TAG_NAME, "echo"),
        (TOKEN_IDENT, "array"),
        (TOKEN_PIPE, "|"),
        (TOKEN_IDENT, "join"),
        (TOKEN_COLON, ":"),
        (TOKEN_DOUBLE_QUOTE, '"'),
        (TOKEN_DOUBLE_QUOTED, " "),
        (TOKEN_DOUBLE_QUOTE, '"'),
        (TOKEN_TAG_END, ""),
        (TOKEN_WC, "-"),
        (TOKEN_TAG_END, "%}"),
    ]


# These test cases are derived from:
#
# https://github.com/Shopify/liquid/blob/a9c85622ddd784078c2eed34b19a351fe57362cf/test/unit/tokenizer_unit_test.rb
#
# See https://github.com/Shopify/liquid/blob/main/LICENSE


def test_output_single_closing_brace() -> None:
    assert tokenize("{{.} ") == [
        (TOKEN_OUT_START, "{{"),
        (TOKEN_DOT, "."),
        (TOKEN_OUT_END, "}"),
        (TOKEN_TEXT, " "),
    ]


def test_output_extra_closing_brace() -> None:
    assert tokenize("{{}}}") == [
        (TOKEN_OUT_START, "{{"),
        (TOKEN_OUT_END, "}}"),
        (TOKEN_TEXT, "}"),
    ]


def test_output_single_closing_brace_followed_by_closing_tag_delimiter() -> None:
    assert tokenize("{{}%}") == [
        (TOKEN_OUT_START, "{{"),
        (TOKEN_OUT_END, "}"),
        (TOKEN_TEXT, "%}"),
    ]


def test_output_close_with_tag_delimiter() -> None:
    assert tokenize("{{%}") == [
        (TOKEN_OUT_START, "{{"),
        (TOKEN_OUT_END, "%}"),
    ]


def test_output_percents() -> None:
    assert tokenize("{{%%%}}") == [
        (TOKEN_OUT_START, "{{"),
        (TOKEN_UNKNOWN, "%"),
        (TOKEN_UNKNOWN, "%"),
        (TOKEN_UNKNOWN, "%"),
        (TOKEN_OUT_END, "}}"),
    ]


def test_open_tag_close_output() -> None:
    assert tokenize("{%}}") == [
        (TOKEN_TEXT, "{%}}"),
    ]


def test_tag_followed_by_brace() -> None:
    assert tokenize("{%%}}") == [
        (TOKEN_TAG_START, "{%"),
        (TOKEN_TAG_END, "%}"),
        (TOKEN_TEXT, "}"),
    ]
