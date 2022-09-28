# Babel Tags

Optional [tags](../language/tags.md) provided by the [liquid-babel](./introduction.md) package.

## translate

**_New in Liquid Babel version 0.3.0_**

```
{% translate
    [context: <string>]
    [, count: <number>]
    [, <identifier>: <object> [| <filter>] ... ] %}
  <text,variable> ...
[ {% plural %} <text,variable> ... ]
{% endtranslate %}
```

Render the localized translation of a message. If a German [Translations](./introduction.md#message-catalogs) object is found in the current render context:

```liquid
{% translate %}
  Hello, World!
{% endtranslate %}
```

```plain title="output"
Hallo Welt!
```

If a `{% plural %}` block follows the message text and the `count` argument is considered plural, the `{% plural %}` block will be rendered instead.

```liquid
{% translate count: 2 %}
  Hello, World!
{% plural %}
  Hello, Worlds!
{% endtranslate %}
```

```plain title="output"
Hallo Welten!
```

Keyword arguments are used to populate translatable message variables. These variables look like Liquid output statements, but can not use dotted or bracketed property/attribute access, or filters.

```liquid
{% translate you: 'Sue' %}
  Hello, {{ you }}!
{% endtranslate %}
```

```plain title="output"
Hallo Sue!
```

Keyword arguments can use simple, no-argument filters like `size` and `capitalize`.

```liquid
{% translate you: 'Sue' | captialize %}
  Hello, {{ you }}!
{% endtranslate %}
```

```plain title="output"
Hallo SUE!
```

### Options

The included `translate` tag can be customized by subclassing `TranslateTag` and overriding class attributes and/or methods. This example changes its name from `translate` to `trans` and disables support for filtered arguments.

```python
from liquid import Environment
from liquid_babel.tags.translate import TranslateTag

class MyTranslateTag(TranslateTag):
    name = "trans"
    end = "endtrans"
    simple_filters = False

env = Environment()
env.add_tag(MyTranslateTag)
```

This table shows configurable `TranslateTag` class attributes/property.

| Property         | Type       | Description                                                                     | Default          |
| ---------------- | ---------- | ------------------------------------------------------------------------------- | ---------------- |
| `name`           | `str`      | The name of the tag that starts the block, as used by template authors.         | `"translate"`    |
| `end`            | `str`      | The name of the tag that ends the block, as used by template authors.           | `"endtranslate"` |
| `plural_name`    | `str`      | The name of the tag that starts the plural block, as used by template authors.  | `"plural"`       |
| `simple_filters` | `bool`     | If `True`, allow simple, no-argument filters to be used with keyword arguments. | `True`           |
| `trim_messages`  | `bool`     | If `True`, normalize message whitespace.                                        | `True`           |
| `node_class`     | `ast.Node` | The node to return from `TranslateTag.parse()`.                                 | `TranslateNode`  |

Further customization can be achieved by extending `TranslateNode` and overriding `resolve_count()`, `resolve_message_context()` and/or `gettext()`.
