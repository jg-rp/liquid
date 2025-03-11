import asyncio
import re

import pytest
from markupsafe import Markup

from liquid import Environment
from liquid import StrictUndefined
from liquid.exceptions import TranslationSyntaxError
from liquid.exceptions import UndefinedError

parse = Environment(extra=True).parse


class MockTranslations:
    """A mock translations class that returns all messages in upper case."""

    RE_VARS = re.compile(r"%\(\w+\)s")

    def gettext(self, message: str) -> str:
        return self._upper(message)

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        if n > 1:
            return self._upper(plural)
        return self._upper(singular)

    def pgettext(self, message_context: str, message: str) -> str:
        return message_context + "::" + self._upper(message)

    def npgettext(
        self, message_context: str, singular: str, plural: str, n: int
    ) -> str:
        if n > 1:
            return message_context + "::" + self._upper(plural)
        return message_context + "::" + self._upper(singular)

    def _upper(self, message: str) -> str:
        start = 0
        parts: list[str] = []
        for match in self.RE_VARS.finditer(message):
            parts.append(message[start : match.start()].upper())
            parts.append(match.group())
            start = match.end()

        parts.append(message[start:].upper())
        return Markup("").join(parts)


MOCK_TRANSLATIONS = MockTranslations()


def test_gettext_filter() -> None:
    source = "{{ 'Hello, World!' | gettext }}"
    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, World!"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "HELLO, WORLD!"


def test_gettext_from_context() -> None:
    source = "{{ foo | gettext }}"
    template = parse(source)
    # Default null translation
    assert template.render(foo="Hello, World!") == "Hello, World!"
    # Mock translation
    assert (
        template.render(
            translations=MOCK_TRANSLATIONS,
            foo="Hello, World!",
        )
        == "HELLO, WORLD!"
    )


def test_gettext_filter_with_variable() -> None:
    source = "{{ 'Hello, %(you)s!' | gettext: you: 'World' }}"
    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, World!"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "HELLO, World!"


def test_ngettext_filter() -> None:
    source = "{{ 'Hello, World!' | ngettext: 'Hello, Worlds!', 2 }}"
    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, Worlds!"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "HELLO, WORLDS!"


def test_pgettext_filter() -> None:
    source = "{{ 'Hello, World!' | pgettext: 'greeting' }}"
    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, World!"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "greeting::HELLO, WORLD!"


def test_npgettext_filter() -> None:
    source = "{{ 'Hello, World!' | npgettext: 'greeting', 'Hello, Worlds!', 2 }}"
    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, Worlds!"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "greeting::HELLO, WORLDS!"


def test_t_filter_gettext() -> None:
    source = "{{ 'Hello, World!' | t }}"
    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, World!"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "HELLO, WORLD!"


def test_t_filter_ngettext() -> None:
    source = "{{ 'Hello, World!' | t: plural: 'Hello, Worlds!', count: 2 }}"
    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, Worlds!"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "HELLO, WORLDS!"


def test_t_filter_pgettext() -> None:
    source = "{{ 'Hello, %(you)s!' | t: 'greeting', you: 'World' }}"
    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, World!"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "greeting::HELLO, World!"


def test_t_filter_npgettext() -> None:
    source = """
        {{-
            'Hello, %(you)s!' | t:
                'greeting',
                plural: 'Hello, %(you)ss!',
                count: 2,
                you: 'World'
        -}}
    """

    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, Worlds!"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "greeting::HELLO, WorldS!"


def test_translate_tag_gettext() -> None:
    source = """
        {%- translate you: 'World', there: false -%}
            Hello, {{ you }}!
        {%- endtranslate -%}
    """
    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, World!"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "HELLO, World!"

    async def coro() -> str:
        return await template.render_async(translations=MOCK_TRANSLATIONS)

    assert asyncio.run(coro()) == "HELLO, World!"


def test_translate_tag_ngettext() -> None:
    source = """
        {%- translate, you: 'World', count: 2 -%}
            Hello, {{ you }}!
        {%- plural -%}
            Hello, {{ you }}s!
        {%- endtranslate -%}
    """
    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, Worlds!"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "HELLO, WorldS!"

    async def coro() -> str:
        return await template.render_async(translations=MOCK_TRANSLATIONS)

    assert asyncio.run(coro()) == "HELLO, WorldS!"


def test_translate_tag_pgettext() -> None:
    source = """
        {%- translate context: 'greeting', you: 'World' -%}
            Hello, {{ you }}!
        {%- endtranslate -%}
    """
    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, World!"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "greeting::HELLO, World!"

    async def coro() -> str:
        return await template.render_async(translations=MOCK_TRANSLATIONS)

    assert asyncio.run(coro()) == "greeting::HELLO, World!"


