# JSONPath Tags

This page documents tags included with the [Liquid JSONPath](https://github.com/jg-rp/liquid-jsonpath) package. See the [tag reference](../language/tags.md) for details of all standard tags. Also see the [Python JSONPath docs](https://jg-rp.github.io/python-jsonpath/syntax/) for JSONPath selector syntax.

## for

A drop-in replacement for the [standard `for` tag](../language/tags.md#for) with support for piping an iterable through a JSONPath expression.

```liquid
{% for name in site | '$.users[?@.score > 60].name' %}
  {{- name }},
{%- endfor %}
```

If the following data was assigned to a variable called `site`:

```json title="data"
{
  "users": [
    {
      "name": "Sue",
      "score": 100
    },
    {
      "name": "John",
      "score": 86
    },
    {
      "name": "Sally",
      "score": 84
    },
    {
      "name": "Jane",
      "score": 55
    }
  ]
}
```

We'd get an output like this:

```plain title="output"
Sue,John,Sally,
```

### Options

This `for` tag defaults to an [undefined](../guides/undefined-variables.md) instance when given a JSONPath and an unacceptable iterable. You can change this behavior by subclassing `liquid_jsonpath.JSONPathForTag` and setting the `default` class attribute to one of `Default.EMPTY`, `Default.RAISE` or `Default.UNDEFINED`.

```python
from liquid import Environment
from liquid_jsonpath import Default
from liquid_jsonpath import JSONPathForTag

class MyJSONPathForTag(JSONPathForTag):
    default = Default.EMPTY

env = Environment()
env.add_tag(MyJSONPathForTag)
# ...
```

`Default.RAISE` will raise a `LiquidTypeError` when given an unacceptable iterable, and `Default.EMPTY` will simply use an empty list instead.

### Customizing JSONPath

This `for` tag uses a [`JSONPathEnvironment`](https://jg-rp.github.io/python-jsonpath/api/#jsonpath.JSONPathEnvironment) with its default configuration. You can use a custom `JSONPathEnvironment` by subclassing `liquid_jsonpath.JSONPathForTag` and setting the `jsonpath_class` class attribute.

```python
from jsonpath import JSONPathEnvironment
from liquid_jsonpath import JSONPathForTag

class MyJSONPathEnv(JSONPathEnvironment):
    root_token = "^"  # silly example

class MyJSONPathForTag(JSONPathForTag):
    jsonpath_class = MyJSONPathEnv

env = Environment()
env.add_tag(MyJSONPathForTag)
# ...
```
