---
title: Compatibility
description: Known incompatibilities between Python Liquid and Ruby Liquid
hide_table_of_contents: false
---

# Known Issues

This page documents known compatibility issues between Python Liquid and the [reference implementation](https://shopify.github.io/liquid/) of Liquid, written in Ruby. We strive to be 100% compatible with the reference implementation. That is, given an equivalent render context, a template rendered with Python Liquid should produce the same output as when rendered with Ruby Liquid.

Issues described here are considered "won't fix" or are an unacceptable breaking change for those who already rely on past Python Liquid behavior. You are encouraged to see the [issue tracker](https://github.com/jg-rp/liquid/issues) for features and bugs that can or will be addressed.

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

## Comment Parsing

Python Liquid will raise a `LiquidSyntaxError` if it finds the string `{% endcomment %}` inside a comment block. Ruby Liquid, on the other hand, will successfully parse fully-formed nested comment blocks, but will fail to parse a comment block containing either a `{% comment %}` or `{% endcomment %}` on its own.

## Counters

In Ruby Liquid, the built-in [`increment`](/language/tags#increment) and [`decrement`](/language/tags#decrement) tags can, in some cases, mutate "global" context and keep named counters alive between renders. Although not difficult to implement, I can't quite bring myself to do it.

## Cycle Arguments

Python Liquid will accept [`cycle`](/language/tags#cycle) arguments of any type, including identifiers to be resolved, this behavior is considered "unintended" or "undefined" in Ruby Liquid (see [issue #1519](https://github.com/Shopify/liquid/issues/1519)). If you need interoperability between Python Liquid and Ruby Liquid, only use strings or numbers as arguments to `cycle`.

## Cycle Groups

**_See issue [#43](https://github.com/jg-rp/liquid/issues/43)_**

When the [`cycle`](/language/tags#cycle) tag is given a name, Python Liquid will use that name and all other arguments to distinguish one cycle from another. Ruby Liquid will disregard all other arguments when given a name. For example.

```liquid
{% cycle a: 1, 2, 3 %}
{% cycle a: "x", "y", "z" %}
{% cycle a: 1, 2, 3 %}
```

**Ruby Liquid Output:**

```plain
1
y
3
```

**Python Liquid Output:**

```plain
1
x
2
```

## The Date Filter

The built-in [`date`](/language/filters#date) filter uses [dateutil](https://dateutil.readthedocs.io/en/stable/) for parsing strings to `datetime`s, and `strftime` for formatting. There are likely to be some inconsistencies between this and the reference implementation's equivalent parsing and formatting of dates and times.

## Error Handling

Python Liquid might not handle syntax or type errors in the same way as the reference implementation. We might fail earlier or later, and will almost certainly produce a different error message.

Python Liquid does not have a "lax" parser, like Ruby Liquid. Upon finding an error, Python Liquid's [lax mode](/introduction/strictness) simply discards the current block and continues to parse/render the next block, if one is available. Also, Python Liquid will never inject error messages into an output document. Although this can be achieved by extending [`BoundTemplate`](/api/BoundTemplate) and overriding [`render_with_context()`](/api/BoundTemplate#render_with_context).

## Floats in Ranges

If a range literal uses a float literal as its start or stop value, the float literal must have something after the decimal point. This is OK `(1.0..3)`. This is not `(1...3)`. Ruby Liquid will accept either, resulting in a sequence of `[1,2,3]`.