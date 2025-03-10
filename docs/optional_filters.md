## currency

```
<number> | currency[: group_separator: <boolean>] -> <string>
```

Currency (aka money) formatting. Return the input number formatted as currency for the current locale. See also [`money`](#money).

```liquid2
{{ 100457.99 | currency }}
```

```plain title="output"
$100,457.99
```

Use the `group_separator` argument to control the output of the current locale's group separators.

```liquid2
{{ 100457.99 | currency: group_separator: false }}
```

```plain title="output"
$100457.99
```

If the input number is a string, it will be parsed to a decimal according to the current _input locale_.

```liquid2
{% with input_locale: "de", locale: "en_CA" %}
  {{ "100.457,99" | currency }}
{% endwith %}
```

```plain title="output"
US$100,457.99
```

## datetime

```
<datetime> | datetime[: format: <string>] -> <string>
```

Date and time formatting. Return the input _datetime_ formatted according to the current locale. If `dt` is a `datetime.datetime` object `datetime.datetime(2007, 4, 1, 15, 30)`.

```liquid2
{{ dt | datetime }}
```

```plain title="output"
Apr 1, 2007, 3:30:00 PM
```

The optional `format` argument can be one of `'short'`, `'medium'`, `'long'`, `'full'` or a custom format string. `format` defaults to `'medium'`.

```liquid2
{% with timezone: 'America/New_York' %}
  {{ dt | datetime: format: 'full' }}
{% endwith %}
```

```plain title="output"
Sunday, April 1, 2007 at 11:30:00 AM Eastern Daylight Time
```

If the input _datetime_ is a string, it will be parsed to a datetime object.

```liquid2
{% with locale: 'en_GB' %}
  {{ "Apr 1, 2007, 3:30:00 PM UTC+4" | datetime: format: 'short' }}
{% endwith %}
```

```plain title="output"
01/04/2007, 19:30
```

## decimal

```
<number> | decimal[: group_separator: <boolean>] -> <string>
```

Decimal number formatting. Return the input number formatted as a decimal for the current locale.

```liquid2
{{ '10000.233' | decimal }}
```

```plain title="output"
10,000.233
```

Use the `group_separator` argument to control the output of the current locale's group separators.

```liquid2
{{ '10000.233' | decimal: group_separator: false }}
```

```plain title="output"
10000.233
```

If the input number is a string, it will be parsed to a decimal according to the current _input locale_.

```liquid2
{% with input_locale: "de" %}
  {{ "100.457,00" | decimal }}
{% endwith %}
```

```plain title="output"
100,457
```

## gettext

```
<string> | gettext[: <identifier>: <object> ... ]
```

Return the localized translation of the input message without pluralization or message context.

```liquid2
{{ "Hello, World!" | gettext }}
```

```plain title="output"
Hallo Welt!
```

Any keyword arguments are used to populate message variables. If `user.name` is `"Sue"`:

```liquid2
{{ "Hello, %(you)s" | gettext: you: user.name }}
```

```plain title="output"
Hallo Sue!
```

## json

```
<object> | json[: <indent>]
```

Return the input object serialized to a JSON (JavaScript Object Notation) string.

```json title="data"
{
  "product": {
    "id": 1234,
    "name": "Football"
  }
}
```

```liquid2
{{ product | json }}
```

```plain title="output"
{ "id": 1234, "name": "Football" }
```

### Pretty JSON

If an argument is given, it should be an integer defining the amount of indentation that should be applied to a formatted JSON representation of the input object.

```liquid2
{{ product | json: indent=2 }}
```

```plain title="output"
{
  "id": 1234,
  "name": "Football"
}
```

## money

`money` is an alias for [`currency`](#currency).

## money_with_currency

`money_with_currency` is an alias for [`currency`](#currency) with the default format set to `"¤#,##0.00 ¤¤"`.

## money_without_currency

`money_without_currency` is an alias for [`currency`](#currency) with the default format set to `"#,##0.00¤"`.

## money_without_trailing_zeros

`money_without_trailing_zeros` is an alias for [`currency`](#currency) with the default format set to `"¤#,###"` and `currency_digits` set to `False`.

## ngettext

```
<string> | ngettext: <string>, <number> [, <identifier>: <object> ... ]
```

Return the localized translation of the input message with pluralization. The first positional argument is the plural form of the message. The second is a number used to determine if the singular or plural message should be used.

```liquid2
{% assign count = "Earth,Tatooine" | split: "," | size %}
{{ "Hello, World!" | ngetetxt: "Hello, Worlds!", count }}
```

```plain title="output"
Hallo Welten!
```

Any keyword arguments are used to populate message variables. If `user.name` is `"Sue"` and `count` is `1`:

```liquid2
{{ "Hello, %(you)s" | ngetetxt: "Hello, everyone!", count, you: user.name }}
```

```plain title="output"
Hallo Sue!
```

## npgettext

````
<string> | npgettext: <string>, <string>, <number> [, <identifier>: <object> ... ]
``

Return the localized translation of the input message with pluralization and a message context. The first positional argument is the message context string, the second is the plural form of the message, and the third is a number used to determine if the singular or plural message should be used.

```liquid2
{% assign count = "Earth,Tatooine" | split: "," | size %}
{{ "Hello, World!" | ngetetxt: "extra special greeting", "Hello, Worlds!", count }}
````

```plain title="output"
Hallo Welten!
```

Any keyword arguments are used to populate message variables. If `user.name` is `"Sue"` and `count` is `1`:

```liquid2
{{ "Hello, %(you)s" | ngetetxt: "extra special greeting", "Hello, everyone!", count, you: user.name }}
```

```plain title="output"
Hallo Sue!
```

## pgettext

```
<string> | pgettext: <string> [, <identifier>: <object> ... ]
```

Return the localized translation of the input message with additional message context. Message context is used to give translators extra information about where the messages is to be used.

```liquid2
{{ "Hello, World!" | pgettext: "extra special greeting" }}
```

```plain title="output"
Hallo Welt!
```

Any keyword arguments are used to populate message variables. If `user.name` is `"Sue"`:

```liquid2
{{ "Hello, %(you)s" | pgettext: "extra special greeting", you: user.name }}
```

```plain title="output"
Hallo Sue!
```

## sort_numeric

```
<sequence> | sort_numeric[: <string>]
```

Return a new array/list with items from the input sequence sorted by any integers and/or floats found in the string representation of each item. Note the difference between `sort_numeric` and `sort` in this example.

```liquid2
{% assign foo = '1.2.1, v1.10.0, v1.1.0, v1.2.2' | split: ', ' -%}
{{ foo | sort_numeric | join: ', ' }}
{{ foo | sort | join: ', ' }}

{% assign bar = '107, 12, 0001' | split: ', ' -%}
{{ bar | sort_numeric | join: ', ' }}
{{ bar | sort | join: ', ' }}
```

```plain title="output"
v1.1.0, 1.2.1, v1.2.2, v1.10.0
1.2.1, v1.1.0, v1.10.0, v1.2.2

0001, 12, 107
0001, 107, 12
```

The optional string argument is the name of a key/property to use as the sort key. In which case each item in the input sequence should be a dict/hash/mapping, each with said key/property.

`sort_numeric` will work as expected when given arrays/lists/tuples of integers, floats and/or Decimals, but will be slower than using standard `sort`.

If an input sequence contains strings (or arbitrary objects that get stringified) that do not have numeric characters, they will be pushed to the end of the resulting list, probably in the same order as in the input sequence.

## t

```
<string> | t[: <string>[, <identifier>: <object> ... ]] -> <string>
```

Return the localized translation of the input message. For example, if a German [Translations](babel.md#message-catalogs) object is found in the current render context:

```liquid2
{{ "Hello, World!" | t }}
```

```plain title="output"
Hallo Welt!
```

If given, the first and only positional argument is a message context string. It will be used to give translators extra information about where the message is to be used. With the default configuration, keyword arguments `plural` and `count` are reserved for specifying a pluralizable message.

```liquid2
{{ "Hello, World!" | t: plural: 'Hello, Worlds!', count: 2 }}
```

```plain title="output"
Hallo Welten!
```

The remaining keyword arguments are used to populate translatable message variables. If `user.name` is `"Sue"`:

```liquid2
{{ "Hello, %(you)s" | t: you: user.name }}
```

```plain title="output"
Hallo Sue!
```

## unit

```
<number> | unit: <string>
  [, denominator: <number>]
  [, denominator_unit: <string>]
  [, length: <string>]
  [, format: <string>]
```

Return the input number formatted with the given units according to the current locale. The first, required positional argument is a [CLDR](https://cldr.unicode.org/) measurement unit [code](https://github.com/unicode-org/cldr/blob/latest/common/validity/unit.xml).

```liquid2
{{ 12 | unit: 'length-meter' }}
```

```plain title="output"
12 meters
```

### length

`length` can be one of "short", "long" or "narrow", defaulting to "long".

```liquid
{{ 12 | unit: 'length-meter' }}
{{ 12 | unit: 'length-meter', length: 'short' }}
{{ 12 | unit: 'length-meter', length: 'long' }}
{{ 12 | unit: 'length-meter', length: 'narrow' }}
```

```plain title="output"
12 meters
12 m
12 meters
12m
```

Or, if the current locale is set to `fr`.

```liquid2
{% with locale:"fr" %}
  {{ 12 | unit: 'length-meter' }}
  {{ 12 | unit: 'length-meter', length: 'short' }}
  {{ 12 | unit: 'length-meter', length: 'long' }}
  {{ 12 | unit: 'length-meter', length: 'narrow' }}
{% endwith %}
```

```plain title="output"
12 mètres
12 m
12 mètres
12m
```

### format

`format` is an optional decimal format string, described in the [Locale Data Markup Language specification (LDML)](https://unicode.org/reports/tr35/).

```liquid2
{{ 12 | unit: 'length-meter', format: '#,##0.00' }}
```

```plain title="output"
12.00 meters
```

### Compound Units

If a `denominator` and/or `denominator_unit` is given, the value will be formatted as a compound unit.

```liquid2
{{ 150 | unit: 'kilowatt', denominator_unit: 'hour' }}
{{ 32.5 | unit: 'ton', denominator: 15, denominator_unit: 'hour' }}
```

```plain title="output"
150 kilowatts per hour
32.5 tons per 15 hours
```

Or, if the current locale is set to `fi`.

```liquid2
{% with locale:"fi" %}
  {{ 150 | unit: 'kilowatt', denominator_unit: 'hour' }}
  {{ 32.5 | unit: 'ton', denominator: 15, denominator_unit: 'hour' }}
{% endwith %}
```

```plain title="output"
150 kilowattia / tunti
32,5 am. tonnia/15 tuntia
```