def test_translate_tag_npgettext() -> None:
    source = """
        {%- translate, context: 'greeting', you: 'World', count: 2 -%}
            Hello, {{ you }}!
        {%- plural -%}
            Hello, {{ you }}s!
        {%- endtranslate -%}
    """
    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, Worlds!"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "greeting::HELLO, WorldS!"

    async def coro() -> str:
        return await template.render_async(translations=MOCK_TRANSLATIONS)

    assert asyncio.run(coro()) == "greeting::HELLO, WorldS!"


AUTO_ESCAPE_ENV = Environment(autoescape=True, extra=True)


def test_t_filter_auto_escape() -> None:
    data = {"s": "<b>Hello, World!</b>"}
    template = AUTO_ESCAPE_ENV.from_string("{{ s | t }}")

    # Default null translation
    assert template.render(**data) == "&lt;b&gt;Hello, World!&lt;/b&gt;"

    # Mock translation
    assert (
        template.render(translations=MOCK_TRANSLATIONS, **data)
        == "&LT;B&GT;HELLO, WORLD!&LT;/B&GT;"
    )


def test_translate_tag_message_trimming() -> None:
    source = """
        {%- translate you: 'World', there: false, other: 'foo' -%}
            Hello, {{ you }}!
            {{ other }}
        {%- endtranslate -%}
    """

    template = parse(source)
    # Default null translation
    assert template.render() == "Hello, World! foo"
    # Mock translation
    assert template.render(translations=MOCK_TRANSLATIONS) == "HELLO, World! foo"

    async def coro() -> str:
        return await template.render_async(translations=MOCK_TRANSLATIONS)

    assert asyncio.run(coro()) == "HELLO, World! foo"


def test_missing_translation_variables_are_undefined() -> None:
    template = parse("{{ 'Hello, %(you)s!' | gettext }}")
    assert template.render() == "Hello, !"

    env = Environment(undefined=StrictUndefined, extra=True)
    template = env.from_string("{{ 'Hello, %(you)s!' | gettext }}")
    with pytest.raises(UndefinedError):
        template.render()


def test_translate_bool_variable() -> None:
    template = parse("{{ 'Hello, %(you)s!' | gettext }}")
    assert template.render(you=True) == "Hello, true!"


def test_translate_none_variable() -> None:
    template = parse("{{ 'Hello, %(you)s!' | gettext }}")
    assert template.render(you=None) == "Hello, !"


def test_translate_list_variable() -> None:
    template = parse("{{ 'Hello, %(you)s!' | gettext }}")
    assert template.render(you=[1, 2, 3]) == "Hello, 123!"


def test_translate_range() -> None:
    template = parse("{% assign you = (1..4) %}{{ 'Hello, %(you)s!' | gettext }}")
    assert template.render() == "Hello, 1..4!"


def test_message_is_not_a_string() -> None:
    template = parse("{{ true | gettext }}")
    assert template.render() == "true"


def test_count_defaults_to_one() -> None:
    template = parse("{{ 'Hello, World!' | t: plural: 'Hello, Worlds!', count:'foo' }}")
    assert template.render() == "Hello, World!"


def test_filtered_block_translation_vars() -> None:
    source = """
        {%- translate you: 'World', count: 2 -%}
            Hello, {{ you | upcase }}!
        {%- plural -%}
            Hello, {{ you }}s!
        {%- endtranslate -%}
    """

    with pytest.raises(TranslationSyntaxError):
        parse(source)


def test_block_translation_paths() -> None:
    source = """
        {%- translate you: 'World', count: 2 -%}
            Hello, {{ some.thing }}!
        {%- plural -%}
            Hello, {{ you }}s!
        {%- endtranslate -%}
    """

    with pytest.raises(TranslationSyntaxError):
        parse(source)


def test_block_translation_literals() -> None:
    source = """
        {%- translate you: 'World', count: 2 -%}
            Hello, {{ 'foo' }}!
        {%- plural -%}
            Hello, {{ you }}s!
        {%- endtranslate -%}
    """

    with pytest.raises(TranslationSyntaxError):
        parse(source)


def test_block_translation_tags() -> None:
    source = """
        {%- translate -%}
            {% if true %}
                Hello, {{ 'foo' }}!
            {% endif %}
        {%- plural -%}
            Hello, {{ you }}s!
        {%- endtranslate -%}
    """

    with pytest.raises(TranslationSyntaxError):
        parse(source)


def test_block_translation_count_is_not_an_int() -> None:
    source = """
        {%- translate you: 'World', count: 'foo' -%}
            Hello, {{ you }}!
        {%- plural -%}
            Hello, {{ you }}s!
        {%- endtranslate -%}
    """

    assert parse(source).render() == "Hello, World!"
