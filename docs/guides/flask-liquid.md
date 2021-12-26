# Flask Liquid

A [Flask](https://palletsprojects.com/p/flask/) extension for Python Liquid.

## Install

Install Flask Liquid using [Pipenv](https://pipenv.pypa.io/en/latest/):

```shell
$ pipenv install flask-liquid
```

Or [pip](https://pip.pypa.io/en/stable/getting-started/):

```shell
$ python -m pip install -U flask-liquid
```

## Getting Started

Flask Liquid provides `render_template` and `render_template_string` functions that behave much like the [Flask equivalents](https://flask.palletsprojects.com/en/2.0.x/quickstart/#rendering-templates) of the same name. By default Flask Liquid will look for templates in [app.template_folder](https://flask.palletsprojects.com/en/2.0.x/api/#flask.Flask.template_folder). The same location Flask uses for Jinja templates.

```python title="app.py"
from flask import Flask

from flask_liquid import Liquid
from flask_liquid import render_template

app = Flask(__name__)
liquid = Liquid(app)

@app.route("/hello/")
@app.route("/hello/<name>")
def index(name=None):
    return render_template("index.html", name=name)
```

Set the `LIQUID_TEMPLATE_FOLDER` configuration value to change the Liquid template folder independently of `app.template_folder`.

```python title="app.py"
app = Flask(__name__)
app.config.update(
    LIQUID_TEMPLATE_FOLDER="/path/to/liquid/templates/",
)

liquid = Liquid(app)
```

## Factories and Blueprints

When using the factory pattern, use `Liquid.init_app(app)` instead. Any `LIQUID_*` configuration values stored on the app will override `Liquid` constructor arguments when `init_app` is called.

```python title="app.py"
from flask import Flask
from flask_liquid import Liquid

from yourapp.blueprints import some_blueprint

liquid = Liquid()

def create_app(config=None):
    app = Flask(__name__)
    app.register_blueprint(some_blueprint.bp)

    liquid.init_app(app)

    return app
```

## Mixing Jinja and Liquid

If you want to use Jinja and Liquid templates side by side, import Liquid render functions using an alias.

```python
from flask import render_template
from flask_liquid import render_template as render_liquid_template
```

## Auto Escape

Unlike a standard [liquid.Environment()](/api/Environment), Flask Liquid enables HTML auto-escaping by default. You can disable auto-escaping by passing `autoescape=False` to `flask_liquid.Liquid()` or setting the `LIQUID_AUTOESCAPE` configuration value to `False`.

To render markup from a Liquid snippet inside a Jinja template (or vice versa), mark the string returned by `render_liquid_template` as safe using `Markup`, then include it in the Jinja template context. That is assuming you trust values in the Liquid render context or have HTML escaped them already.

```python title="app.py"
from flask import Flask
from flask import Markup
from flask import render_template

from flask_liquid import Liquid
from flask_liquid import render_template as render_liquid_template

app = Flask(__name__)
liquid = Liquid(app)

@app.route("/hello")
def hello():
    user_content = render_liquid_template("content.liquid")
    return render_template("page.html", content=Markup(user_content))
```

## Flask Standard Context

Flask has some [standard context variables](https://flask.palletsprojects.com/en/1.1.x/templating/#standard-context) that are included in each Jinja template context automatically. Flask Liquid does not include these variables. If you need access to the Flask session or request, for example, you'll need to manually map session or request properties to Liquid context keys.

```python title="app.py"
from flask import Flask
from flask import request

from flask_liquid import Liquid
from flask_liquid import render_template

app = Flask(__name__)
liquid = Liquid(app)

@app.route("/hello/")
@app.route("/hello/<name>")
def index(name=None):
    return render_template("index.html", name=name, path=request.path)
```

## Context Processors

When the `LIQUID_FLASK_CONTEXT_PROCESSORS` configuration value is set to `True`, Flask context processors will update Liquid template contexts too.

:::info
Remember that Python Liquid uses the [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence) and [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping) interfaces for resolving object properties. See [Objects and Drops](/introduction/objects-and-drops).
:::

```python title="app.py"
from flask import Flask
from flask import request

from flask_liquid import Liquid
from flask_liquid import render_template

app = Flask(__name__)
app.config.update(
    LIQUID_FLASK_CONTEXT_PROCESSORS=True,
)

liquid = Liquid(app)

@app.context_processor
def extra_context():
    return {"request_path": request.path}

@app.route("/hello/")
@app.route("/hello/<name>")
def index(name=None):
    return render_template("index.html", name=name)
```

## Signals

By default, when [signals are available](https://flask.palletsprojects.com/en/1.1.x/api/#flask.signals.signals_available), Flask Liquid will send a `before_render_template` and `template_rendered` signal for each successful call to `render_template` and `render_template_string`.

You can disable these signals for Liquid templates by setting the `LIQUID_FLASK_SIGNALS` configuration value to `False`.

## Async Support

Render templates asynchronously using `flask_liquid.render_template_async()` and `flask_liquid.render_template_string_async()`.

```python title="app.py"
from flask import Flask

from flask_liquid import Liquid
from flask_liquid import render_template_async

app = Flask(__name__)
liquid = Liquid(app)

@app.route("/render/<name>")
async def render_by_name(name=None):
    return await render_template_async(name)
```

## Configuration Values

The following [configuration values](https://flask.palletsprojects.com/en/2.0.x/config/) can be used instead of passing arguments to `flask_liquid.Liquid()`.

| Configuration Value             | Liquid Argument          | Default                                 |
| ------------------------------- | ------------------------ | --------------------------------------- |
| LIQUID_TAG_START_STRING         | tag_start_string         | `"{%"`                                  |
| LIQUID_TAG_END_STRING           | tag_end_string           | `"%}"`                                  |
| LIQUID_STATEMENT_START_STRING   | statement_start_string   | `"{{"`                                  |
| LIQUID_STATEMENT_END_STRING     | statement_end_string     | `"}}"`                                  |
| LIQUID_TEMPLATE_COMMENTS        | template_comments        | `False`                                 |
| LIQUID_COMMENT_START_STRING     | statement_start_string   | `"{#"`                                  |
| LIQUID_COMMENT_END_STRING       | statement_end_string     | `"#}"`                                  |
| LIQUID_TOLERANCE                | mode                     | `liquid.Mode.STRICT`                    |
| LIQUID_UNDEFINED                | undefined                | `liquid.Undefined`                      |
| LIQUID_STRICT_FILTERS           | strict_filters           | `True`                                  |
| LIQUID_TEMPLATE_FOLDER          |                          | `app.template_folder`                   |
|                                 | loader                   | `FileSystemLoader(app.template_folder)` |
| LIQUID_AUTOESCAPE               | autoescape               | `True`                                  |
| LIQUID_AUTO_RELOAD              | auto_reload              | `True`                                  |
| LIQUID_EXPRESSION_CACHE_SIZE    | expression_cache_size    | `0`                                     |
| LIQUID_FLASK_CONTEXT_PROCESSORS | flask_context_processors | `False`                                 |
| LIQUID_FLASK_SIGNALS            | flask_signals            | `True`                                  |

Note that if you specify a [loader](/introduction/loading-templates) with the `loader` argument to `flask_liquid.Liquid()`, Flask Liquid will use that instead of creating a [FileSystemLoader](/api/FileSystemLoader) pointing to `LIQUID_TEMPLATE_FOLDER`.
