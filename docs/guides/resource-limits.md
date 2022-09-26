# Resource Limits

**_New in version 1.4.0_**

For deployments where template authors are untrusted, you can set limits on some resources to avoid malicious templates from consuming too much memory or too many CPU cycles. Set one or more resource limits by subclassing a Liquid [Environment](../api/environment.md).

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
# LoopIterationLimitError: loop iteration limit reached, on line 1
```

## Context Depth Limit

The maximum number of times a render context can be extended or wrapped before a [`ContextDepthError`](../api/exceptions.md#liquidexceptionscontextdeptherror) is raised.

This helps us guard against recursive use of the `include` and `render` tags. The default context depth limit is 30. Before Python Liquid version 1.4.0, a context depth limit of 30 was hard coded.

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
# ContextDepthError: maximum context depth reached, possible recursive render, on line 1
```

## Local Namespace Limit

The maximum number of bytes (according to `sys.getsizeof()`) allowed in a template's local namespace, per render, before a [`LocalNamespaceLimitError`](../api/exceptions.md#liquidexceptionslocalnamespacelimiterror) exception is raised. Note that we only count the size of the local namespace values, not its keys.

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
# LocalNamespaceLimitError: local namespace limit reached, on line 1
```

:::caution
[PyPy](https://doc.pypy.org/en/latest/cpython_differences.html) does not implement `sys.getsizeof`. Instead of a size in bytes, when run with PyPy, `local_namespace_limit` will degrade to being the number of distinct values in a template's local namespace.
:::

## Loop Iteration Limit

The maximum number of loop iterations allowed before a [`LoopIterationLimitError`](../api/exceptions.md#liquidexceptionsloopiterationlimiterror) is raised.

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
# LoopIterationLimitError: loop iteration limit reached, on line 1
```

Other built in tags that contribute to the loop iteration counter are `render`, `include` (when using their `{% render 'thing' for some.thing %}` syntax) and `tablerow`. If a partial template is rendered within a `for` loop, the loop counter is carried over to the render context of the partial template.

## Output Stream Limit

The maximum number of bytes that can be written to a template's output stream, per render, before an [`OutputStreamLimitError`](../api/exceptions.md#liquidexceptionsoutputstreamlimiterror) exception is raised.

The default `output_stream_limit` is `None`, meaning there is no limit.

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
# OutputStreamLimitError: output stream limit reached, on line 4
```

## String to Integer Limit

**_New in version 1.4.4_**

[CVE-2020-10735](https://github.com/python/cpython/issues/95778) describes a potential denial of service attack by converting very long strings to integers. As of version 1.4.4, Python Liquid will raise a `LiquidValueError` if an attempt is made to cast a long string to an integer.

Due to some unfortunate early Python Liquid design decisions, this is an interpreter-wide limit, unlike other limits described on this page, which are set per `liquid.Environment`.

Python Liquid will look for a `LIQUIDINTMAXSTRDIGITS` [environment variable](https://en.wikipedia.org/wiki/Environment_variable), giving the maximum number of digits allowed before attempting a str to int conversion. We will fall back to looking for `PYTHONINTMAXSTRDIGITS` before defaulting to `4300`. Use `LIQUIDINTMAXSTRDIGITS` when you want to use a lower limit for Liquid while keeping Python's limit higher.

When using [patched versions](https://github.com/python/cpython/pull/96500/files#diff-08a31a70dd1f6d97aa8dacdce77db4de04c700d9949be1af611a595186aad5b3) of Python, Liquid will **not** honour `sys.set_int_max_str_digits`. If Python's limit is lower than Liquid's, it will be possible to get a `ValueError` exception instead of a `LiquidValueError` when parsing Liquid templates.

:::caution
Python Liquid's default limit helps guard against malicious templates authors. Be sure to validate user controlled inputs that might appear in a Liquid render context.
:::
