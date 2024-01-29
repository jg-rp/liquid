<h1 align="center">Python Liquid</h1>

<p align="center">
A Python engine for <a href="https://shopify.github.io/liquid/">Liquid</a>, the safe customer-facing template language for flexible web apps.
<br>We follow <a href="https://github.com/Shopify/liquid">Shopify/Liquid</a> closely and test against the <a href="https://github.com/jg-rp/golden-liquid">Golden Liquid</a> test suite.
</p>
<p align="center">
  <a href="https://github.com/jg-rp/liquid/blob/main/LICENSE">
    <img src="https://img.shields.io/pypi/l/python-liquid.svg?style=flat-square" alt="License">
  </a>
  <br>
  <a href="https://pypi.org/project/python-liquid/">
    <img src="https://img.shields.io/pypi/v/python-liquid.svg?style=flat-square" alt="PyPi - Version">
  </a>
  <a href="https://anaconda.org/conda-forge/python-liquid">
    <img src="https://img.shields.io/conda/vn/conda-forge/python-liquid?style=flat-square" alt="conda-forge">
  </a>
  <br>
  <a href="https://pypi.org/project/python-liquid/">
    <img src="https://img.shields.io/pypi/pyversions/python-liquid.svg?style=flat-square" alt="Python versions">
  </a>
  <a href="https://github.com/jg-rp/liquid/actions/workflows/coverage.yaml">
    <img src="https://img.shields.io/badge/pypy-3.7%20%7C%203.8%20%7C%203.9-blue?style=flat-square" alt="PyPy versions">
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
</p>

---

**Table of Contents**

- [Install](#install)
- [Links](#links)
- [Example](#example)
- [Related Projects](#related-projects)
- [Compatibility](#compatibility)
- [Benchmark](#benchmark)
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
- Change Log: https://github.com/jg-rp/liquid/blob/main/CHANGES.md
- PyPi: https://pypi.org/project/python-liquid/
- Source Code: https://github.com/jg-rp/liquid
- Issue Tracker: https://github.com/jg-rp/liquid/issues

## Example

```python
from liquid import Template

template = Template("Hello, {{ you }}!")
print(template.render(you="World"))  # "Hello, World!"
print(template.render(you="Liquid"))  # "Hello, Liquid!"
```

## Related Projects

- [liquid-babel](https://github.com/jg-rp/liquid-babel) Internationalization and localization for Liquid templates.
- [LiquidScript](https://github.com/jg-rp/liquidscript): A JavaScript and TypeScript engine for Liquid with a similar high-level API to Python Liquid.
- [django-liquid](https://github.com/jg-rp/django-liquid): A Django template backend for Liquid. Render Liquid templates in your Django apps.
- [Flask-Liquid](https://github.com/jg-rp/Flask-Liquid): A Flask extension for Liquid. Render Liquid templates in your Flask applications.
- [golden-liquid](https://github.com/jg-rp/golden-liquid): A test suite for Liquid. See how various Liquid template engines compare to the reference implementation.

## Compatibility

We strive to be 100% compatible with the [reference implementation](https://shopify.github.io/liquid/) of Liquid, written in Ruby. That is, given an equivalent render context, a template rendered with Python Liquid should produce the same output as when rendered with Ruby Liquid.

See the [known issues page](https://jg-rp.github.io/liquid/known_issues) for details of known incompatibilities between Python Liquid and Ruby Liquid, and please help by raising an issue if you notice an incompatibility.

## Benchmark

You can run the benchmark using `hatch run benchmark` (or `python -O scripts/performance.py` if you don't have `make`) from the root of the source tree. On my ropey desktop computer with a Ryzen 5 1500X and Python 3.11.0, we get the following results.

```text
Best of 5 rounds with 100 iterations per round and 60 ops per iteration (6000 ops per round).

lex template (not expressions): 1.2s (5020.85 ops/s, 83.68 i/s)
                    lex and parse: 5.0s (1197.32 ops/s, 19.96 i/s)
                        render: 1.4s (4152.92 ops/s, 69.22 i/s)
            lex, parse and render: 6.5s (922.08 ops/s, 15.37 i/s)
```

And PyPy3.7 gives us a decent increase in performance.

```text
Best of 5 rounds with 100 iterations per round and 60 ops per iteration (6000 ops per round).

lex template (not expressions): 0.58s (10308.67 ops/s, 171.81 i/s)
                    lex and parse: 3.6s (1661.20 ops/s, 27.69 i/s)
                        render: 0.95s (6341.14 ops/s, 105.69 i/s)
            lex, parse and render: 4.6s (1298.18 ops/s, 21.64 i/s)
```

On the same machine, running `rake benchmark:run` from the root of the reference implementation source tree gives us these results.

```text
/usr/bin/ruby ./performance/benchmark.rb lax

Running benchmark for 10 seconds (with 5 seconds warmup).

Warming up --------------------------------------
                parse:     3.000  i/100ms
            render:     8.000  i/100ms
    parse & render:     2.000  i/100ms
Calculating -------------------------------------
                parse:     39.072  (± 0.0%) i/s -    393.000  in  10.058789s
            render:     86.995  (± 1.1%) i/s -    872.000  in  10.024951s
    parse & render:     26.139  (± 0.0%) i/s -    262.000  in  10.023365s
```

I've tried to match the benchmark workload to that of the reference implementation, so that we might compare results directly. The workload is meant to be representative of Shopify's use case, although I wouldn't be surprised if their usage has changed subtly since the benchmark fixture was designed.

## Contributing

Please see [Contributing to Python Liquid](https://github.com/jg-rp/liquid/blob/main/contributing.md).
