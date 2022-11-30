# Extra Filters

**_New in version 1.5.0_**

This page documents extra filters that are not included in standard Liquid. See the [filter reference](../language/filters.md) for a details of all standard filters. Each filter described here must be registered with a [`liquid.Environment`](../api/environment.md) to make it available to templates rendered from that environment.

## index

`<array> | index: <object>`

Return the zero-based index of the first occurrence of the argument object in the input array. If the argument object is not in the array, `nil` is returned.

```python
from liquid import Environment
from liquid.extra import filters

env = Environment()
env.add_filter("index", filters.index)

template = env.from_string("""\
{% assign colors = "red, blue, green" | split: ", "%}
{{ colors | index: 'blue' }}
""")

print(template.render())
```

```plain title="output"
1
```

## json

`<object> | json`

Serialize an object as a JSON (JavaScript Object Notation) formatted string.

```python
from liquid import Environment
from liquid.extra import filters

env = Environment()
env.add_filter("json", filters.JSON())

template = env.from_string("""\
<script type="application/json">
  {{ product | json }}
</script>
""")

data = {
  "product": {
    "id": 1234,
    "name": "Football"
  }
}

print(template.render(**data))
```

```html title=output
<script type="application/json">
  { "id": 1234, "name": "Football" }
</script>
```

The `json` filter uses Python's default [`JSONEncoder`](https://docs.python.org/3.8/library/json.html#json.JSONEncoder), supporting `dict`, `list`, `tuple`, `str`, `int`, `float`, some Enums, `True`, `False` and `None`.

When registering the `JSON` filter, you can optionally pass a `default` argument. `default` will be passed to `json.dumps` and should be a function that gets called for objects that can't otherwise be serialized. For example, this default function adds support for serializing [data classes](https://docs.python.org/3/library/dataclasses.html).

```python
from dataclasses import dataclass
from dataclasses import asdict
from dataclasses import is_dataclass

from liquid import Environment
from liquid.extra import filters

env = Environment()

def default(obj):
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError(f"can't serialize object {obj}")

env.add_filter("json", filters.JSON(default=default))
```

## script_tag

`<string> | script_tag`

Return an HTML `script` tag, as a string, with `src` equal to the input string, which should be a URL.

```python
from liquid import Environment
from liquid.extra import filters

env = Environment()
env.add_filter("script_tag", filters.script_tag)

template = env.from_string("{{ url | script_tag }}")
print(template.render(url="https://example.com/static/app.js"))
```

```plain title="output"
<script src="https://example.com/static/app.js" type="text/javascript"></script>
```

## stylesheet_tag

`<string> | stylesheet_tag`

Return an HTML `link` tag, as a string, with `href` equal to the input string, which should be a URL.

```python
from liquid import Environment
from liquid.extra import filters

env = Environment()
env.add_filter("stylesheet_tag", filters.stylesheet_tag)

template = env.from_string("{{ url | stylesheet_tag }}")
print(template.render(url="https://example.com/static/style.css"))
```

```plain title="output"
<link href="https://example.com/static/style.css" rel="stylesheet" type="text/css" media="all" />
```
