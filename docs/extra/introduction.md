# Python Liquid Extra

Python Liquid Extra is a repository of extra tags and filters for Python Liquid.

:::caution
These tags and filters are not part of "standard" Liquid. If you choose to use them in your
templates, those templates are unlikely to render correctly with other implementations of Liquid.
:::

## Install

Install Python Liquid Extra using [Pipenv](https://pipenv.pypa.io/en/latest/):

```shell
$ pipenv install python-liquid-extra
```

Or [pip](https://pip.pypa.io/en/stable/getting-started/):

```shell
$ python -m pip install -U python-liquid-extra
```

## Usage

Unlike [standard tags and filters](/language/tags), which are registered for you automatically,
you must register any extra tags and/or filters with an [Environment](/#environment)
explicitly. Just like you would with [custom tags or filters](/guides/custom-tags).

### Filters

A filter function is any callable that accepts at least one argument, the result of the left hand
side of a filtered expression. They can be implemented as simple functions, classes with a
`__call__` method or closures that return a function or callable object. The latter two could take
additional arguments. Refer to the [extra filter reference](filters) to see what, if any, additional
arguments they support.

Add a template filter to an [Environment](../api/Environment) by calling its [add_filter()](../api/Environment#add_filter) method. For example:

```python
from liquid import Environment
from liquid_extra import filters

env = Environment()
env.add_filter("json", filters.JSON())
```

### Tags

Some tags, like [if (not)](tags#if-not), will replace standard, built-in tags. Others will introduce
new tags. Refer to the [extra tag reference](tags) to see what features each tags adds and/or
removes.

Register a tag with an [Environment](../api/Environment) by calling its [add_tag](../api/Environment#add_tag)
method. Then render templates from that environment. Notice that `add_tag` expects the tag class,
not an instance of it.

```python
from liquid import Environment
from liquid_extra.tags import IfNotTag

env = Environment()
env.add_tag(IfNotTag)
```

### Flask-Liquid

If you're using [Flask-Liquid](https://github.com/jg-rp/Flask-Liquid), you can get hold of the
active [liquid.Environment](../api/Environment) from an instance of the `Liquid` extension.

```python title="app.py"
from flask import Flask

from flask_liquid import Liquid
from flask_liquid import render_template

from liquid_extra import filters
from liquid_extra import tags

app = Flask(__name__)

liquid = Liquid(app)
liquid.env.add_filter("json", filters.JSON())
liquid.env.add_tag(tags.IfNotTag)

@app.route("/hello/")
@app.route("/hello/<name>")
def index(name=None):
    return render_template("index.html", name=name)
```

### django-liquid

Using [django-liquid](https://github.com/jg-rp/django-liquid), the [liquid.Environment](../api/Environment)
needs to be configured with a factory function. In `settings.py`, when configuring your `TEMPLATES`
backend, set the `environment` option to the path of your environment factory function.

```python title="myproject/liquid.py"
from liquid import Environment
from liquid_extra import filters
from liquid_extra import tags

def environment(**options):
    env = Environment(**options)
    env.add_filter("json", filters.JSON())
    env.add_tag(tags.IfNotTag)
    # Register more filters or tags here.
    return env
```

```python title="settings.py"
TEMPLATES = [
    {
        'BACKEND': 'django_liquid.liquid.Liquid',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'myproject.liquid.environment'
        },
    },
]
```
