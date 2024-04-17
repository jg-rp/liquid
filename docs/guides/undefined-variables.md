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

**_New in version 1.4.0_**

We can use the built-in `StrictDefaultUndefined` type, which plays nicely with the `default` filter, while still providing strictness elsewhere.

```python
from liquid import Environment
from liquid import StrictDefaultUndefined

env = Environment(undefined=StrictDefaultUndefined)
template = env.from_string('Hello {{ username | default: "user" }}')
print(template.render())
```

```plain title="output"
Hello user
```

## Falsy StrictUndefined

It's [usually not possible](https://github.com/Shopify/liquid/issues/1034) to detect undefined variables in a template using an [`if`](../language/tags#if) tag. In Python Liquid we can implement an `Undefined` type that allows us to write `{% if nosuchthing %}` or `{% if nosuchthing == 'foo' %}`, but still get some strictness when undefined variables are used elsewhere.

```python
from liquid import Environment
from liquid import StrictUndefined


class FalsyStrictUndefined(StrictUndefined):
    # Properties that don't raise an UndefinedError.
    allowed_properties = frozenset(
        [
            "__repr__",
            "__bool__",
            "__eq__",
            "__liquid__",
            "__class__",
            "name",
            "hint",
            "obj",
            "msg",
        ]
    )

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return other is False


env = Environment(undefined=FalsyStrictUndefined)

template = env.from_string("{% if nosuchthing %}foo{% else %}bar{% endif %}")
print(template.render())  # "bar"

template = env.from_string("{% if nosuchthing == 'hi' %}foo{% else %}bar{% endif %}")
print(template.render())  # "bar"

template = env.from_string("{{ nosuchthing | upcase }}")
template.render()
# UndefinedError: 'nosuchthing' is undefined, on line 1
```
