# Liquid environments

Template parsing and rendering behavior is configured using an instance of [`Environment`](api/environment.md). Once configured, you'd parse templates with [`Environment.from_string()`](api/environment.md#liquid.Environment.from_string) or [`Environment.get_template()`](api/environment.md#liquid.Environment.get_template), both of which return an instance of [`BoundTemplate`](api/template.md).

## The default environment

The default environment, `liquid.DEFAULT_ENVIRONMENT`, and an instance of `Environment` without any arguments are equivalent to the following `Environment` subclass and constructor arguments.

```python
from liquid import BoundTemplate
from liquid import DictLoader
from liquid import Environment
from liquid import Mode
from liquid import Undefined
from liquid import builtin


class MyLiquidEnvironment(Environment):
    context_depth_limit = 30
    loop_iteration_limit = None
    local_namespace_limit = None
    output_stream_limit = None
    template_class = BoundTemplate
    suppress_blank_control_flow_blocks = True
    shorthand_indexes = False
    string_sequences = False
    string_first_and_last = False
    logical_not_operator = False
    logical_parentheses = False
    ternary_expressions = False
    keyword_assignment = False

    def setup_tags_and_filters(self):
        builtin.register(self)


env = MyLiquidEnvironment(
    autoescape=False,
    comment_end_string="#}",
    comment_start_string="{#",
    extra=False,
    globals=None,
    loader=DictLoader({}),
    statement_end_string=r"}}",
    statement_start_string=r"{{",
    strict_filters=True,
    tag_end_string=r"%}",
    tag_start_string=r"{%",
    template_comments=False,
    tolerance=Mode.STRICT,
    undefined=Undefined,
)
```

## Managing tags and filters

