# Python Liquid

A Python implementation of [Liquid](https://shopify.github.io/liquid/), the safe customer-facing template language for flexible web apps.

!!! info
    Python Liquid documentation has moved to [https://jg-rp.github.io/liquid/](https://jg-rp.github.io/liquid/).

## Install

Install Python Liquid using [Pipenv](https://pipenv.pypa.io/en/latest/):

```shell
$ pipenv install -u python-liquid
```

Or [pip](https://pip.pypa.io/en/stable/getting-started/):

```shell
$ pip install python-liquid
```

Or from [conda-forge](https://anaconda.org/conda-forge/python-liquid):

```shell
$ conda install -c conda-forge python-liquid
```

## Quick Start

Render a template string by creating a `Template` and calling its `render()` method.

```python
from liquid import Template

template = Template("Hello, {{ you }}!")
print(template.render(you="World"))  # Hello, World!
print(template.render(you="Liquid"))  # Hello, Liquid!
```

Keyword arguments passed to render() are available as variables for templates to use in Liquid expressions.

```python
from liquid import Template

template = Template(
    "{% for person in people %}"
    "Hello, {{ person.name }}!\n"
    "{% endfor %}"
)

data = {
    "people": [
        {"name": "John"},
        {"name": "Sally"},
    ]
}

print(template.render(**data))
# Hello, John!
# Hello, Sally!
```

## What's next?

Learn how to [configure a Liquid environment](https://jg-rp.github.io/liquid/introduction/getting-started#configure) and [load templates](https://jg-rp.github.io/liquid/introduction/loading-templates) from a file system or database.
