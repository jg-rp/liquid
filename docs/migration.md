This is the documentation for the latest version of Python Liquid ([GitHub](https://github.com/jg-rp/liquid)). Python Liquid strives for 100% compatibility with [Shopify/liquid](https://github.com/Shopify/liquid), the reference implementation.

[Python Liquid2](https://github.com/jg-rp/python-liquid2), a Python implementation of Liquid2, is an alternative Liquid template engine that deliberately deviates from [Shopify/liquid](https://github.com/Shopify/liquid) in its syntax and rendering behavior.

Here we cover migrating from Python Liquid version 1.x to the latest version. See the [Liquid2 migration guide](https://jg-rp.github.io/python-liquid2/migration/) if you're interested in switching to Liquid2.

## New features

Other than improved error messages and some new standard filters ([`has`](filter_reference.md#has), [`find`](filter_reference.md#find), [`find_index`](filter_reference.md#find_index) and [`reject`](filter_reference.md#reject)), there are no new features. Our goal with this release was to improve Python Liquid's API and improve compatibility with Shopify/liquid.

If you're interested in new features, take a look at [Liquid2](https://jg-rp.github.io/python-liquid2/migration/#new-features).

## Python version support and dependencies

Support for Python versions 3.7 and 3.8 has been dropped. Both are now [end of life](https://endoflife.date/python).

[MarkupSafe](https://github.com/pallets/markupsafe/) is now a required dependency. Previously it was an optional dependency.

[Babel](https://github.com/python-babel/babel) and [pytz](https://pypi.org/project/pytz/) are now dependencies as internationalization and localization tags and filters are included in Python Liquid. They used to be available from a separate package.

## API changes

### Package-level functions

[`parse`](api/convenience.md#liquid.parse), [`render`](api/convenience.md#liquid.render) and [`render_async`](api/convenience.md#liquid.render_async) are package-level functions that parse and render templates using the [default environment](environment.md). Where as before you might have done something like this:

```python
from liquid import Template
print(Template("Hello, {{ you }}!").render(you="World"))
```

You can now do:

```python
from liquid import render
print(render("Hello, {{ you }}!", you="World"))
```

### Environment.parse

[`Environment.from_string`](api/environment.md#liquid.Environment.from_string) is now aliased as [`Environment.parse`](api/environment.md#liquid.parse). The old `parse` method, which returned a list of nodes instead of a template, is now private.

```python
from liquid import Environment

env = Environment(extra=True)
template = env.parse("Hello, {{ you }}!")
```

### Environment.render

[`Environment.render`](api/environment.md#liquid.Environment.render) and [`Environment.render_async`](api/environment.md#liquid.Environment.render_async) parse and immediately render template source text without forcing you to explicitly create a new template.

```python
from liquid import Environment

env = Environment(extra=True)
print(env.render("Hello, {{ you }}!", you="World"))
```

### Template caching

The `cache_size` argument to `liquid.Environment` and `liquid.Template` has been removed. Template caching is now handled exclusively by template loaders. See [`CachingFileSystemLoader`](loading_templates.md/#caching-file-system-loader) and [`CachingLoaderMixin`](api/loaders.md#liquid.CachingLoaderMixin).

### Expression caching

The `expression_cache_size` argument to `liquid.Environment` and `liquid.Template` has been removed. Environment-level expression caching is no longer available as it does not play nicely with detailed error messages. If you need to cache parsing of Liquid expressions, it is now recommended to implement a cache per tag, where it makes sense to do so for your use case.

### Template loaders

[`BaseLoader.get_source`](api/loaders.md#liquid.loader.BaseLoader.get_source) and [`BaseLoader.get_source_async`](api/loaders.md#liquid.loader.BaseLoader.get_source_async) have been changed to accept an optional `context` argument and arbitrary keyword arguments as "load context". These new arguments replace methods `get_source_with_context` and `get_source_with_args`, which have been removed.

The value returned from `get_source`, [`TemplateSource`](api/loaders.md#liquid.loader.TemplateSource), has also changed to be a named tuple of the form `(text, name, uptodate, matter)`. It used to be `(source, filename, uptodate, matter)`.

### Template inheritance

We've added methods `variables()`, `variable_paths()`, `variable_segments()`, `global_variables()`, `global_variable_paths()`, `global_variable_segments()`, `filter_names()`, `tag_names()` and their async equivalents to [`liquid.BoundTemplate`](api/template.md). These are convenience methods for reporting variables, tags and filters using static analysis.

#### Custom tags

We've Changed [`Node.children()`](api/ast.md#liquid.Node.children) to return a sequence of [`Node`](api/ast.md) instance only, and added [`expressions()`](api/ast.md#liquid.Node.expressions), [`template_scope()`](api/ast.md#liquid.Node.template_scope), [`block_scope()`](api/ast.md#liquid.Node.block_scope) and [`partial_scope()`](api/ast.md#liquid.Node.partial_scope) methods.

See [liquid/builtin/tags](https://github.com/jg-rp/liquid/tree/main/liquid/builtin/tags) for examples.

### Render context

`liquid.Context` has been renamed to `liquid.RenderContext` and it's constructor arguments changed to require a instance of [`BoundTemplate`](api/template.md) as its only positional argument instead of an instance of `Environment`. All other arguments are now keyword only.

### Tokens, streams and expressions

All [tokens](api/tokens.md) are now named tuples of the form `(kind, value, start_index, source)`. They used to be `(linenum, type, value)`, and sometimes standard tuples instead of named tuples.

The `liquid.expressions` module has been removed in favour of a single [`TokenStream`](api/tokens.md#liquid.TokenStream) interface (there used to be two) and more sane expression parsing functions or static methods. Here's a summary mapping from old expression parsing functions to the recommended new parsing functions/methods.

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