[`builtin.register()`](api/builtin.md#liquid.builtin.register) registers all the default tags and filters with the environment. You are encouraged to override `setup_tags_and_filters()` in your `Environment` subclasses to add optional or custom tags and filters, remove unwanted default tags and filters, and possibly replace default implementation with your own.

It's also OK to manipulate [`Environment.tags`](api/environment.md#liquid.Environment.tags) and [`Environment.filters`](api/environment.md#liquid.Environment.filters) directly after an `Environment` instance has been created. They are just dictionaries mapping tag names to instances of [`Tag`](api/tag.md) and filter names to callables, respectively.

```python
from liquid import Environment

env = Environment()
del env.tags["include"]
```

### Extra tags and filters

Python Liquid includes some [extra tags](optional_tags.md) and [extra filters](optional_filters.md) that are not enabled by default. If you want to enable them all, pass `extra=True` when constructing a Liquid [`Environment`](api/environment.md).

```python
from liquid import Environment

env = Environment(extra=True)
print(env.render("{{ 100457.99 | money }}"))
# $100,457.99
```

## Managing global variables

By default, global template variables attached to instances of [`Template`](api/template.md) take priority over global template variables attached to an `Environment`. You can change this priority or otherwise manipulate the `globals` dictionary for a `Template` by overriding [`Environment.make_globals()`](api/environment.md#liquid.Environment.make_globals).

Also see [Render context data](render_context.md).

```python
from typing import Mapping
from liquid import Environment

class MyLiquidEnvironment(Environment):

    def make_globals(
        self,
        globals: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        """Combine environment globals with template globals."""
        if globals:
            # Template globals take priority over environment globals.
            return {**self.globals, **globals}
        return dict(self.globals)
```

## Tolerance

Templates are parsed and rendered in strict mode by default. Where syntax and render-time type errors raise an exception as soon as possible. You can change the error tolerance mode with the `tolerance` argument to [`Environment`](api/environment.md).

Available modes are `Mode.STRICT`, `Mode.WARN` and `Mode.LAX`.

```python
from liquid import Environment
from liquid import FileSystemLoader
from liquid import Mode

env = Environment(
    loader=FileSystemLoader("templates/"),
    tolerance=Mode.LAX,
)
```

## HTML auto escape

When `autoescape` is `True`, [render context variables](render_context.md) will be automatically escaped to produce HTML-safe strings on output.

You can be explicitly mark strings as _safe_ by wrapping them in `Markup()` and [drops](variables_and_drops.md) can implement the [special `__html__()` method](variables_and_drops.md#__html__).

```python
from markupsafe import Markup
from liquid import Environment

env = Environment(autoescape=True)
template = env.from_string("<p>Hello, {{ you }}</p>")
print(template.render(you=Markup("<em>World!</em>")))
```

## Resource limits

For deployments where template authors are untrusted, you can set limits on some resources to avoid malicious templates from consuming too much memory or too many CPU cycles. Limits are set by subclassing [`Environment`](api/environment.md) and setting some class attributes.

```python
from liquid import Environment

class MyEnvironment(Environment):
    context_depth_limit = 30
    local_namespace_limit = 2000
    loop_iteration_limit = 1000
    output_stream_limit = 15000


env = MyEnvironment()

template = env.from_string("""\
{% for x in (1..1000000) %}
{% for y in (1..1000000) %}
    {{ x }},{{ y }}
{% endfor %}
{% endfor %}
""")

template.render()
# liquid.exceptions.LoopIterationLimitError: loop iteration limit reached
```

### Context depth limit

[`context_depth_limit`](api/environment.md#liquid.Environment.context_depth_limit) is the maximum number of times a render context can be extended or wrapped before a `ContextDepthError` is raised. This helps us guard against recursive use of the `include` and `render` tags. The default context depth limit is 30.

```python
from liquid import Environment
from liquid import DictLoader

env = Environment(
    loader=DictLoader(
        {
            "foo": "{% render 'bar' %}",
            "bar": "{% render 'foo' %}",
        }
    )
)

template = env.from_string("{% render 'foo' %}")
template.render()
# liquid.exceptions.ContextDepthError: maximum context depth reached, possible recursive render
#   -> '{% render 'bar' %}' 1:3
#   |
# 1 | {% render 'bar' %}
#   |    ^^^^^^ maximum context depth reached, possible recursive render
```

### Local Namespace Limit

[`local_namespace_limit`](api/environment.md#liquid.Environment.local_namespace_limit) is the maximum number of bytes (according to `sys.getsizeof()`) allowed in a template's local namespace, per render, before a `LocalNamespaceLimitError` exception is raised. Note that we only count the size of the local namespace values, not its keys.

The default `local_namespace_limit` is `None`, meaning there is no limit.

```python
from liquid import Environment

class MyEnvironment(Environment):
    local_namespace_limit = 50  # Very low, for demonstration purposes.

env = MyEnvironment()

template = env.from_string("""\
{% assign x = "Nunc est nulla, pellentesque ac dui id erat curae." %}
""")

template.render()
# liquid.exceptions.LocalNamespaceLimitError: local namespace limit reached
```

!!! warning

    [PyPy](https://doc.pypy.org/en/latest/cpython_differences.html) does not implement `sys.getsizeof`. Instead of a size in bytes, when run with PyPy, `local_namespace_limit` will degrade to being the number of distinct values in a template's local namespace.

### Loop Iteration Limit

[`loop_iteration_limit`](api/environment.md#liquid.Environment.loop_iteration_limit) is the maximum number of loop iterations allowed before a `LoopIterationLimitError` is raised.

The default `loop_iteration_limit` is `None`, meaning there is no limit.

```python
from liquid import Environment

class MyEnvironment(Environment):
    loop_iteration_limit = 999


env = MyEnvironment()

template = env.from_string("""\
{% for x in (1..100) %}
{% for y in (1..100) %}
    {{ x }},{{ y }}
{% endfor %}
{% endfor %}
""")

template.render()
# liquid.exceptions.LoopIterationLimitError: loop iteration limit reached
```

Other built in tags that contribute to the loop iteration counter are `render`, `include` (when using their `{% render 'thing' for some.thing %}` syntax) and `tablerow`. If a partial template is rendered within a `for` loop, the loop counter is carried over to the render context of the partial template.

### Output Stream Limit

The maximum number of bytes that can be written to a template's output stream, per render, before an `OutputStreamLimitError` exception is raised. The default `output_stream_limit` is `None`, meaning there is no limit.

```python
from liquid import Environment

class MyEnvironment(Environment):
    output_stream_limit = 20  # Very low, for demonstration purposes.


env = MyEnvironment()

template = env.from_string("""\
{% if false %}
this is never rendered, so will not contribute the the output byte counter
{% endif %}
Hello, {{ you }}!
""")

template.render(you="World")
# '\nHello, World!\n'

template.render(you="something longer that exceeds our limit")
# liquid.exceptions.OutputStreamLimitError: output stream limit reached
```

## String sequences

By default, strings in Liquid can not be looped over with the `{% for %}` tag and characters in a string can not be selected by index.

Setting the `string_sequences` class attribute to `True` tells Python Liquid to treat strings as sequences, meaning we can loop over Unicode characters in a string or retrieve a Unicode "character" by its index.

## String first and last

Strings don't respond to the special `.first` and `.last` properties by default. Set `string_first_and_last` to `True` to enable `.first` and `.last` for strings.

## Logical not operator

The logical `not` operator is disabled by default. Set the `logical_not_operator` class attribute to `True` to enable `not` inside `{% if %}`, `{% unless %}` and ternary expressions.

## Logical parentheses

By default, terms in `{% if %}` tag expressions can not be grouped to control precedence. Set the `logical_parentheses` class attribute to `True` to enable grouping terms with parentheses.

## Ternary expressions

Enable ternary expressions in output statements, assign tags and echo tags by setting the `ternary_expressions` class attribute to `True`.

```
{{ <expression> if <expression> else <expression> }}
```

Inline conditional expressions can be used as an alternative to the longer form [`{% if %}` tag](tag_reference.md#if).

```liquid
{{ "bar" if x.y == z else "baz" }}
```

Filters can be applied to either branch.

```liquid
{{ "bar" | upcase if x else "baz" | capitalize }}
```

Or applied to the result of the conditional expression as a whole using _tail filters_. Notice the double pipe symbol (`||`).

```liquid
{{ "bar" if x else "baz" || upcase | append: "!" }}
```

## Keyword assignment

By default, named arguments must separated names from values with a colon (`:`). Set the `keyword_assignment` class attribute to `True` to allow equals (`=`) or a colon between names and their values.

## What's next?

See [loading templates](loading_templates.md) for more information about configuring a template loader and [undefined variables](variables_and_drops.md#undefined-variables) for information about managing undefined variables.
