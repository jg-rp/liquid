[Filters](tag_reference.md#filters) are usually implemented as simple Python functions. When rendered, Liquid will find the function in [`Environment.filters`](api/environment.md#liquid.Environment.filters), then call it, passing the input value as the first argument, followed by positional and keyword arguments given by the template author. The function's return value then becomes the result of the _filtered expression_.

Filters can actually be any Python [callable](https://docs.python.org/3/glossary.html#term-callable). Implementing a filter as a class with a `__call__` method or as a closure can be useful if you want to configure the filter before registering it with an [`Environment`](environment.md).

Also see the [filter helpers](api/filter.md) API documentation.

!!! tip

    See [liquid/builtin/filters](https://github.com/jg-rp/liquid/tree/main/liquid/builtin/filters) for lots of examples.

## Add a filter

To add a filter, add an item to [`Environment.filters`](api/environment.md#liquid.Environment.filters). It's a regular dictionary mapping filter names to callables.

In this example we add `ends_with`, a filter that delegates to Python's `str.endswith`. The `@string_filter` decorator coerces the input value to a string, if it is not one already.

```python
from liquid import Environment
from liquid.filter import string_filter


@string_filter
def ends_with(left: str, val: str) -> bool:
    return left.endswith(val)


env = Environment()
env.filters["ends_with"] = ends_with

source = """\
{% assign foo = "foobar" | ends_with: "bar" %}
{% if foo %}
    do something
{% endif %}"""

template = env.from_string(source)
print(template.render())
```

### With context

Sometimes a filter will need access to the current [render context](render_context.md). Use the `@with_context` decorator to have an instance of [`RenderContext`](api/render_context.md) passed to your filter callable as a keyword argument named `context`.

Here we use the render context to resolve a variable called "handle".

```python
from liquid import Environment
from liquid.filter import string_filter
from liquid.filter import with_context


@string_filter
@with_context
def link_to_tag(label, tag, *, context):
    handle = context.resolve("handle", default="")
    return (
        f'<a title="Show tag {tag}" href="/collections/{handle}/{tag}">{label}</a>'
    )

class MyEnvironment(Environment):
    def register_tags_and_filters(self):
        super().register_tags_and_filters()
        self.filters["link_to_tag"] = link_to_tag

env = MyEnvironment()
# ...
```

### With environment

Use the `@with_environment` decorator to have the current [`Environment`](api/environment.md) passed to your filter callable as a keyword argument named `environment`.

```python
import re

from markupsafe import Markup
from markupsafe import escape as markupsafe_escape

from liquid import Environment
from liquid.filter import string_filter
from liquid.filter import with_environment

RE_LINETERM = re.compile(r"\r?\n")


@with_environment
@string_filter
def strip_newlines(val: str, *, environment: Environment) -> str:
    if environment.autoescape:
        val = markupsafe_escape(val)
        return Markup(RE_LINETERM.sub("", val))
    return RE_LINETERM.sub("", val)

# ...
```

## Replace a filter

To replace a default filter implementation with your own, simply update the [`filters`](api/environment.md#liquid.Environment.filters) dictionary on your Liquid [Environment](environment.md).

Here we replace the default `slice` filter with one which uses start and stop values instead of start and length, and is a bit more forgiving in terms of allowed inputs.

```python
from liquid import Environment
from liquid.filter import int_arg
from liquid.filter import sequence_filter

@sequence_filter
def myslice(val, start, stop=None):
    start = int_arg(start)

    if stop is None:
        return val[start]

    stop = int_arg(stop)
    return val[start:stop]


env = Environment()
env.filters["slice"] = myslice
# ...
```

## Remove a filter

Remove a built-in filter by deleting it from your [environment's](environment.md) [`filters`](api/environment.md#liquid.Environment.filters) dictionary.

```python
from liquid import Environment

env = Environment()
del env.filters["safe"]

# ...
```

!!! tip

    You can add, remove and replace filters on `liquid.DEFAULT_ENVIRONMENT` too. Convenience functions [`parse()`](api/convenience.md#liquid.parse) and [`render()`](api/convenience.md#liquid.render) use `DEFAULT_ENVIRONMENT`
