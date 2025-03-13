This page covers i18n and l10n filter and tag configuration, and how we support translations and translation message catalogs. See the [filter reference](optional_filters.md) and [tag reference](optional_tags.md) for usage examples.

## Currency

The `currency` filter returns the input number formatted as currency for the current locale. For usage examples see [`currency`](optional_filters.md#currency) in the filter reference.

### Options

`currency` defaults to looking for a locale in a render context variable called `locale`, and a currency code in a render context variable called `currency_code`. It outputs in the locale's standard format and falls back to `en_US` and `USD` if those context variables don't exist.

```python
from liquid import parse

template = parse("{{ 100457.99 | currency }}")

print(template.render())
print(template.render(currency_code="GBP"))
print(template.render(locale="de", currency_code="CAD"))
```

```plain title="output"
$100,457.99
£100,457.99
100.457,99 CA$
```

To configure `currency`, register a new instance of [`Currency`](api/extra.md#liquid.extra.Currency) with an [`Environment`](environment.md#managing-tags-and-filters), then render your templates from that. See [the API reference](api/extra.md#liquid.extra.Currency) for details of all arguments accepted by `Currency`.

```python
from liquid.extra import Currency
from liquid import Environment

env = Environment()
env.filters["currency"] = Currency(default_locale="de")
```

### Money

For convenience, some "money" filters are defined that mimic Shopify's money filter behavior. These are instances of [`Currency()`](api/extra.md#liquid.extra.Currency) with specific default formats. All other currency options are set to their defaults.

```python
from liquid import parse

template = parse("""\
{% assign amount = 10 %}
{{ amount | money }}
{{ amount | money_with_currency }}
{{ amount | money_without_currency }}
{{ amount | money_without_trailing_zeros }}""")

print(template.render(currency_code="CAD", locale="en_CA"))
```

```plain title="output"
$10.00
$10.00 CAD
10.00
$10
```

## DateTime

The `datetime` filter returns the input _datetime_ formatted for the current locale. For usage examples see [`datetime`](optional_filters.md#datetime) in the filter reference.

### Options

`datetime` defaults to looking for a timezone in a render context variable called `timezone`, a locale in a render context variable called `locale` and a datetime format in a render context variable called `datetime_format`.

```python
from liquid import parse

template = parse("{{ 'Apr 1, 2007, 3:30:00 PM' | datetime }}")

print(template.render())
print(template.render(locale="de", datetime_format="long"))
print(template.render(locale="de", timezone="CET", datetime_format="short"))
```

```plain title="output"
Apr 1, 2007, 3:30:00 PM
1. April 2007 um 15:30:00 UTC
01.04.07, 17:30
```

To configure `datetime`, register a new instance of [`DateTime`](api/extra.md#liquid.extra.DateTime) with an [`Environment`](environment.md#managing-tags-and-filters), then render your templates from that. See [the API reference](api/extra.md#liquid.extra.DateTime) for details of all arguments accepted by `DateTime`.

```python
from liquid.extra import DateTime
from liquid import Environment

env = Environment()
env.filters["datetime"] = DateTime(timezone_var="tz")
```

## Decimal

The `decimal` filter returns the input number formatted as a decimal for the current locale. For usage examples see [`decimal`](optional_filters.md#decimal) in the filter reference.

### Options

`decimal` defaults to looking for a locale in a render context variable called `locale`. It uses the locale's standard format and falls back to `en_US` if that variable does not exist.

```python
from liquid import parse

# Parse a number from a string in the default (en_US) input locale.
template = parse("""\
{{ '10,000.23' | decimal }}
{{ '10,000.23' | decimal: group_separator: false }}
""")

print(template.render(locale="de"))
print(template.render(locale="en_GB"))
```

```plain title="output"
10.000,23
10000,23

10,000.23
10000.23
```

To configure `decimal`, register a new instance of [`Number`](api/extra.md#liquid.extra.Number) with an [`Environment`](environment.md#managing-tags-and-filters), then render your templates from that.

```python
from liquid.extra import Number
from liquid import Environment

env = Environment()
env.filters["decimal"] = Number(default_locale="en_GB")
```

## Unit

The `unit` filter returns he input number formatted with the given units according to the current locale. For usage examples see [`unit`](optional_filters.md#unit) in the filter reference.

### Options

`unit` defaults to looking for a locale in a render context variable called `locale`, a length in a render context variable called `unit_length`, and a decimal format in a render context variable called `unit_format`.

```python
from liquid import parse

template = parse("""\
{{ 12 | unit: 'length-meter', format: '#,##0.00' }}
{{ 150 | unit: 'kilowatt', denominator_unit: 'hour' }}
""")

print(template.render(unit_length="long"))
print(template.render(locale="de", unit_length="long"))
```

```plain title="output"
12.00 meters
150 kilowatts per hour

12,00 Meter
150 Kilowatt pro Stunde
```

To configure `unit`, register a new instance of [`Unit`](api/extra.md#liquid.extra.Unit) with an [`Environment`](environment.md#managing-tags-and-filters), then render your templates from that.

```python
from liquid.extra import Unit
from liquid import Environment

env = Environment()
env.filters["unit"] = Unit(locale_var="_locale")
```

## Translations

Liquid Babel includes [`gettext`](optional_filters.md#gettext), [`ngettext`](optional_filters.md#ngettext), [`pgettext`](optional_filters.md#pgettext) and [`npgettext`](optional_filters.md#npgettext) filter equivalents to the functions found in [Python's gettext module](https://docs.python.org/3.10/library/gettext.html#gnu-gettext-api). Application developers can choose to use any of these filters, possibly using more user friendly filter names, and/or the more general [`t (translate)`](optional_filters.md#t) filter.

The [`t`](optional_filters.md#t) filter can behave like any of the \*gettext filters, depending on the arguments it is given. Where the \*gettext filters require positional arguments for `context`, `count` and `plural`, `t` reserves optional `count` and `plural` keyword arguments.

Liquid Babel also offers a [`{% translate %}`](optional_tags.md#translate) tag. This is similar to the [`{% trans %}`](https://jinja.palletsprojects.com/en/3.1.x/templates/#i18n) tag found in Jinja or the [`{% blocktranslate %}`](https://docs.djangoproject.com/en/4.1/topics/i18n/translation/#blocktranslate-template-tag) tag found in Django's template language. Again, application developers can configure and customize the included `translate` tag to suit an application's needs.

### Filters

[`gettext`](optional_filters.md#gettext), [`ngettext`](optional_filters.md#ngettext), [`npgettext`](optional_filters.md#npgettext), [`pgettext`](optional_filters.md#pgettext) and [`t`](optional_filters.md#t) filters all default to looking for [translations](#message-catalogs) in a render context variable called `translations`, falling back to an instance of [`NullTranslations`](https://docs.python.org/3.10/library/gettext.html#the-nulltranslations-class) if `translations` can not be resolved.

```python
from liquid import parse

# You'll need to load an appropriate Translations object.
# `get_translations()` is defined elsewhere.
translations = get_translations(locale="de")

template = parse("{{ 'Hello, World!' | t }}")
print(template.render(translations=translations))  # Hallo Welt!
```

To configure [`gettext`](optional_filters.md#gettext), [`ngettext`](optional_filters.md#ngettext), [`npgettext`](optional_filters.md#npgettext), [`pgettext`](optional_filters.md#pgettext) or [`t`](optional_filters.md#t), register a new instance of [`GetText`](api/extra.md#liquid.extra.GetText), [`NGetText`](api/extra.md#liquid.extra.NGetText), [`NPGetText`](api/extra.md#liquid.extra.NPGetText), [`PGetText`](api/extra.md#liquid.extra.PGetText) or [`Translate`](api/extra.md#liquid.extra.Translate) with an [`Environment`](environment.md#managing-tags-and-filters), then render your templates from that. All of these classes inherit from [`BaseTranslateFilter`](api/extra.md#liquid.extra.BaseTranslateFilter) and accept the same constructor arguments.

### Message catalogs

By default, all translation filters and tags will look for a render context variable called `translations`, which must be an object implementing the `Translations` protocol. It is the application developer's responsibility to provide a `Translations` object, being the interface between Liquid and a message catalog.

The `Translations` protocol is defined as follows. It is simply a subset of the [`NullTranslations`](https://docs.python.org/3.10/library/gettext.html#gettext.NullTranslations) class found in the [gettext module](https://docs.python.org/3.10/library/gettext.html#gnu-gettext-api).

```python
class Translations(Protocol):
    def gettext(self, message: str) -> str:
        ...

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        ...

    def pgettext(self, context: str, message: str) -> str:
        ...

    def npgettext(self, context: str, singular: str, plural: str, n: int) -> str:
        ...
```

It could be a [`GNUTranslations`](https://docs.python.org/3.10/library/gettext.html#the-gnutranslations-class) instance, a [Babel `Translations`](https://babel.pocoo.org/en/latest/support.html#extended-translations-class) instance, or any object implementing `gettext`, `ngettext`, `pgettext` and `npgettext` methods.

### Message variables

Translatable message text can contain placeholders for variables. When using variables in strings to be translated by filters, variables are defined using percent-style formatting. Only the `s` modifier is supported and every variable must have a name. In this example `you` is the variable name.

```liquid
{{ "Hello, %(you)s!" | t }}
```

Filter keyword arguments are merged with the current render context before being used to replace variables in message text. All variables are converted to their string representation before substitution. Dotted property/attribute access is not supported inside message variables.

```liquid
{{ "Hello, %(you)s!" | t: you: user.name }}
```

The [`translate`](optional_tags.md#translate) block tag recognizes simplified Liquid output statements as translation message variables. These variables must be valid identifiers without dotted or bracketed property/attribute access, and no filters.

```liquid
{% translate %}
    Hello, {{ you }}!
{% endtranslate %}
```

Keyword arguments passed to the [`translate`](optional_tags.md#translate) tag will be merged with the current render context before being used to replace variables in message text.

```liquid
{% translate you: user.name, count: users.size %}
    Hello, {{ you }}!
{% plural %}
    Hello, {{ you }}s!
{% endtranslate %}
```

### Message Extraction

Use the [`extract_from_templates()`](api/messages.md#liquid.extract_from_template) function to build a message [catalog](https://babel.pocoo.org/en/latest/api/messages/catalog.html#catalogs) from one or more templates. You are then free to make use of [Babel's PO file features](https://babel.pocoo.org/en/latest/api/messages/pofile.html), or convert the catalog to a more convenient internal representation.

```python
import io

from babel.messages.pofile import write_po

from liquid import parse
from liquid.messages import extract_from_templates

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

template = parse(source, name="something.liquid")
catalog = extract_from_templates(template)

buf = io.BytesIO()
write_po(buf, catalog, omit_header=True)
print(buf.getvalue().decode("utf-8"))
```

```plain title="output"
#. Translators: some comment
#: something.liquid:3
msgid "Hello, World!"
msgstr ""

#. Translators: other comment
#: something.liquid:5
#, python-format
msgid "Hello, %(you)s!"
msgid_plural "Hello, all!"
msgstr[0] ""
msgstr[1] ""
```

### Translator Comments

When a Liquid comment tag immediately precedes a translatable filter or tag, and the comment starts with a string in `comment_tags`, that comment will be included as a translator comment with the message. Use the `comment_tags` argument to [`extract_liquid()`](api/convenience.md#liquid.extract_liquid), or [`extract_from_templates()`](api/messages.md#liquid.extract_from_template) to change translator comment prefixes. The default is `["Translators:"]`.

```python
from liquid import parse
from liquid.messages import extract_from_templates

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

template = parse(source, name="something.liquid")
catalog = extract_from_templates(template, strip_comment_tags=True)

message = catalog.get("Hello, World!")
print(message.auto_comments[0])  # some comment
```
