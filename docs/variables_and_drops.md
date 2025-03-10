Liquid _primitive types_ map to Python types according to the following table. You can, for example, compare a Liquid string to a Python string directly with `{% if var == "thing" %}`, where `var` is a [global](render_context.md) variable containing a Python string.

Note that Liquid has _weak typing_. Anywhere a particular type is expected, Liquid will implicitly try to convert a value to that type if needed.

| Primitive type | Python type | Example Liquid literal |
| -------------- | ----------- | ---------------------- |
| BooleanLiteral | bool        | `true` or `false`      |
| NullLiteral    | None        | `null` or `nil`        |
| IntegerLiteral | int         | `123`                  |
| FloatLiteral   | float       | `1.23`                 |
| StringLiteral  | str         | `"Hello"` or `'Hello'` |
| RangeLiteral   |             | `(1..5)` or `(x..y)`   |

## Sequences and mappings

Anywhere an array-like value is expected, like the left-hand side of the [`join` filter](filter_reference.md#join), Liquid will accept any Python [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence), not just a list.

In the case of a [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping), like a dict, a `{% for %}` loop will iterator over mapping items, whereas a sequence filter will add the mapping to a single element sequence and iterate over that.

```python
from collections.abc import Sequence
from liquid import render


class MySequence(Sequence[int]):
    def __init__(self, items: list[int]):
        self.items = items

    def __getitem__(self, key: int) -> int:
        return self.items[key] * 2

    def __len__(self) -> int:
        return len(self.items)


data = {
    "sequences": [
        MySequence([1, 2, 3]),
        ["a", "b", "c"],
        (True, False),
        {"x": 4, "y": 5, "z": 6},
    ]
}

source = """\
{% for sequence in sequences -%}
    {% for item in sequence %}
        - {{ item -}}
    {% endfor %}
{% endfor %}
"""

print(render(source, **data))

```

```plain title="output"
        - 2
        - 4
        - 6

        - a
        - b
        - c

        - true
        - false

        - ('x', 4)
        - ('y', 5)
        - ('z', 6)
```

## Paths to variables

When referenced in a template, a variable is best viewed as a _path_ to a value, where each path has one or more _segments_. Segments can be property names separated by dots (`foo.bar`), array indexes using bracket notation (`store.products[1]`) or bracketed property names for situations where the property name is held in a variable or contains reserved characters (`product.variant[var]` or `products["something with spaces"]`)

Python Liquid uses [`__getitem__`](https://docs.python.org/3/reference/datamodel.html#object.__getitem__) internally for resolving property names and accessing items in a sequence. So, if your data is some combination of dictionaries and lists, for example, templates can reference objects as follows.

```json title="data"
{
  "products": [
    {
      "title": "Some Shoes",
      "available": 5,
      "colors": ["blue", "red"]
    },
    {
      "title": "A Hat",
      "available": 2,
      "colors": ["grey", "brown"]
    }
  ]
}
```

```liquid title="template"
{{ products[0].title }}
{{ products[-2]['available'] }}
{{ products.last.title }}
{{ products.first.colors | join: ', ' }}
```

```plain title="output"
Some Shoes
5
A Hat
blue, red
```

Attempting to access properties from a Python class or class instance **will not work**.

```python
from liquid import Template

class Product:
    def __init__(self, title, colors):
        self.title = title
        self.colors = colors

products = [
    Product(title="Some Shoes", colors=["blue", "red"]),
    Product(title="A Hat", colors=["grey", "brown"]),
]

Template("{{ products.first.title }}!").render(products=products)
```

```plain title="output"
!
```

## Drops

A _drop_ (as in "drop of liquid") is an instance of a Python class that implements the [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence) or [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping) interface, or other [magic methods](#other-magic-methods).

We use the Mapping interface to force ourselves to be explicit about which properties are exposed to template authors.

```python
from collections import abc
from typing import Any

from liquid import Environment
from liquid import StrictUndefined
from liquid import render


class User(abc.Mapping[str, Any]):
    def __init__(
        self,
        first_name: str,
        last_name: str,
        perms: list[str],
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.perms = perms or []

        self._keys = [
            "first_name",
            "last_name",
            "is_admin",
            "name",
        ]

    def __getitem__(self, k):
        if k in self._keys:
            return getattr(self, k)
        raise KeyError(k)

    def __iter__(self):
        return iter(self._keys)

    def __len__(self):
        return len(self._keys)

    def __str__(self):
        return f"User(first_name='{self.first_name}', last_name='{self.last_name}')"

    @property
    def is_admin(self):
        return "admin" in self.perms

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"


user = User("John", "Smith", ["admin"])

print(render("{{ user.first_name }}", user=user))  # John
print(render("{{ user.name }}", user=user))  # John Smith
print(render("{{ user.is_admin }}", user=user))  # true


strict_env = Environment(undefined=StrictUndefined)
print(strict_env.from_string("{{ user.perms[0] }}").render(user=user))
# liquid.exceptions.UndefinedError: user.perms is undefined
#   -> '{{ user.perms[0] }}' 1:3
#   |
# 1 | {{ user.perms[0] }}
#   |    ^^^^ user.perms is undefined

```

### Drop wrapper

For convenience, you could implement a drop wrapper for data access objects, while still being explicit about which properties to expose.

```python
class Drop(abc.Mapping):
    def __init__(obj, keys):
        self.obj = obj
        self.keys = keys

    def __getitem__(self, k):
        # Delegate attribute access to self.obj only if `k` is in `self.keys`.
        if k in self.keys:
            return getattr(obj, k)
        raise KeyError(k)

    def __iter__(self):
        return iter(self.keys)

    def __len__(self):
        return len(self.keys)
```

### `__liquid__`

If a drop implements the special `__liquid__()` method, Liquid will use the result of calling `__liquid__()` when resolving a [variable path or segment](#paths-to-variables). This is useful for situations where you need your Python object to act as an array index, or to be compared to a primitive data type, for example.

```python
from liquid import parse

class IntDrop:
    def __init__(self, val: int):
        self.val = val

    def __int__(self) -> int:
        return self.val

    def __str__(self) -> str:
        return "one"

    def __liquid__(self) -> int:
        return self.val


template = parse(
    "{% if my_drop < 10 %}"
    "{{ my_drop }} "
    "{% endif %}"
    "{{ some_array[my_drop] }}"
)

context_data = {
    "my_drop": IntDrop(1),
    "some_array": ["a", "b", "c"],
}

print(template.render(**context_data))  # one b
```

### `__html__`

When [HTML auto-escaping](environment.md#html-auto-escape) is enabled, an object can be output as an HTML-safe string by implementing the special `__html__()` method.

```python
from liquid import Environment


class ListDrop:
    def __init__(self, somelist):
        self.items = somelist

    def __str__(self):
        return f"ListDrop({self.items})"

    def __html__(self):
        lis = "\n".join(f"  <li>{item}</li>" for item in self.items)
        return f"<ul>\n{lis}\n</ul>"


env = Environment(auto_escape=True)
template = env.from_string(r"{{ products }}")
print(template.render(products=ListDrop(["Shoe", "Hat", "Ball"])))
```

```plain title="output"
<ul>
  <li>Shoe</li>
  <li>Hat</li>
  <li>Ball</li>
</ul>
```

### `__getitem_async__`

If an instance of a drop that implements `__getitem_async__()` appears in a [`render_async()`](api/template.md#liquid.BoundTemplate.render_async) context, `__getitem_async__()` will be awaited instead of calling `__getitem__()`.

```python
class AsyncCollection(abc.Mapping):
    def __init__(self, val):
        self.keys = ["products"]
        self.cached_products = []

    def __len__(self):
        return 1

    def __iter__(self):
        return iter(self["products"])

    async def __aiter__(self):
        # Note that Liquid's built-in `for` loop does not yet support async iteration.
        return iter(self.__getitem_async__("products"))

    def __getitem__(self, k):
        if not self.cached_products:
            # Blocking IO here
            self.cached_products = get_stuff_from_database()
        return self.cache_products

    async def __getitem_async__(self, k):
        if not self.cached_products:
            # Do async IO here.
            self.cached_products = await get_stuff_from_database_async()
        return self.cache_products
```

### Other magic methods

Other Python [magic methods](https://docs.python.org/3/reference/datamodel.html) will work with Liquid filters and special properties too.

```python
from liquid import Environment

env = Environment()

class Foo:
    def __int__(self):
        return 7

    def __str__(self):
        return "Bar"

    def __len__(self):
        return 5


template = env.from_string(
    """\
{{ foo }}
{{ foo | plus: 2 }}
{{ foo.size }}
"""
)

print(template.render(foo=Foo()))
```

```plain title="output"
Bar
9
5
```

## Undefined variables

At render time, if a variable can not be resolved, and instance of [`Undefined`](api/undefined.md) is used instead. We can customize template rendering behavior by implementing some of [Python's "magic" methods](https://docs.python.org/3/reference/datamodel.html#basic-customization) on a subclass of `Undefined`.

### Default undefined

All operations on the default `Undefined` type are silently ignored and, when rendered, it produces an empty string. For example, you can access properties and iterate an undefined variable without error.

```liquid
Hello {{ nosuchthing }}
{% for thing in nosuchthing %}
    {{ thing }}
{% endfor %}
```

```plain title="output"
Hello



```

### Strict undefined

When [`StrictUndefined`](api/undefined.md#liquid.undefined.StrictUndefined) is passed as the `undefined` argument to an [`Environment`](api/environment.md), any operation on an undefined variable will raise an `UndefinedError`.

```python
from liquid import Environment, StrictUndefined

env = Environment(undefined=StrictUndefined)
template = env.from_string("Hello {{ nosuchthing }}")
template.render()
# liquid.exceptions.UndefinedError: 'nosuchthing' is undefined
#   -> 'Hello {{ nosuchthing }}' 1:9
#   |
# 1 | Hello {{ nosuchthing }}
#   |          ^^^^^^^^^^^ 'nosuchthing' is undefined
```

### Falsy strict undefined

[`FalsyStrictUndefined`](api/undefined.md#liquid.undefined.FalsyStrictUndefined) is the same as [`StrictUndefined`](#strict-undefined), but can be tested for truthiness and equality without raising an exception.

```python
from liquid import Environment
from liquid import FalsyStrictUndefined

env = Environment(undefined=FalsyStrictUndefined)
template = env.from_string("{% if nosuchthing %}foo{% else %}bar{% endif %}")
print(template.render())  # bar
```
