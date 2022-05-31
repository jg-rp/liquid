# Objects and Drops

Python Liquid uses [`__getitem__`](https://docs.python.org/3/reference/datamodel.html#object.__getitem__) internally for resolving property names and accessing items in a sequence. So, if your [data](./render-context.md#render-arguments) is some combination of dictionaries and lists, for example, templates can reference objects as follows.

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

This is by design, and is one of the reasons Liquid is considered "safe" and "suitable for end users". To expose an object's properties we can implement Python's [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence) or [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping) interface.

:::info
Python Liquid's equivalent of a "drop", as found in Ruby Liquid, is a Python object that implements the [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence) or [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping) interface.
:::

```python
from collections import abc
from liquid import Template, StrictUndefined

class User(abc.Mapping):
    def __init__(
        self,
        first_name,
        last_name,
        perms,
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

print(Template("{{ user.first_name }}").render(user=user))  # John
print(Template("{{ user.name }}").render(user=user))  # John Smith
print(Template("{{ user.is_admin }}").render(user=user))  # true

print(Template("{{ user.perms[0] }}", undefined=StrictUndefined).render(user=user))
# UndefinedError: key error: 'perms', user[perms][0], on line 1
```

## Drop Wrapper

One could implement a simple "Drop" wrapper for data access objects like this, while still being explicit about which properties are exposed to templates.

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

## `__liquid__`

By implementing a `__liquid__` method, Python objects can behave like primitive Liquid data types. This is useful for situations where you need your Python object to act as an array index, or to be compared to a primitive data type, for example.

```python
from liquid import Template

class IntDrop:
    def __init__(self, val: int):
        self.val = val

    def __int__(self) -> int:
        return self.val

    def __str__(self) -> str:
        return "one"

    def __liquid__(self) -> int:
        return self.val


template = Template(
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

## `__html__`

When [HTML auto-escaping](./auto-escape.md) is enabled, an object can be output as an HTML-safe string by implementing an `__html__()` method.

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

env = Environment(autoescape=True)
template = env.from_string(r"{{ products }}")
print(template.render(products=ListDrop(["Shoe", "Hat", "Ball"])))
```

```html title="output"
<ul>
  <li>Shoe</li>
  <li>Hat</li>
  <li>Ball</li>
</ul>
```

If auto-escaping is not enabled, `__html__` is ignored and the return value of `__str__` is used instead. Explicitly escaping an object using the [escape](../language/filters#escape) filter will always yield an escaped version of `__str__`.
