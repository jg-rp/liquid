<h1 align="center">Python Liquid</h1>

<p align="center">
Python Liquid is a Python engine for <a href="https://shopify.github.io/liquid/">Liquid</a>, the safe, customer-facing template language.
<br>
We follow <a href="https://github.com/Shopify/liquid">Shopify/Liquid</a> closely and test against the <a href="https://github.com/jg-rp/golden-liquid">Golden Liquid</a> test suite.
</p>
<p align="center">
  <a href="https://pypi.org/project/python-liquid/">
    <img src="https://img.shields.io/pypi/v/python-liquid.svg?style=flat-square" alt="PyPi - Version">
  </a>
  <a href="https://anaconda.org/conda-forge/python-liquid">
    <img src="https://img.shields.io/conda/vn/conda-forge/python-liquid?style=flat-square" alt="conda-forge">
  </a>
  <a href="https://pypi.org/project/python-liquid/">
    <img src="https://img.shields.io/pypi/pyversions/python-liquid.svg?style=flat-square" alt="Python versions">
  </a>
  <br>
  <a href="https://github.com/jg-rp/liquid/actions/workflows/tests.yaml">
    <img src="https://img.shields.io/github/actions/workflow/status/jg-rp/liquid/tests.yaml?branch=main&label=tests&style=flat-square" alt="Tests">
  </a>
  <a href="https://github.com/jg-rp/liquid/actions/workflows/coverage.yaml">
    <img src="https://img.shields.io/github/actions/workflow/status/jg-rp/liquid/coverage.yaml?branch=main&label=coverage&style=flat-square" alt="Coverage">
  </a>
  <br>
  <a href="https://pypi.org/project/python-liquid/">
    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/python-liquid?style=flat-square">
  </a>
  <br>
  <a href="https://github.com/jg-rp/liquid/blob/main/LICENSE">
    <img src="https://img.shields.io/pypi/l/python-liquid.svg?style=flat-square" alt="License">
  </a>
</p>

---

**Table of Contents**

- [Install](#install)
- [Links](#links)
- [Related Projects](#related-projects)
- [Quick Start](#example)
- [Contributing](#contributing)

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

## Links

- Documentation: https://jg-rp.github.io/liquid/
- Documentation for Python Liquid version 1.x: https://jg-rp.github.io/python-liquid-docs-archive/
- Change Log: https://github.com/jg-rp/liquid/blob/main/CHANGES.md
- PyPi: https://pypi.org/project/python-liquid/
- Source Code: https://github.com/jg-rp/liquid
- Issue Tracker: https://github.com/jg-rp/liquid/issues

## Related Projects

- [Python Liquid2](https://github.com/jg-rp/python-liquid2): A new Python engine for Liquid with [extra features](https://jg-rp.github.io/python-liquid2/migration/#new-features).
- [LiquidScript](https://github.com/jg-rp/liquidscript): A JavaScript engine for Liquid with a similar high-level API to Python Liquid.

## Quick Start

### `render()`

This example renders a template from a string of text with the package-level `render()` function. The template has just one placeholder variable `you`, which we've given the value `"World"`.

```python
from liquid import render

print(render("Hello, {{ you }}!", you="World"))
# Hello, World!
```

### `parse()`

Often you'll want to render the same template several times with different variables. We can parse source text without immediately rendering it using the `parse()` function. `parse()` returns a `BoundTemplate` instance with a `render()` method.

```python
from liquid import parse

template = parse("Hello, {{ you }}!")
print(template.render(you="World"))  # Hello, World!
print(template.render(you="Liquid"))  # Hello, Liquid!
```

### Configure

Both `parse()` and `render()` are convenience functions that use the default Liquid environment. For all but the simplest cases, you'll want to configure an instance of `Environment`, then load and render templates from that.

```python
from liquid import CachingFileSystemLoader
from liquid import Environment

env = Environment(
    autoescape=True,
    loader=CachingFileSystemLoader("./templates"),
)
```

Then, using `env.parse()` or `env.get_template()`, we can create a `BoundTemplate` from a string or read from the file system, respectively.

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

## Contributing

Please see [Contributing to Python Liquid](https://github.com/jg-rp/liquid/blob/main/contributing.md).
