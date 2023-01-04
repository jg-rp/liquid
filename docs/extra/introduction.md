# Extra Tags and Filters

**_New in version 1.5.0_**

Extra tags and filters are those that are not "standard", require zero additional dependencies, and are commonly useful in scenarios that don't require strict compatibility with Ruby Liquid. Since Python Liquid version 1.5.0, extra tags and filters are importable from the `liquid.extra` package.

:::info
Prior to Python Liquid version 1.5.0, some extra tags and filters were maintained in the [Liquid Extra repository](https://github.com/jg-rp/liquid-extra). Wherever possible, you should use extra tags and filters included in Python Liquid over those found in Liquid Extra.

Python Liquid Extra will be maintained with bug fixes, but no new features, and is expected to work with Python Liquid up to, but not including, version 2.0.0 (unreleased).
:::

Unlike [standard tags and filters](../language/tags.md), which are registered for you automatically, non-standard tags and filters must be explicitly registered with an [`Environment`](../api/environment.md), just like you would with [custom tags or filters](../guides/custom-tags.md).

## Add All Extras

To add all extra tags and filters to a Liquid environment, with their default options, you can use the convenience function `liquid.extra.add_tags_and_filters()`.

```python
from liquid import Environment
from liquid.extra import add_tags_and_filters

env = Environment()
add_tags_and_filters(env)

template = env.from_string("""\
{% with greeting: "Hello" -%}
  {% for person in people -%}
    {% assign name = person.handle if person.has_handle else person.first_name | capitalize -%}
    {% if not person.leaving %}
      {{ greeting }}, {{ name }}
    {% else %}
      Goodbye, {{ name }}
    {% endif -%}
  {% endfor -%}
{% endwith -%}
""")

people = [
    {
        "handle": "",
        "has_handle": False,
        "first_name": "sue",
        "leaving": False,
    },
    {
        "handle": "MyNameIsJohn",
        "has_handle": True,
        "first_name": "John",
        "leaving": True,
    },
]

print(template.render(people=people))
```

```plain title="output"
Hello, Sue

Goodbye, MyNameIsJohn
```

## Adding Extra Filters

Filters can be implemented as simple functions, classes with a `__call__` method, or closures that returns a callable object. The latter two approaches are useful if a filter is configurable, in which case it will need to be instantiated or called before registering it with an [`Environment`](../api/environment.md).

For example, the `index` filter is a simple function, so we just pass the function object to [`Environment.add_filter()`](../api/environment.md#add_filter).

```python
from liquid import Environment
from liquid.extra import filters

env = Environment()
env.add_filter("index", filters.index)

template = env.from_string("""\
{{ shapes | index: 'square' }}
{% assign colors = "red, blue, green" | split: ", " -%}
{{ colors | index: 'blue' }}
""")

print(template.render(shapes=["square", "circle", "triangle"]))
```

```plain title="output"
0
1
```

Whereas the `json` filter is a class that can be configured with a `default` function, so it must be instantiated.

```python
from liquid import Environment
from liquid.extra.filters import JSON

env = Environment()
env.add_filter("json", JSON())

template = env.from_string("{{ data | json }}")

some_data = {
    "foo": [1,2,3],
    "bar": "Hello!"
}

print(template.render(data=some_data))
```

```plain title="output"
'{"foo": [1, 2, 3], "bar": "Hello!"}'
```

Refer to the [extra filter reference](./filters.md) for examples of registering each filter and their available options.

## Adding Extra Tags

All tags are implemented as a class inheriting from [`liquid.tag.Tag`](../api/tag.md). [`Environment.add_tag()`](../api/environment.md#add_tag) always takes a `Tag` object, not an instance of it.

For example, the [if (not)](./tags.md#if-not) tag - which adds a logical `not` operator and grouping with parentheses - would be registered as follows.

```python
from liquid import Environment
from liquid.extra.tags import IfNotTag

env = Environment()
env.add_tag(IfNotTag)

template = env.from_string("""\
{% if not product.available %}
   This product is not available.
{% endif %}
""")

print(template.render(product={"available": False}))
```

```plain title="output"
   This product is not available.
```

Some tags can be configured by subclassing them and setting class variables or overriding methods.