# Babel Filters

Optional [filters](../language/filters.md) provided by the [liquid-babel](./introduction.md) package.

:::info
Liquid Babel uses [Python Babel](https://github.com/python-babel/babel). Please refer to the [Babel docs](https://babel.pocoo.org/en/latest/index.html) for more information about working with message catalogs, locales, currency codes and format strings.
:::

## Currency

`<number> | currency[: group_separator: <boolean>] -> <string>`

Currency (aka money) formatting. Return the input number formatted as currency for the current locale.

```liquid
{{ 100457.99 | currency }}
```

```plain title="output"
$100,457.99
```

Use the `group_separator` argument to control the output of the current locale's group separators.

```liquid
{{ 100457.99 | currency: group_separator: false }}
```

```plain title="output"
$100457.99
```

If the input number is a string, it will be parsed to a decimal according to the current _input locale_.

```liquid
{% with input_locale: "de", locale: "en_CA" %}
  {{ "100.457,99" | currency }}
{% endwith %}
```

```plain title="output"
US$100,457.99
```

### Options

Instances of the `Currency` class default to looking for a locale in a render context variable called `locale`, and a currency code in a render context variable called `currency_code`. It outputs in the locale's standard format and falls back to `en_US` and `USD` if those context variables don't exist.

```python
from liquid import Environment
from liquid_babel.filters import Currency

env = Environment()
env.add_filter("currency", Currency())

template = env.from_string("{{ 100457.99 | currency }}")

print(template.render())
print(template.render(currency_code="GBP"))
print(template.render(locale="de", currency_code="CAD"))
```

```plain title="output"
$100,457.99
£100,457.99
100.457,99 CA$
```

This table shows the available `Currency()` constructor arguments.

| Argument                | Type            | Description                                                                                                                                      | Default             |
| ----------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- |
| `currency_code_var`     | `str`           | The name of a render context variable that resolves to the current currency code.                                                                | `"currency_code"`   |
| `default_currency_code` | `str`           | A fallback currency code if `currency_code_var` can not be resolved.                                                                             | `"USD"`             |
| `locale_var`            | `str`           | The name of a render context variable that resolves to the current locale.                                                                       | `"locale"`          |
| `default_locale`        | `str`           | A fallback locale to use if `locale_var` can not be resolved.                                                                                    | `"en_US"`           |
| `format_var`            | `str`           | The name of a render context variable that resolves to the current currency format string.                                                       | `"currency_format"` |
| `default_format`        | `Optional[str]` | A fallback currency format that is used if `format_var` can not be resolved. If `None`, the standard format for the current locale will be used. | `None`              |
| `currency_digits`       | `bool`          | Indicates if the format should override locale specific trailing digit behavior.                                                                 | `True`              |
| `input_locale_var`      | `str`           | The name of a render context variable that resolves to a locale suitable for parsing input strings to decimals.                                  | `"input_locale"`    |
| `default_input_locale`  | `str`           | A fallback locale to use if `input_locale_var` can not be resolved.                                                                              | `"en_US"`           |

### Money

For convenience, some "money" filters are defined that mimic Shopify's money filter behavior. These are instances of `Currency` with specific default formats. All other currency options are set to their defaults.

```python
from liquid import Environment
from liquid_babel.filters import money
from liquid_babel.filters import money_with_currency
from liquid_babel.filters import money_without_currency
from liquid_babel.filters import money_without_trailing_zeros

env = Environment()
env.add_filter("money", money)
env.add_filter("money_with_currency", money_with_currency)
env.add_filter("money_without_currency", money_without_currency)
env.add_filter("money_without_trailing_zeros", money_without_trailing_zeros)

template = env.from_string("""\
{% assign amount = 10 %}
{{ amount | money }}
{{ amount | money_with_currency }}
{{ amount | money_without_currency }}
{{ amount | money_without_trailing_zeros }}
""")

print(template.render(currency_code="CAD", locale="en_CA"))
```

```plain title="output"
$10.00
$10.00 CAD
10.00
$10
```

## DateTime

`<datetime> | datetime[: format: <string>] -> <string>`

Date and time formatting. Return the input _datetime_ formatted according to the current locale. If `dt` is a `datetime.datetime` object `datetime.datetime(2007, 4, 1, 15, 30)`.

```liquid
{{ dt | datetime }}
```

```plain title="output"
Apr 1, 2007, 3:30:00 PM
```

The optional `format` argument can be one of `'short'`, `'medium'`, `'long'`, `'full'` or a custom format string. `format` defaults to `'medium'`.

```liquid
{% with timezone: 'America/New_York' %}
  {{ dt | datetime: format: 'full' }}
{% endwith %}
```

```plain title="output"
Sunday, April 1, 2007 at 11:30:00 AM Eastern Daylight Time
```

If the input _datetime_ is a string, it will be parsed to a datetime object.

```liquid
{% with locale: 'en_GB' %}
  {{ "Apr 1, 2007, 3:30:00 PM UTC+4" | datetime: format: 'short' }}
{% endwith %}
```

```plain title="output"
01/04/2007, 19:30
```

### Options

Instances of the `DateTime` class default to looking for a timezone in a render context variable called `timezone`, a locale in a render context variable called `locale` and a datetime format in a render context variable called `datetime_format`.

```python
from liquid import Environment
from liquid_babel.filters import DateTime

env = Environment()
env.add_filter("datetime", DateTime())

template = env.from_string("{{ 'Apr 1, 2007, 3:30:00 PM' | datetime }}")

print(template.render())
print(template.render(locale="de", datetime_format="long"))
print(template.render(locale="de", timezone="CET", datetime_format="short"))
```

```plain title="output"
Apr 1, 2007, 3:30:00 PM
1. April 2007 um 15:30:00 UTC
01.04.07, 17:30
```

This table shows the available `DateTime()` constructor arguments.

| Argument                 | Type  | Description                                                                                                 | Default             |
| ------------------------ | ----- | ----------------------------------------------------------------------------------------------------------- | ------------------- |
| `timezone_var`           | `str` | The name of a render context variable that resolves to a timezone.                                          | `"timezone"`        |
| `default_timezone`       | `str` | A fallback timezone to use if `timezone_var` can not be resolved.                                           | `"UTC"`             |
| `locale_var`             | `str` | The name of a render context variable that resolves to the current locale.                                  | `"locale"`          |
| `default_locale`         | `str` | A fallback locale to use if `locale_var` can not be resolved.                                               | `en_US"`            |
| `format_var`             | `str` | The name of a render context variable that resolves to the current datetime format string.                  | `"datetime_format"` |
| `default_format`         | `str` | A fallback datetime format that is used if `format_var` can not be resolved.                                | `"medium"`          |
| `input_timezone_var`     | `str` | The name of a render context variable that resolves to a timezone for parsing datetimes entered as strings. | `"input_timezone"`  |
| `default_input_timezone` | `str` | A fallback timezone to use if `input_timezone_var` can not be resolved.                                     | `"UTC"`             |

## Decimal / Number

`<number> | decimal[: group_separator: <boolean>] -> <string>`

Decimal number formatting. Return the input number formatted as a decimal for the current locale.

```liquid
{{ '10000.233' | decimal }}
```

```plain title="output"
10,000.233
```

Use the `group_separator` argument to control the output of the current locale's group separators.

```liquid
{{ '10000.233' | decimal: group_separator: false }}
```

```plain title="output"
10000.233
```

If the input number is a string, it will be parsed to a decimal according to the current _input locale_.

```liquid
{% with input_locale: "de" %}
  {{ "100.457,00" | decimal }}
{% endwith %}
```

```plain title="output"
100,457
```

### Options

Instances of the `Number` class default to looking for a locale in a render context variable called `locale`. It uses the locale's standard format and falls back to `en_US` if that variable does not exist.

```python
from liquid import Environment
from liquid_babel.filters import Number

env = Environment()
# Register an instance of the `Number` class as a filter called "decimal".
env.add_filter("decimal", Number())

# Parse a number from a string in the default (en_US) input locale.
template = env.from_string("""\
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

This table shows the available `Number()` constructor arguments.

| Argument                       | Type            | Description                                                                                                                                      | Default             |
| ------------------------------ | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- |
| `decimal_quantization_var`     | `str`           | The name of a render context variable that resolves to the decimal quantization to be used.                                                      | `"currency_code"`   |
| `default_decimal_quantization` | `bool`          | A fallback decimal quantization if `decimal_quantization_var` can not be resolved.                                                               | `"USD"`             |
| `locale_var`                   | `str`           | The name of a render context variable that resolves to the current locale.                                                                       | `"locale"`          |
| `default_locale`               | `str`           | A fallback locale to use if `locale_var` can not be resolved.                                                                                    | `"en_US"`           |
| `format_var`                   | `str`           | The name of a render context variable that resolves to the current currency format string.                                                       | `"currency_format"` |
| `default_format`               | `Optional[str]` | A fallback currency format that is used if `format_var` can not be resolved. If `None`, the standard format for the current locale will be used. | `None`              |
| `input_locale_var`             | `str`           | The name of a render context variable that resolves to a locale suitable for parsing input strings to decimals.                                  | `"input_locale"`    |
| `default_input_locale`         | `str`           | A fallback locale to use if `input_locale_var` can not be resolved.                                                                              | `"en_US"`           |

## Translation

Instances of the following translation filters default to looking for [Translations](./introduction.md#message-catalogs) in a render context variable called `translations`, falling back to an instance of [`NullTranslations`](https://docs.python.org/3.10/library/gettext.html#the-nulltranslations-class) if `translations` can not be resolved.

```python
from liquid import Environment
from liquid_babel.filters import GetText

env = Environment()
# Register an instance of the GetText filter as `t`.
env.add_filter("t", GetText())

# You'll need to load an appropriate Translations object.
# `get_translations()` is defined elsewhere.
translations = get_translations(locale="de")

template = env.from_string("{{ 'Hello, World!' | t }}")
print(template.render(translations=translations))  # Hallo Welt!
```

This table show the options available when instantiating `Translate` (aka `t`), `GetText`, `NGetText`, `PGetText` and `NPGetText` filters.

| Argument                | Type                     | Description                                                                                                                | Default            |
| ----------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| `translations_var`      | `str`                    | The name of a render context variable that resolves to a `Translations` object.                                            | `"translations"`   |
| `default_translations`  | `Optional[Translations]` | A fallback `Translations` object used if `translations_var` can not be resolved.                                           | `NullTranslations` |
| `message_interpolation` | `bool`                   | If `True`, do percent-style variable substitution when rendering message text.                                             | `True`             |
| `autoescape_message`    | `bool`                   | If `True` and the current environment has `autoescape` set to `True`, translatable messages will be escaped before output. | `False`            |

To register all included translation filters with an environment, use `register_translation_filters(env)`. It too accepts the arguments described in the table above.

```python
from liquid import Environment
from liquid_babel.filters import register_translation_filters

env = Environment()
# Register `t`, `gettext`, `ngettext`, `pgettext` and `npgettext`
# with HTML auto escaping enabled.
register_translation_filters(env, autoescape_message=True)
```

### t

`<string> | t[: <string>[, <identifier>: <object>, ... ]] -> <string>`

Template internationalization. Return the localized translation of the input message. If a German [Translations](./introduction.md#message-catalogs) object is found in the current render context:

```liquid
{{ "Hello, World!" | t }}
```

```plain title="output"
Hallo Welt!
```

If given, the first and only positional argument is a message context string. It will be used to give translators extra information about where the message is to be used. With the default configuration, keyword arguments `plural` and `count` are reserved for specifying a pluralizable message.

```liquid
{{ "Hello, World!" | t: plural: 'Hello, Worlds!', count: 2 }}
```

```plain title="output"
Hallo Welten!
```

The remaining keyword arguments are used to populate translatable message variables. If `user.name` is `"Sally"`:

```liquid
{{ "Hello, %(you)s" | t: you: user.name }}
```

```plain title="output"
Hallo Sally!
```

### gettext

TODO

### ngettext

TODO

### pgettext

TODO

### npgettext
