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

Install `python-liquid` from [PyPi](https://pypi.org/project/python-liquid) using your favorite package manager.

**pip**

```shell
pip install python-liquid
```

**uv**

```shell
uv add python-liquid
```

**pipenv**

```shell
pipenv install -u python-liquid
```

**conda**

```shell
conda install -c conda-forge python-liquid
```

## Links

- Documentation: https://jg-rp.github.io/liquid/
- Documentation for Python Liquid version 1.x: https://jg-rp.github.io/python-liquid-docs-archive/
- Documentation for Python Liquid version 2.x: https://github.com/jg-rp/liquid/blob/v2.3.6/docs/index.md
- Change Log: https://github.com/jg-rp/liquid/blob/main/CHANGES.md
- PyPi: https://pypi.org/project/python-liquid/
- Source Code: https://github.com/jg-rp/liquid
- Issue Tracker: https://github.com/jg-rp/liquid/issues

## Related Projects

- [Python Liquid2](https://github.com/jg-rp/python-liquid2): A new Python engine for Liquid with [extra features](https://jg-rp.github.io/python-liquid2/migration/#new-features).
- [Ruby Liquid2](https://github.com/jg-rp/ruby-liquid2): Liquid2 templates for Ruby.
- [Micro Liquid](https://github.com/jg-rp/micro-liquid): A stripped-down Liquid-like template engine for Python. You can think of it as a non-evaluating alternative to Python's [f-strings](https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals) or [t-strings](https://docs.python.org/3.14/whatsnew/3.14.html#whatsnew314-pep750).
- [LiquidScript](https://github.com/jg-rp/liquidscript): A JavaScript engine for Liquid with a similar high-level API to Python Liquid.

## Quick Start

### `render()`

Use the package-level `liquid.render()` function to render a template with Liquid's default configuration. The first argument is template source code and the second is a dictionary of template variables.

```python
import liquid

print(liquid.render("Hello, {{ you }}!", {"you": "World"}))  # Hello, World!
```

### `parse()`

Use `liquid.parse()` to get an instance of `liquid.Template`, which can be rendered multiple times with different data.

```python
from liquid import parse

template = parse("Hello, {{ you }}!")
print(template.render(you="World"))  # Hello, World!
print(template.render(you="Liquid"))  # Hello, Liquid!
```

### Configure

You'll need to create an instance of `liquid.Environment` to configure Liquid, then load and render templates from that.

```python
from liquid import Environment, CachingFileSystemLoader

env = Environment(
  autoescape=True,
  loader=CachingFileSystemLoader("./templates")
)

template = env.get_template("index.liquid")
another_template = env.parse("{% render 'greeting' %}, World!")
```

See [docs](https://jg-rp.github.io/liquid/).

## Contributing

Please see [Contributing to Python Liquid](https://github.com/jg-rp/liquid/blob/main/contributing.md).
