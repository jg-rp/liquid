# Python Liquid

Liquid is a template language, where source text (the template) contains placeholders for variables, conditional expressions for including or excluding blocks of text, and loops for repeating blocks of text. Plus other syntax for manipulating variables and combining multiple templates into a single output.

Python Liquid is a Python engine for te Liquid template language. We follow [Shopify/Liquid](https://github.com/Shopify/liquid) closely and test against the [Golden Liquid test suite](https://github.com/jg-rp/golden-liquid).

## Install

Install Python Liquid from [PyPi](https://pypi.org/project/python-liquid/) using [pip](https://pip.pypa.io/en/stable/getting-started/):

```console
python -m pip install python-liquid
```

Or [Pipenv](https://pipenv.pypa.io/en/latest/):

```console
pipenv install -u python-liquid
```

Or [poetry](https://python-poetry.org/docs/)

```console
poetry add python-liquid
```

Or from [conda-forge](https://anaconda.org/conda-forge/python-liquid):

```console
conda install -c conda-forge python-liquid
```

## Quick Start

## `render()`

Here's a very simple example that renders a template from a string of text with the package-level [`render()`](api/convenience.md#liquid.render) function. The template has just one placeholder variable `you`, which we've given the value `"World"`.

```python
from liquid import render

print(render("Hello, {{ you }}!", you="World"))
# Hello, World!
```

## `parse()`

Often you'll want to render the same template several times with different variables. We can parse source text without immediately rendering it using the [`parse()`](api/convenience.md#liquid.parse) function. `parse()` returns a [`Template`](api/template.md) instance with a `render()` method.

```python
from liquid import parse

template = parse("Hello, {{ you }}!")
print(template.render(you="World"))  # Hello, World!
print(template.render(you="Liquid"))  # Hello, Liquid!
```

## Configure

Both [`parse()`](api/convenience.md#liquid.parse) and [`render()`](api/convenience.md#liquid.render) are convenience functions that use the [default Liquid environment](environment.md). For all but the simplest cases you'll want to configure an instance of [`Environment`](api/environment.md), then load and render templates from that.

```python
from liquid import CachingFileSystemLoader
from liquid import Environment

env = Environment(
    autoescape=True,
    loader=CachingFileSystemLoader("./templates"),
)
```

Then, using `env.parse()` or `env.get_template()`, we can create a [`Template`](api/template.md) from a string or read from the file system, respectively.

```python
# ... continued from above
template = env.parse("Hello, {{ you }}!")
print(template.render(you="World"))  # Hello, World!

# Try to load "./templates/index.html"
another_template = env.get_template("index.html")
data = {"some": {"thing": [1, 2, 3]}}
result = another_template.render(**data)
```

Unless you happen to have a relative folder called `templates` with a file called `index.html` within it, we would expect a `TemplateNotFoundError` to be raised when running the example above.

## What's next?

Read more about [configuring Liquid environments](environment.md), [template loaders](loading_templates.md) and [managing render context data](render_context.md).
