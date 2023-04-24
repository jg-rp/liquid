# JSONPath Filters

This page documents filters included with the [Liquid JSONPath](https://github.com/jg-rp/liquid-jsonpath) package. See the [filter reference](../language/filters.md) for details of all standard filters. Also see the [Python JSONPath docs](https://jg-rp.github.io/python-jsonpath/syntax/) for JSONPath selector syntax.

## find

`<object> | find: <string> -> <list>`

Return the result of applying a _jsonpath string_ to the input value. The input value should be a list (or any sequence) or a dict (or any mapping).

```liquid
{{ site | find: '$.users.*.name' | join: ' ' }}
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
Sue John Sally Jane
```

### Options

The `find` filter defaults to returning an [undefined](../guides/undefined-variables.md) instance when given anything other than a mapping or sequence as its input value. You can change this behavior by setting the `default` argument to one of `Default.EMPTY`, `Default.RAISE` or `Default.UNDEFINED` when registering `find` with an environment.

```python
from liquid import Environment
from liquid_jsonpath import Default
from liquid_jsonpath import Find

env = Environment()
env.add_filter("find", Find(default=Default.RAISE))
# ...
```

`Default.RAISE` will raise a `FilterArgumentError` when given an unacceptable input value or JSONPath string, and `Default.EMPTY` will simply return an empty list instead.

### Customizing JSONPath

The `find` filter uses a [`JSONPathEnvironment`](https://jg-rp.github.io/python-jsonpath/api/#jsonpath.JSONPathEnvironment) with its default configuration. You can replace the `JSONPathEnvironment` used by `find` by subclassing `liquid_jsonpath.Find` and setting the `jsonpath_class` class attribute.

```python
from jsonpath import JSONPathEnvironment
from liquid_jsonpath import Find

class MyJSONPathEnv(JSONPathEnvironment):
    root_token = "^"  # silly example

class MyFindFilter(Find):
    jsonpath_class = MyJSONPathEnv

env = Environment()
env.add_filter("find", MyFindFilter())
```
