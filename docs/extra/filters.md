# Extra Filters

This page documents extra filters that are not included in standard Liquid. See the
[filter reference](/language/filters) for a details of all standard filters.

:::caution
These filters are not part of "standard" Liquid. If you choose to use them in your templates, those
templates are unlikely to render correctly with other implementations of Liquid.
:::

## index

`<array> | index: <object>`

Return the zero-based index of the first occurrence of the argument object in the input array. If
the argument object is not in the array, `nil` is returned.

Register `index` with a [liquid.Environment](/api/Environment) to make it available to templates
rendered from that environment.

```python
from liquid import Environment
from liquid_extra import filters

env = Environment()
env.add_filter("index", filters.index)
```

```liquid title="template"
{% assign colors = "red, blue, green" | split: ", "%}
{{ colors | index 'blue' }}
```

```plain title="output"
1
```

## json

`<object> | json`

Serialize objects as a JSON (JavaScript Object Notation) formatted string.

The `json` filter uses Python's default [JSONEncoder](https://docs.python.org/3.8/library/json.html#json.JSONEncoder),
supporting `dict`, `list`, `tuple`, `str`, `int`, `float`, some Enums, `True`, `False` and `None`.

Register `json` with a [liquid.Environment](/api/Environment) to make it available to templates
rendered from that environment. Notice that `filters.JSON` is a class that need instantiating.

```python
from liquid import Environment
from liquid_extra import filters

env = Environment()
env.add_filter("json", filters.JSON())
```

```json title="data"
{
  "product": {
    "id": 1234,
    "name": "Football"
  }
}
```

```liquid title="template"
<script type="application/json">
    {{ product | json }}
</script>
```

```html title=output
<script type="application/json">
  { "id": 1234, "name": "Football" }
</script>
```

When registering the `JSON` filter, you can optionally pass a `default` argument. `default` will be
passed to `json.dumps` and should be a function that gets called for objects that can't otherwise be
serialized. For example, this default function adds support for serializing
[data classes](https://docs.python.org/3/library/dataclasses.html).

```python
from dataclasses import dataclass
from dataclasses import asdict
from dataclasses import is_dataclass

from liquid import Environment
from liquid_extra import filters

env = Environment()

def default(obj):
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError(f"can't serialize object {obj}")

env.add_filter("json", filters.JSON(default=default))
```

## stylesheet_tag

`<string> | stylesheet_tag`

Return an HTML `link` tag, as a string, with `href` equal to the input string, which should be a
URL.

Register `stylesheet_tag` with a [liquid.Environment](/api/Environment) to make it available to
templates rendered from that environment.

```python
from liquid import Environment
from liquid_extra import filters

env = Environment()
env.add_filter("stylesheet_tag", filters.stylesheet_tag)
```

```json title="data"
{
  "url": "https://example.com/static/style.css"
}
```

```liquid title="template"
{{ url | stylesheet_tag }}
```

```plain title="output"
<link href="https://example.com/static/style.css" rel="stylesheet" type="text/css" media="all" />
```

## script_tag

`<string> | script_tag`

Return an HTML `script` tag, as a string, with `src` equal to the input string, which should be a
URL.

Register `script_tag` with a [liquid.Environment](/api/Environment) to make it available to
templates rendered from that environment.

```python
from liquid import Environment
from liquid_extra import filters

env = Environment()
env.add_filter("script_tag", filters.script_tag)
```

```json title="data"
{
  "url": "https://example.com/static/app.js"
}
```

```liquid title="template"
{{ url | script_tag }}
```

```plain title="output"
<script src="https://example.com/static/app.js" type="text/javascript"></script>
```

## t (translate)

`<string> | t [: <identifier>: <object> [, <identifier>: object] ... ]`

Replace translation keys with strings for the current locale.

Pass a mapping of locales to translations to the `Translate` filter when you register it. The
current locale is read from the template context at render time, by looking for a variable named
`locale`. `locale` will default to `default` if it is undefined.

Register `t` with a [liquid.Environment](/api/Environment) to make it available to templates
rendered from that environment.

```python
from liquid import Environment
from liquid_extra.filters import Translate

some_locales = {
    "default": {
        "layout": {
            "greeting": r"Hello {{ name }}",
        },
        "cart": {
            "general": {
                "title": "Shopping Basket",
            },
        },
        "pagination": {
            "next": "Next Page",
        },
    },
    "de": {
        "layout": {
            "greeting": r"Hallo {{ name }}",
        },
        "cart": {
            "general": {
                "title": "Warenkorb",
            },
        },
        "pagination": {
            "next": "Nächste Seite",
        },
    },
}

env = Environment()
env.add_filter(Translate.name, Translate(locales=some_locales))
```

```json title="data"
{
  "locale": "de",
  "user": {
    "name": "Welt"
  }
}
```

```liquid title="template"
{{ 'layout.cart.general.title' | t }}
{{ 'layout.greeting' | t: name: user.name }}
```

```plain title="output"
Warenkorb
Hallo Welt
```

Notice that the `t` filter accepts arbitrary named parameters. Named parameters can be used to
substitute fields in translation strings with values from the template context.

It you don't give `Translate` any locales or you leave it empty, you'll always get the translation
key back unchanged.
