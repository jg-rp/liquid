# Python Liquid Babel

[Liquid Babel](https://github.com/jg-rp/liquid-babel) is a collection of optional [filters](../language/filters.md) and [tags](../language/tags.md) that facilitate the internationalization (i18n) and localization (i10n) of Liquid templates.

:::info
Liquid Babel uses [Python Babel](https://github.com/python-babel/babel). Please refer to the [Babel docs](https://babel.pocoo.org/en/latest/index.html) for more information about locales, currency codes and format strings.
:::

## Install

Install Python Liquid Babel using [pipenv](https://pipenv.pypa.io/en/latest/):

```shell
$ pipenv install liquid-babel
```

Or [pip](https://pip.pypa.io/en/stable/getting-started/):

```shell
$ python -m pip install -U liquid-babel
```

## Filters

Liquid Babel filters are implemented as Python classes. Pass options to a filter constructor, then register the resulting instance with a Liquid [`Environment`](../api/environment.md) by calling its [`add_filter()`](../api/environment.md#add_filter) method.

```python
from liquid import Environment
from liquid_babel.filters import Currency

env = Environment()
env.add_filter("currency", Currency(
    default_locale="en_CA",
    default_format="#,##0.00",
))

template = env.from_string("{{ 100457.99 | currency }}")
print(template.render())
```

## Tags

Liquid Babel tags can be registered with an [`Environment`](../api/environment.md) using its [`add_tag()`](../api/environment.md#addtag) method. [Tags](../api/tag.md) are configured by setting attributes on a subclass.

This example changes the name of the default `translation` block tag to `trans` and disables whitespace normalization in translation messages.

```python
from liquid import Environment
from liquid_babel.tags.translate import TranslateTag

class MyTranslateTag(TranslateTag):
    name = "trans"
    end = "endtrans"
    trim_messages = False

env = Environment()
env.add_tag(MyTranslateTag)

source = """
{%- trans count: worlds | size, you: 'World' -%}
    Hello, {{ you }}!
{%- plural -%}
    Hello, {{ you }}s!
{%- endtrans -%}
"""

template = env.from_string(source)

# With default NullTranslation
print(template.render())
```

## Translations

Liquid Babel includes [`gettext`](./filters.md#gettext), [`ngettext`](./filters.md#ngettext), [`pgettext`](./filters.md#pgettext) and [`npgettext`](./filters.md#npgettext) filter equivalents to the functions found in [Python's gettext module](https://docs.python.org/3.10/library/gettext.html#gnu-gettext-api). Application developers can choose to use zero or more of these filters, possibly using more user friendly filter names, and/or the more general [`t (translate)`](./filters.md#t) filter.

The [`t`](./filters.md#t) filter can behave like any of the \*gettext filters, depending on the arguments it is given. Where the \*gettext filters require positional arguments for `context`, `count` and `plural`, `t` reserves optional `count` and `plural` keyword arguments. See the [Liquid Babel filter reference](./filters.md) for filter configuration and usage examples.

Liquid Babel also offers a [`{% translate %}`](./tags.md#translate) tag. This is similar to the [`{% trans %}`](https://jinja.palletsprojects.com/en/3.1.x/templates/#i18n) tag found in Jinja or the [`{% blocktranslate %}`](https://docs.djangoproject.com/en/4.1/topics/i18n/translation/#blocktranslate-template-tag) tag found in Django's template language. Again, application developers can configure and customize the default `translate` filter to suit an application's needs. See the [Liquid Babel tag reference](./tags.md) for customization and usage examples.

### Message Catalogs

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

### Message Variables

Translatable message text can contain placeholders for variables. When using variables in strings to be translated by Liquid Babel filters, variables are defined using percent-style formatting. Only the `s` modifier is supported and every variable must have a name. In this example `you` is the variable name.

```liquid
{{ "Hello, %(you)s!" | t }}
```

:::tip
Message variables can be disabled by setting the `message_interpolation` argument to `False` when instantiating any of the included translation filters.
:::

Filter keyword arguments are merged with the current render context before being used to replace variables in message text. All variables are converted to their string representation before substitution. Dotted property/attribute access is not supported inside message variables.

```liquid
{{ "Hello, %(you)s!" | t: you: user.name }}
```

The `translation` block tag recognizes simplified Liquid output statements as translation message variables. These variables must be valid identifiers without dotted or bracketed property/attribute access, and no filters.

```liquid
{% translation %}
    Hello, {{ you }}!
{% endtranslation %}
```

Keyword arguments passed to the `translation` tag will be merged with the current render context before being used to replace variables in message text. These arguments can use simple, no-argument filters, like `size`. You should expect a `TranslationSyntaxError` if unexpected filters or filter arguments are used.

```liquid
{% translation you: user.name | capitalize, count: users | size %}
    Hello, {{ you }}!
{% plural %}
    Hello, {{ you }}s!
{% endtranslation %}
```

### Message Extraction

TODO:

### Translator Comments

TODO: