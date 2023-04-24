# Python Liquid JSONPath

**_Requires Python Liquid version 1.9.2 or later._**

The [Liquid JSONPath](https://github.com/jg-rp/liquid-jsonpath) package brings JSONPath syntax to Liquid templates.

:::info
See the [Python JSONPath docs](https://jg-rp.github.io/python-jsonpath/syntax/) for JSONPath selector syntax.
:::

## Install

Install JSONPath for Liquid using [pip](https://pip.pypa.io/en/stable/getting-started/):

```shell
python -m pip install -U liquid-jsonpath
```

Or [pipenv](https://pipenv.pypa.io/en/latest/):

```shell
pipenv install liquid-jsonpath
```

## Configure

Filters and tags provided by Liquid JSONPath must be registered with an [`Environment`](../api/environment.md), just like you would with [custom tags or filters](../guides/custom-tags.md).

```python
from liquid import Environment
from liquid_jsonpath import Find
from liquid_jsonpath import JSONPathForTag

env = Environment()
env.add_filter("find", Find())
env.add_tag(JSONPathForTag)

# ...
```
