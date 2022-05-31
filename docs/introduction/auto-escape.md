# HTML Auto-Escape

Python Liquid offers HTML auto-escaping. Where render context variables are automatically escaped on output. Install optional dependencies for auto-escaping using the `autoescape` extra.

```shell
$ pipenv install python-liquid[autoescape]
```

Or

```shell
$ python -m pip install -U python-liquid[autoescape]
```

Auto-escaping is disabled by default. Enable it by setting the [`Environment`](../api/environment.md) or [`Template`](../api/template.md) `autoescape` argument to `True`.

```python
from liquid import Environment
env = Environment(autoescape=True)
template = env.from_string("<p>Hello, {{ you }}</p>")
print(template.render(you='</p><script>alert("XSS!");</script>'))
```

```plain title="output"
<p>Hello, &lt;/p&gt;&lt;script&gt;alert(&#34;XSS!&#34;);&lt;/script&gt;</p>
```

## Markup

Mark a string as "safe" by wrapping it in a `Markup` object.

```python
from liquid import Environment, Markup
env = Environment(autoescape=True)
template = env.from_string("<p>Hello, {{ you }}</p>")
print(template.render(you=Markup("<em>World!</em>")))
```

```plain title=output
'<p>Hello, <em>World!</em></p>'
```

## Safe

Alternatively use the non-standard [safe](../language/filters.md#safe) filter.

:::caution
The `safe` filter is not available in "standard" Liquid.
:::

```python
from liquid import Environment
env = Environment(autoescape=True)
template = env.from_string("<p>Hello, {{ you | safe }}</p>")
print(template.render(you="<em>World!</em>"))
```

```plain title=output
'<p>Hello, <em>World!</em></p>'
```
