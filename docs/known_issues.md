This page documents known compatibility issues between Python Liquid's default [`Environment`](api/environment.md) and [Shopify/liquid](https://shopify.github.io/liquid/), the reference implementation written in Ruby. We strive to be 100% compatible with Shopify/liquid. That is, given an equivalent render context, a template rendered with Python Liquid should produce the same output as when rendered with Ruby Liquid.

## Coercing Strings to Integers Inside Filters

**_See issue [#49](https://github.com/jg-rp/liquid/issues/49)_**

Many filters built in to Liquid will automatically convert a string representation of a number to an integer or float as needed. When converting integers, Ruby Liquid uses [Ruby's String.to_i method](https://ruby-doc.org/core-3.1.1/String.html#method-i-to_i), which will disregard trailing non-digit characters. In the following example, `'7,42'` is converted to `7`

**template:**

```liquid
{{ 3.14 | plus: '7,42' }}
{{ '123abcdef45' | plus: '1,,,,..!@qwerty' }}
```

**output**

```plain
10.14
124
```

Python Liquid currently falls back to `0` for any string that can't be converted to an integer in its entirety. As is the case in Ruby Liquid for strings without leading digits.

This does not apply to parsing of integer literals, only converting strings to integers (not floats) inside filters.

## The Date Filter

The built-in [`date`](filter_reference.md#date) filter uses [dateutil](https://dateutil.readthedocs.io/en/stable/) for parsing strings to `datetime`s, and `strftime` for formatting. There are likely to be some inconsistencies between this and the reference implementation's equivalent parsing and formatting of dates and times.

## Orphaned `{% break %}` and `{% continue %}`

**_See issue [#76](https://github.com/jg-rp/liquid/issues/76)_**

Shopify/liquid shows some unintuitive behavior when `{% break %}` or `{% continue %}` are found outside a `{% for %}` tag block.

```liquid
{%- if true -%}
before
{%- if true %}
hello{% break %}goodbye
{% endif -%}
after
{%- endif -%}
{% for x in (1..3) %}
{{ x }}
{% endfor %}
{% for x in (1..3) %}
{{ x }}
{% endfor %}
```

Shopify/iquid output in both strict and lax modes:

```plain
before
hello
```

Python Liquid raises a `LiquidSyntaxError` in strict mode and jumps over the entire outer `{% if %}` block in lax mode.

```plain
1

2

3


1

2

3

```
