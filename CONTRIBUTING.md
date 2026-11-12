# Contributing to Python Liquid

Your contributions and questions are always welcome. Feel free to ask questions, report bugs or request features on the [issue tracker](https://github.com/jg-rp/liquid/issues) or on [Github Discussions](https://github.com/jg-rp/liquid/discussions).

**Table of contents**

- [Development](#development)
- [Documentation](#documentation)
- [Style Guides](#style-guides)
- [Branches](#branches)

## Development

The [Golden Liquid Test Suite](https://github.com/jg-rp/golden-liquid) is included as a Git [submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules). Clone the Python Liquid Git repository and initialize the Golden Liquid submodule like this.

```shell
$ git clone git@github.com:jg-rp/liquid.git
$ cd liquid
$ git submodule update --init
```

We use [hatch](https://hatch.pypa.io/latest/) to manage project dependencies and development environments.

Run tests with the _test_ script.

```shell
$ hatch run test
```

Or, to test against the full matrix of supported Python versions.

```shell
$ hatch run test:test
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

[Documentation](https://jg-rp.github.io/liquid/) is built using Sphinx. Find the source in the `docs` folder of this repository.

Build HTML docs to the `site` directory.

```shell
$ hatch run docs-build
```

## Style Guides

### Git Commit Messages

There are no hard rules for git commit messages, although you might like to indicate the type of commit by starting the message with `docs:`, `chore:`, `feat:`, `fix:` or `refactor:`, for example.

### Python Style

All Python files are formatted using [Ruff](https://github.com/astral-sh/ruff), configured in `pyproject.toml`

### Branches

The `main` branch is for the latest version of Python Liquid.

Python Liquid version 2.x lives on the `v2` branch.
