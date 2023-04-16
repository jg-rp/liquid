# Custom Filters

In Python Liquid, a [filters](../language/introduction.md#filters) are implemented as a Python functions or callable classes that accept at least one argument, the left hand side of a filtered expression. The callable's return value will be output, assigned or piped to more filters.

:::info
All built-in filters are implemented in this way, so have a look in [liquid/builtin/filters/](https://github.com/jg-rp/liquid/tree/main/liquid/builtin/filters) for examples.
:::

## Add a Filter

Add a custom template filter to an [`Environment`](../api/environment.md) by calling its [`add_filter()`](../api/environment.md#add_filter) method. Here's a simple example of adding Python's `str.endswith` as a filter function.

```python
from liquid import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates/"))
env.add_filter("endswith", str.endswith)
```

In a template, you'd use it like this.

```liquid
{% assign foo = "foobar" | endswith: "bar" %}
{% if foo %}
    <!-- do something -->
{% endif %}
```

### With Context

Decorate filter functions with `with_context` to have the active render context passed as a keyword argument. Notice that we can use the [`context`](../api/context.md) object to resolve variables that have not been passed as filter arguments.

```python title="myfilters.py"
from liquid.filter import with_context
from liquid.filter import string_filter

@string_filter
@with_context
def link_to_tag(label, tag, *, context):
    handle = context.resolve("handle", default="")
    return (
        f'<a title="Show tag {tag}" href="/collections/{handle}/{tag}">{label}</a>'
    )
```

And register it wherever you create your environment.

```python
from liquid import Environment, FileSystemLoader
from myfilters import link_to_tag

env = Environment(loader=FileSystemLoader("templates/"))
env.add_filter("link_to_tag", link_to_tag)
```

In a template, you could then use the link_to_tag filter like this.

```liquid
{% if tags %}
    <dl class="navbar">
    <dt>Tags</dt>
        {% for tag in collection.tags %}
        <dd>{{ tag | link_to_tag: tag }}</dd>
        {% endfor %}
    </dl>
{% endif %}
```

### With Environment

Decorate filter functions with `with_environment` to have the active [`Environment`](../api/environment.md) passed as a keyword argument. For example, the built-in [`strip_newlines`](../language/filters#strip_newlines) filter changes its return value depending on parameters set on the environment.

```python
@with_environment
@string_filter
def strip_newlines(val: str, *, environment: Environment) -> str:
    """Return the given string with all newline characters removed."""
    if environment.autoescape:
        val = markupsafe_escape(val)
        return Markup(RE_LINETERM.sub("", val))
    return RE_LINETERM.sub("", val)
```

## Replace a Filter

If given the name of an existing filter function, [`Environment.add_filter()`](../api/environment.md#add_filter) will replace it without warning. For example, suppose you wish to replace the [`slice`](../language/filters.md#slice) filter for one which uses start and stop values instead of start and length, and is a bit more forgiving in terms of allowed inputs.

```python title="myfilters.py"
@liquid_filter
def myslice(val, start, stop = None):
    try:
        start = int(start)
    except (ValueError, TypeError) as err:
        raise FilterArgumentError(
            f"slice expected an integer start, found {type(start).__name__}"
        ) from err

    if stop is None:
        return val[start]

    try:
        stop = int(stop)
    except (ValueError, TypeError) as err:
        raise FilterArgumentError(
            f"slice expected an integer stop, found {type(stop).__name__}"
        ) from err

    if isinstance(val, str):
        return val[start:stop]

    # `val` could be any sequence.
    return list(val[start:stop])
```

```python
from liquid import Environment, FileSystemLoader
from myfilters import myslice

env = Environment(loader=FileSystemLoader("templates/"))
env.add_filter("slice", myslice)
```

## Remove a Filter

Remove a built-in filter by deleting it from [`Environment.filters`](../api/environment.md). It's a regular dictionary mapping filter names to filter functions.

```python
from liquid import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates/"))
del env.filters["base64_decode"]
```

## Class-Based Filters

If your custom filter takes initialization arguments or needs to retain state between calls (probably not a good idea), a class-based implementation might be appropriate. Simply implement a [`__call__`](https://docs.python.org/3/reference/datamodel.html#object.__call__) method, and Python Liquid will use it when applying the filter.

For example, here's the implementation of a `json` filter, that dumps the input object to a JSON formatted string.

```python
import json
from typing import Any
from typing import Callable
from typing import Optional

from liquid.filter import int_arg
from liquid.filter import liquid_filter

class JSON:
    def __init__(self, default: Optional[Callable[[Any], Any]] = None):
        self.default = default

    @liquid_filter
    def __call__(
        self,
        obj: object,
        indent: Optional[object] = None,
    ) -> str:
        indent = int_arg(indent) if indent else None
        return json.dumps(obj, default=self.default, indent=indent)
```

### Async Filters

Class-based filters can also implement a `filter_async` method, which should be a coroutine. When applied in an async context, if a filter implements `filter_async`, it will be awaited instead of calling `__call__`.

## Filter Function Decorators

Although not required, built-in filter functions tend to use decorators for performing common argument manipulation and error handling. None of these decorators take any arguments, and they can all be found in `liquid.filters`.

### `@liquid_filter`

A filter function decorator that catches any `TypeError`s raised from the wrapped function. If a `TypeError` is raised, it is re-raised as a `liquid.exceptions.FilterArgumentError`.

### `@sequence_filter`

A filter function decorator that raises a `liquid.exceptions.FilterValueError` if the filter value
can not be coerced into an array-like object. Also catches any `TypeError`s raised from the wrapped function. If a `TypeError` is raised, it is re-raised as a `liquid.exceptions.FilterArgumentError`.

This is intended to mimic the semantics of the reference implementation's `InputIterator` class.

### `@array_filter`

A filter function decorator that raises a `liquid.exceptions.FilterValueError` if the filter value
is not array-like. Also catches any `TypeError`s raised from the wrapped function. If a `TypeError`
is raised, it is re-raised as a `liquid.exceptions.FilterArgumentError`.

### `@string_filter`

A filter function decorator that converts the first positional argument to a string and catches any
`TypeError`s raised from the wrapped function. If a `TypeError` is raised, it is re-raised as a
`liquid.exceptions.FilterArgumentError`.

### `@math_filter`

A filter function decorator that raises a `liquid.excpetions.FilterArgumentError` if the filter
value is not, or can not be converted to, a number. Also catches any `TypeError`s raised from the
wrapped function. If a `TypeError` is raised, it is re-raised as a `liquid.exceptions.FilterArgumentError`.

## Raising Exceptions From Filter Functions

In general, when raising exceptions from filter functions, those exceptions should be a subclass of
[`liquid.exceptions.FilterError`](../api/exceptions.md#liquidexceptionsfiltererror).
