# Python Liquid Babel

Internationalization and localization for Liquid templates.

[Python Liquid Babel](https://github.com/jg-rp/liquid-babel) is a collection of optional [filters](../language/filters.md) and [tags](../language/tags.md) that facilitate the internationalization (i18n) and localization (i10n) of Liquid templates.

:::info
At this time, only `currency`/`money`, `number`/`decimal` and `datetime` filters are implemented. More filters, translation tags and a translation extractor are planned for the future.
:::

## Install

Install Python Liquid Babel using [pipenv](https://pipenv.pypa.io/en/latest/):

```shell
$ pipenv install liquid-babel
```

Or [pip](https://pip.pypa.io/en/stable/getting-started/):

```shell
$ python -m pip install -U liquid-babel
```

## Usage

Babel filters are implemented as Python classes. Pass options to a babel filter constructor, and register the resulting instance with a Liquid [`Environment`](../api/environment.md) by calling its [`add_filter()`](../api/environment.md#add_filter) method.

```python
from liquid import Environment
from liquid_babel.filters import Currency

env = Environment()
env.add_filter("currency", Currency(
    default_locale="en_CA",
    default_format="#,##0.00",
))

template = env.from_string("{{ 100457.99 | currency }}")
print(template.render())
```

:::info
Liquid Babel uses [Python Babel](https://github.com/python-babel/babel). Please refer to the [Babel docs](https://babel.pocoo.org/en/latest/index.html) for more information about locales, currency codes and format strings.
:::
