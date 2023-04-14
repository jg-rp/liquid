# Contributing to Python Liquid

Hi. Your contributions and questions are always welcome. Feel free to ask questions, report bugs or request features on the [issue tracker](https://github.com/jg-rp/liquid/issues) or on [Github Discussions](https://github.com/jg-rp/liquid/discussions).

**Table of contents**

- [Development](#development)
- [Documentation](#documentation)
- [Style Guides](#style-guides)

## Development

We use [hatch](https://hatch.pypa.io/latest/) to manage project dependencies and development environments.

Run tests with the _test_ script.

```shell
$ hatch run test
```

Or, to test against the full matrix of supported Python versions.

```shell
$ hatch run test:test
```

And to test without the _autoescape_ extra.

```shell
$ hatch run noescape:test
```

Lint with [ruff](https://beta.ruff.rs/docs/).

```shell
$ hatch run lint
```

Typecheck with [Mypy](https://mypy.readthedocs.io/en/stable/).

```shell
$ hatch run typing
```

Check coverage with pytest-cov.

```shell
$ hatch run cov
```

Or generate an HTML coverage report.

```shell
$ hatch run cov-html
```

Then open `htmlcov/index.html` in your browser.

## Documentation

[Documentation](https://jg-rp.github.io/liquid/>) is built using [Docusaurus](https://docusaurus.io/). Find the source in the [docs branch](https://github.com/jg-rp/liquid/tree/docs) of this repository.

The `docs` folder in the root of this repository contains older, sphinx-based docs, still hosted on [Read the Docs](https://liquid.readthedocs.io/en/latest/). The plan is to generate API Documentation for Docusaurus from Python doc comments. The older docs will be kept until such time that better Docusaurus/sphinx integration is available or a workaround is found.

## Style Guides

### Git Commit Messages

There are no hard rules for git commit messages, although you might like to indicate the type of commit by starting the message with `docs:`, `chore:`, `feat:`, `fix:` or `refactor:`, for example.

### Python Style

All Python files are formatted using [Black](https://github.com/psf/black), with its default configuration.

Docstrings must use the [Sphinx docstring format](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html).
