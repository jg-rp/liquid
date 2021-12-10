---
slug: /
---

# Getting Started

Python Liquid is a [Python](https://www.python.org/) engine for [Liquid](https://shopify.github.io/liquid/),
the safe, customer-facing template language for flexible web apps.

This page gets you started using Liquid with Python. See [Introduction to Liquid](/language/introduction),
the [filter reference](/language/filters) and the [tag reference](/language/tags) to learn about
writing Liquid templates.

## Install

Install Python Liquid using [Pipenv](https://pipenv.pypa.io/en/latest/):

```shell
$ pipenv install python-liquid
```

Or [pip](https://pip.pypa.io/en/stable/getting-started/):

```shell
$ python -m pip install -U python-liquid
```

## Render

Render a template string by creating a [Template](/api/Template) and calling its [render()](/api/BoundTemplate#render) method.

```python
from liquid import Template

template = Template("Hello, {{ you }}!")
print(template.render(you="World"))  # Hello, World!
print(template.render(you="Liquid"))  # Hello, Liquid!
```

Keyword arguments passed to [render()](/api/BoundTemplate#render) are available as variables for
templates to use in Liquid expressions.

```python
from liquid import Template

template = Template(
    "{% for person in people %}"
    "Hello, {{ person.name }}!\n"
    "{% endfor %}"
)

context_data = {"people": [
    {"name": "John"},
    {"name": "Sally"},
]}
print(template.render(**context_data))
# Hello, John!
# Hello, Sally!
```

## Configure

Configure template parsing and rendering behavior with extra arguments to [Template](/api/Template).
The following example renders a template in [strict mode](introduction/strictness) and will raise an
exception whenever an undefined variable is used. See [liquid.Template](api/Template) for all
available options.

```python
from liquid import Template
from liquid import Mode
from liquid import StrictUndefined

template = Template(
    "Hello, {{ you }}!",
    tolerance=Mode.STRICT,
    undefined=StrictUndefined,
)

result = template.render(you="World")
```

:::tip
Keep reading to see how to configure an environment once, then load and render templates from it.
:::

## Environment

While [Template](/api/Template) can be convenient, more often than not an application will want
to configure a single [Environment](/api/Environment), then load and render templates from it.
This is usually more efficient than using [Template](/api/Template) directly.

All templates rendered from an [Environment](/api/Environment) will share the environment's
configuration. See [liquid.Environment](api/Environment) for all available options.

```python
from liquid import Template
from liquid import Mode
from liquid import StrictUndefined
from liquid import FileSystemLoader

env = Environment(
    tolerance=Mode.STRICT,
    undefined=StrictUndefined,
    loader=FileSystemLoader("./templates/"),
)

template = env.from_string("Hello, {{ you }}!")
result = template.render(you="World")
```

:::note
Notice that [Environment](/api/Environment) accepts a `loader` argument, whereas
[Template](/api/Template) does not.
:::
