import io

from babel.messages import Catalog
from babel.messages.extract import extract as babel_extract

from liquid import Environment
from liquid import extract_liquid
from liquid.messages import DEFAULT_KEYWORDS
from liquid.messages import extract_from_template
from liquid.messages import extract_from_templates

parse = Environment(extra=True, template_comments=True).parse


def test_gettext_filter() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{{ 'Hello, World!' | gettext }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 2
    assert message.funcname == "gettext"
    assert message.message == ("Hello, World!",)
    assert message.comments == []


def test_gettext_filter_with_inline_comment() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{% # Translators: greeting %}\n"
        "{{ 'Hello, World!' | gettext }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template, comment_tags=["Translators:"]))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 3
    assert message.funcname == "gettext"
    assert message.message == ("Hello, World!",)
    assert message.comments == ["Translators: greeting"]


def test_gettext_filter_with_block_comment() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{% comment %}Translators: greeting{% endcomment %}\n"
        "{{ 'Hello, World!' | gettext }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template, comment_tags=["Translators:"]))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 3
    assert message.funcname == "gettext"
    assert message.message == ("Hello, World!",)
    assert message.comments == ["Translators: greeting"]


def test_gettext_filter_with_comment_markup() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{# Translators: greeting #}\n"
        "{{ 'Hello, World!' | gettext }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template, comment_tags=["Translators:"]))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 3
    assert message.funcname == "gettext"
    assert message.message == ("Hello, World!",)
    assert message.comments == ["Translators: greeting"]


def test_preceding_comments() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{% # Translators: greeting %}\n"
        "\n"
        "{{ 'Hello, World!' | gettext }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template, comment_tags=["Translators:"]))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 4
    assert message.funcname == "gettext"
    assert message.message == ("Hello, World!",)
    assert message.comments == []


def test_multiple_preceding_comments() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{% # Translators: hello %}\n"
        "{% # Translators: greeting %}\n"
        "{{ 'Hello, World!' | gettext }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template, comment_tags=["Translators:"]))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 4
    assert message.funcname == "gettext"
    assert message.message == ("Hello, World!",)
    assert message.comments == ["Translators: greeting"]


def test_comment_without_tag() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{% # greeting %}\n"
        "{{ 'Hello, World!' | gettext }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template, comment_tags=["Translators:"]))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 3
    assert message.funcname == "gettext"
    assert message.message == ("Hello, World!",)
    assert message.comments == []


def test_gettext_filter_ignore_excess_args() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{{ 'Hello, World!' | gettext: 1 }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 2
    assert message.funcname == "gettext"
    assert message.message == ("Hello, World!",)
    assert message.comments == []


def test_ngettext_filter() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{{ 'Hello, World!' | ngettext: 'Hello, Worlds!', 2 }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 2
    assert message.funcname == "ngettext"
    assert message.message == ("Hello, World!", "Hello, Worlds!")
    assert message.comments == []


def test_ngettext_filter_missing_arg() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{{ 'Hello, World!' | ngettext }}\n"
        "{{ 'Hello, World!' | ngettext: 'Hello, Worlds!' }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 3
    assert message.funcname == "ngettext"
    assert message.message == ("Hello, World!", "Hello, Worlds!")
    assert message.comments == []


def test_ngettext_filter_excess_args() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{{ 'Hello, World!' | ngettext: 'Hello, Worlds!', 2, foo }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 2
    assert message.funcname == "ngettext"
    assert message.message == ("Hello, World!", "Hello, Worlds!")
    assert message.comments == []


def test_pgettext_filter() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{{ 'Hello, World!' | pgettext: 'greeting' }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 2
    assert message.funcname == "pgettext"
    assert message.message == (("greeting", "c"), "Hello, World!")
    assert message.comments == []


def test_npgettext_filter() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{{ 'Hello, World!' | npgettext: 'greeting', 'Hello, Worlds!', 2 }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 2
    assert message.funcname == "npgettext"
    assert message.message == (("greeting", "c"), "Hello, World!", "Hello, Worlds!")
    assert message.comments == []


def test_t_filter_gettext() -> None:
    source = "{{ 'Hello, World!' }}\n{{ 'Hello, World!' | t }}\n{{ 'Hello, World!' }}\n"

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 2
    assert message.funcname == "gettext"
    assert message.message == ("Hello, World!",)
    assert message.comments == []


def test_t_filter_ngettext() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{{ 'Hello, World!' | t: plural: 'Hello, Worlds!' }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 2
    assert message.funcname == "ngettext"
    assert message.message == ("Hello, World!", "Hello, Worlds!")
    assert message.comments == []


def test_t_filter_pgettext() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{{ 'Hello, World!' | t: 'greeting' }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 2
    assert message.funcname == "pgettext"
    assert message.message == (("greeting", "c"), "Hello, World!")
    assert message.comments == []


def test_t_filter_npgettext() -> None:
    source = (
        "{{ 'Hello, World!' }}\n"
        "{{ 'Hello, World!' | t: 'greeting', plural: 'Hello, Worlds!' }}\n"
        "{{ 'Hello, World!' }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 2
    assert message.funcname == "npgettext"
    assert message.message == (("greeting", "c"), "Hello, World!", "Hello, Worlds!")
    assert message.comments == []


def test_translate_tag_gettext() -> None:
    source = "{% translate %}Hello, World!{% endtranslate %}"
    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 1
    assert message.funcname == "gettext"
    assert message.message == ("Hello, World!",)
    assert message.comments == []


def test_translate_tag_pgettext() -> None:
    source = (
        "{% translate context: 'greetings everyone' %}Hello, World!{% endtranslate %}"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 1
    assert message.funcname == "pgettext"
    assert message.message == (("greetings everyone", "c"), "Hello, World!")
    assert message.comments == []


def test_translate_tag_ngettext() -> None:
    source = "{% translate %}Hello, World!{% plural %}Hello, Worlds!{% endtranslate %}"

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 1
    assert message.funcname == "ngettext"
    assert message.message == ("Hello, World!", "Hello, Worlds!")
    assert message.comments == []


def test_translate_tag_npgettext() -> None:
    source = (
        "{% translate context: 'greetings everyone' %}"
        "Hello, World!"
        "{% plural %}"
        "Hello, Worlds!"
        "{% endtranslate %}"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 1
    assert message.funcname == "npgettext"
    assert message.message == (
        ("greetings everyone", "c"),
        "Hello, World!",
        "Hello, Worlds!",
    )
    assert message.comments == []


def test_translate_tag_variable() -> None:
    source = "{% translate %}Hello, {{ you }}!{% endtranslate %}"

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 1
    assert message.funcname == "gettext"
    assert message.message == ("Hello, %(you)s!",)
    assert message.comments == []


def test_empty_translate_tag() -> None:
    source = "{% translate %}{% endtranslate %}"
    template = parse(source)
    messages = list(extract_from_template(template))
    assert len(messages) == 0


def test_translate_tag_with_comment() -> None:
    source = (
        "{% comment %}Translators: greeting{% endcomment %}\n"
        "{% translate %}Hello, World!{% endtranslate %}"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 2
    assert message.funcname == "gettext"
    assert message.message == ("Hello, World!",)
    assert message.comments == ["Translators: greeting"]


def test_ignore_non_string_messages() -> None:
    source = (
        "{{ some | t }}\n"
        "{{ some | gettext }}\n"
        "{{ some | ngettext: thing, 5 }}\n"
        "{{ some | pgettext: other }}\n"
        "{{ some | npgettext: other, thing, 5 }}\n"
    )

    template = parse(source)
    messages = list(extract_from_template(template))
    assert len(messages) == 0


def test_ignore_past_comments() -> None:
    source = (
        "{% comment %}Translators: something{% endcomment %}\n"
        "something\n"
        "{% translate %}Hello, World!{% endtranslate %}"
    )

    template = parse(source)
    messages = list(extract_from_template(template))

    assert len(messages) == 1
    message = messages[0]

    assert message.lineno == 3
    assert message.funcname == "gettext"
    assert message.message == ("Hello, World!",)
    assert message.comments == []


def test_translation_filters_must_come_first() -> None:
    source = "{{ 'Hello, World!' | upcase | t }}\n"
    template = parse(source)
    messages = list(extract_from_template(template))
    assert len(messages) == 0


def test_extract_liquid() -> None:
    source = """
    {% # Translators: some comment %}
    {{ 'Hello, World!' | t }}
    {% comment %}Translators: other comment{% endcomment %}
    {% translate count: 2 %}
        Hello, {{ you }}!
    {% plural %}
        Hello, all!
    {% endtranslate %}
    """

    messages = list(
        babel_extract(
            extract_liquid,
            io.StringIO(source),  # type: ignore
            keywords=DEFAULT_KEYWORDS,
            comment_tags=["Translators:"],
        )
    )

    assert len(messages) == 2
    assert messages == [
        (3, "Hello, World!", ["Translators: some comment"], None),
        (
            5,
            ("Hello, %(you)s!", "Hello, all!"),
            ["Translators: other comment"],
            None,
        ),
    ]


def test_extract_to_catalog() -> None:
    templates = [
        parse(
            """
                {% # Translators: some comment %}
                {{ 'Hello, World!' | t }}
                {% comment %}Translators: other comment{% endcomment %}
                {% translate count: 2 %}
                    Hello, {{ you }}!
                {% plural %}
                    Hello, all!
                {% endtranslate %}
                """,
            name="foo.liquid",
        ),
        parse(
            """
                {{ 'Hello, World!' | t }}
                {% comment %}Translators: salutation{% endcomment %}
                {% translate context: 'greeting', count: 2 %}
                    Goodbye, {{ you }}!
                {% plural %}
                    Goodbye, all!
                {% endtranslate %}
                """,
            name="bar.liquid",
        ),
    ]

    catalog = extract_from_templates(*templates)
    assert isinstance(catalog, Catalog)
    messages = list(catalog)
    assert len(messages) == 4


def test_strip_comment_tags() -> None:
    template = parse(
        """
        {% # Translators: some comment %}
        {{ 'Hello, World!' | t }}
        {% comment %}Translators: other comment{% endcomment %}
        {% translate count: 2 %}
            Hello, {{ you }}!
        {% plural %}
            Hello, all!
        {% endtranslate %}
        """,
        name="foo.liquid",
    )

    catalog = extract_from_templates(template, strip_comment_tags=True)
    assert catalog.get("Hello, World!").auto_comments[0] == "some comment"
