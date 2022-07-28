# Undefined Variables

When rendering a Liquid template, if a variable name can not be resolved, an instance of `liquid.Undefined` is used instead. We can customize template rendering behavior by implementing some of [Python's "magic" methods](https://docs.python.org/3/reference/datamodel.html#basic-customization) on a subclass of `liquid.Undefined`.

## Default Undefined

All operations on the default `Undefined` type are silently ignored and, when rendered, it produces an empty string. For example, you can access properties and iterate an undefined variable without error.

```liquid title="template"
Hello {{ nosuchthing }}
{% for thing in nosuchthing %}
    {{ thing }}
{% endfor %}
```

```plain title="output"
Hello



```

## Strict Undefined

When `liquid.StrictUndefined` is passed as the `undefined` argument to [`Environment`](../api/environment.md) or [`Template`](../api/template.md), any operation on an undefined variable will raise an `UndefinedError`.

```python
from liquid import Environment, StrictUndefined

env = Environment(undefined=StrictUndefined)
template = env.from_string("Hello {{ nosuchthing }}")
template.render()
# UndefinedError: 'nosuchthing' is undefined, on line 1
```

## The default filter

With `StrictUndefined`, the built-in [`default`](../language/filters.md#default) filter does not handle undefined variables the [way you might expect](https://github.com/Shopify/liquid/issues/1404). The following example will raise an `UndefinedError` if `username` is undefined.

```liquid
Hello {{ username | default: "user" }}
```

We can fix this by implementing our own `Undefined` type and registering an updated version of the `default` filter.

```python title="strict_default_undefined.py"
from liquid import StrictUndefined
from liquid.exceptions import UndefinedError

class StrictDefaultUndefined(StrictUndefined):
    def __getattribute__(self, name: str) -> object:
        if name in (
            "__repr__",
            "__liquid__",
            "__class__",
            "name",
            "hint",
            "obj",
            "msg",
        ):
            return object.__getattribute__(self, name)
        raise UndefinedError(object.__getattribute__(self, "msg"))
```

```python title="my_default_filter.py"
from liquid.filter import liquid_filter
from liquid import is_undefined
from liquid.expression import EMPTY

@liquid_filter
def default_undefined(
    obj: object,
    default_: object = "",
    *,
    allow_false: bool = False
) -> object:
    """Return a default value if the input is undefined, nil, false, or empty."""
    _obj = obj
    if hasattr(obj, "__liquid__"):
        _obj = obj.__liquid__()

    if allow_false is True and _obj is False:
        return obj

    if is_undefined(_obj) or _obj in (None, False, EMPTY):
        return default_

    return obj
```

Use `StrictDefaultUndefined` and `default_undefined` by registering them with an [`Environment`](../api/environment.md), then loading and rendering templates from that environment.

```python
from liquid import Environment
from strict_default_undefined import StrictDefaultUndefined
from my_default_filter import default_undefined

env = Environment(undefined=StrictDefaultUndefined)
env.add_filter("default", default_undefined)
```

## Falsy StrictUndefined

It's usually [not possible](https://github.com/Shopify/liquid/issues/1034) to detect undefined variables in a template using an [`if`](../language/tags#if) tag. In Python Liquid we can implement an `Undefined` type that allows us to write `{% if nosuchthing %}`, but still get some strictness when undefined variables are used elsewhere.

```python
from liquid import Environment
from liquid import StrictUndefined

class FalsyStrictUndefined(StrictUndefined):
    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        if other is False:
            return True
        raise UndefinedError(self.msg)

env = Environment(undefined=FalsyStrictUndefined)

template = env.from_string("{% if nosuchthing %}foo{% else %}bar{% endif %}")
template.render() # "bar"

template = env.from_string("{{ nosuchthing }}")
template.render()
# UndefinedError: 'nosuchthing' is undefined, on line 1
```
