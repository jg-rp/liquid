# Contributing to Python Liquid

Hi. Your contributions and questions are always welcome. Feel free to ask questions, report bugs or request features on the [issue tracker](https://github.com/jg-rp/liquid/issues) or on [Github Discussions](https://github.com/jg-rp/liquid/discussions).

**Table of contents**

- [Development](#development)
- [Documentation](#documentation)
- [Style Guides](#style-guides)

## Development

Install development dependencies with [Pipenv](https://pipenv.pypa.io/en/latest/).

```shell
$ pipenv install --dev
$ pipenv shell
```

Run tests with Python's [unittest](https://docs.python.org/3/library/unittest.html#command-line-interface) module.

```shell
$ python -m unittest
```

Or [pytest](https://docs.pytest.org/en/7.1.x/).

```shell
$ pytest
```

Check formatting and style with [Pylint](https://github.com/PyCQA/pylint), [Flake8](https://flake8.pycqa.org/en/latest/) and [Black](https://github.com/psf/black).

```shell
$ tox -e lint
```

Typecheck with [Mypy](https://mypy.readthedocs.io/en/stable/).

```
$ tox -e typing
```

Always write tests using `unittest.TestCase`. We want our tests to be type-checked and linted too. Check test coverage with [Coverage.py](https://coverage.readthedocs.io/en/6.4.3/).

```
$ python -m coverage erase
$ python -m coverage run -p -m unittest
$ python -m coverage combine
$ python -m coverage report --fail-under=98
$ python -m coverage html
```

Then open `htmlcov/index.html` in your browser.

## Documentation

[Documentation](https://jg-rp.github.io/liquid/>) is built using [Docusaurus](https://docusaurus.io/). Find the source in the [docs branch](https://github.com/jg-rp/liquid/tree/docs) of this repository.

The `docs` folder in the root of this repository contains older, sphinx-based docs, still hosted on [Read the Docs](https://liquid.readthedocs.io/en/latest/). The plan is to generate API Documentation for Docusaurus from Python doc comments. The older docs will be kept until such time that better Docusaurus/sphinx integration is available or a workaround is found.

## Style Guides

### Git Commit Messages

There are no hard rules for git commit messages, although you might like to indicate the type of commit by starting the message with `docs:`, `feat:`, `fix:` or `refactor:`, for example.

### Python Style

All Python files are formatted using [Black](https://github.com/psf/black), with its default configuration.

Docstrings must use the [Sphinx docstring format](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html).
