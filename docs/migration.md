This is the documentation for the latest version of Python Liquid. Python Liquid strives for 100% compatibility with [Shopify/liquid](https://github.com/Shopify/liquid), the reference implementation.

[Python Liquid2](https://github.com/jg-rp/python-liquid2), a Python implementation of Liquid2, is an alternative Liquid template engine that deliberately deviates from [Shopify/liquid](https://github.com/Shopify/liquid) in its syntax and rendering behavior.

Here we cover migrating from Python Liquid version 1.x to the latest version. See the [Liquid2 migration guide](https://jg-rp.github.io/python-liquid2/migration/) if you're interested in switching to Liquid2.

## New features

Other than improved error messages and some new standard filters, there are no new features. Our goal with this release was to improve Python Liquid's API, without changing template rendering behavior.

If you're interested in new features, take a look at [Liquid2](https://jg-rp.github.io/python-liquid2/migration/#new-features).

## Python version support and dependencies

Support for Python versions 3.7 and 3.8 has been dropped. Both are now [end of life](https://endoflife.date/python).

[MarkupSafe](https://github.com/pallets/markupsafe/) is now a required dependency. Previously it was an optional dependency.

[Babel](https://github.com/python-babel/babel) and [pytz](https://pypi.org/project/pytz/) are now dependencies as internationalization and localization tags and filters are included in Python Liquid. They used to be available from a separate package.

## API changes

### Name changes

TODO:

### New convenience functions

TODO:

### Caching

TODO:

### Template loaders

TODO:

### Tokens and expressions

TODO:

Here's a summary mapping from old expression parsing functions to the recommended new parsing functions/methods.

| Old                                        | New                                                                |
| ------------------------------------------ | ------------------------------------------------------------------ |
| `tokenize_common_expression(str, linenum)` | `liquid.builtin.expressions.tokenize(source, parent_token)`        |
| `*.tokenize(source, linenum)`              | `liquid.builtin.expressions.tokenize(source, parent_token)`        |
| `parse_common_expression(stream)`          | `liquid.builtin.expressions.parse_primitive(env, stream)`          |
| `parse_keyword_arguments(expr, linenum)`   | `liquid.builtin.expressions.KeywordArgument.parse(env, stream)`    |
| `parse_identifier(stream)`                 | `liquid.builtin.expressions.Path.parse(env, stream)`               |
| `parse_unchained_identifier(stream)`       | `liquid.builtin.expressions.parse_identifier(env, stream)`         |
| `parse_string_or_identifier`               | `liquid.builtin.expressions.parse_string_or_path(env, stream)`     |
| `parse_unchained_identifier`               | `liquid.builtin.expressions.parse_name(env, stream)`               |
| `parse_boolean`                            | `liquid.builtin.expressions.parse_primitive(env, stream)`          |
| `parse_nil`                                | `liquid.builtin.expressions.parse_primitive(env, stream)`          |
| `parse_empty`                              | `liquid.builtin.expressions.parse_primitive(env, stream)`          |
| `parse_blank`                              | `liquid.builtin.expressions.parse_primitive(env, stream)`          |
| `parse_string_literal`                     | `liquid.builtin.expressions.parse_primitive(env, stream)`          |
| `parse_integer_literal`                    | `liquid.builtin.expressions.parse_primitive(env, stream)`          |
| `parse_float_literal`                      | `liquid.builtin.expressions.parse_primitive(env, stream)`          |
| `Environment.parse_boolean_expression`     | `liquid.builtin.expressions.BooleanExpression.parse(env, stream)`  |
| `Environment.parse_filtered_expression`    | `liquid.builtin.expressions.FilteredExpression.parse(env, stream)` |
| `Environment.parse_loop_expression`        | `liquid.builtin.expressions.LoopExpression.parse(env, stream)`     |

### Template inheritance

TODO:
