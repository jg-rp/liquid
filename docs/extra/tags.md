# Extra Tags

This page documents extra tags that are not included in standard Liquid. See the [tag reference](../language/tags.md) for details of all standard tags. Each tag described here must be registered with a [`liquid.Environment`](../api/environment.md) to make it available to templates rendered from that environment.

## extends / block

**_New in version 1.8.0_**

```plain
{% extends "<string>" %}
```

```plain
{% block <identifier,string> [, required] %}
  <literal,statement,tag> ...
{% endblock [<identifier,string>] %}
```

The `{% extends %}` and `{% block %}` tags add template inheritance features to Python Liquid. In this example `page.html` inherits from `base.html` and overrides the `content` block. As `page.html` does not define a `footer` block, the footer from `base.html` is used.

```python
from liquid import DictLoader
from liquid import Environment
from liquid.extra import add_inheritance_tags

loader = DictLoader(
    {
        "base.html": (
            "<body>\n"
            '  <div id="content">{% block content required %}{% endblock %}</div>\n'
            '  <div id="footer">{% block footer %}Default footer{% endblock %}</div>\n'
            "</body>"
        ),
        "page.html": (
            "{% extends 'base.html' %}\n"
            "{% block content %}Hello, {{ you }}!{% endblock %}"
        ),
    }
)

env = Environment(loader=loader)
add_inheritance_tags(env)

template = env.get_template("page.html")
print(template.render(you="World"))
```

```html title="output"
<body>
  <div id="content">Hello, World!</div>
  <div id="footer">Default footer</div>
</body>
```

A template can contain at most one `{% extends %}` tag, and that tag should normally be the first in the template. All other template text and tags (including whitespace) preceding `{% extends %}` will be output normally. Subsequent template text and tags outside any `{% block %}` tags will be ignored, unless rendering a base template directly.

As soon as an `{% extends %}` tag is found, template rendering stops and Python Liquid loads the parent template (using the configured [loader](../introduction/loading-templates.md)) before searching for `{% block %}` tags. We keep loading and searching up the inheritance chain until a parent template with no `{% extends %}` tag is found, this is the _base_ template.

The base template is then rendered, substituting its blocks with those defined in its children.

### Block Names

Every `{% block %}` must have a name and that name must be unique within a single template. Block names must be valid Liquid identifiers, optionally enclosed in quotes (quoted and unquoted block names are equivalent).

`{% endblock %}` tags can include a name too. If given a name and that name does not match the one given at the start of the block, a `TemplateInheritanceError` is raised when parsing the template.

```liquid
<body>
  <div id="content">
    {% block content %}
      {% block title %}
        <h1>Some Title</h1>
      {% endblock title %}
    {% endblock content %}
  </div>
  <div id="footer">
    {% block footer %}
      Default footer
    {% endblock footer %}
  </div>
</body>
```

### Block Scope

All blocks are scoped. Variables defined in base templates and enclosing blocks will be in scope when rendering overridden blocks.

```liquid title="base"
{% assign thing = 'item' %}
{% for i in (1..3) %}
  {% block list-item %}{% endblock %}
{% endfor %}
```

```liquid title="child"
{% extends "base" %}
{% block list-item %}
  {{ thing }} #{{ i }}
{% endblock %}
```

```plain title="output"
item #1

item #2

item #3
```

Variables defined in an overridden block will go out of scope after that block has been rendered.

```liquid title="base"
{% assign greeting = "Hello" %}
{% block say-hi %}{{ greeting }}, World!{% endblock %}
{{ greeting }}, World!
```

```liquid title="child"
{% extends "base" %}
{% block say-hi %}
  {% assign greeting = "Goodbye" %}
  {{ greeting }}, World!
  {{ block.super }}
{% endblock %}
```

```plain title="output"
Goodbye, World!
Hello, World!

Hello, World!
```

### Required Blocks

Use the `{% block %}` tag's `required` argument to indicate that the block must be overridden by a child template. If a required block does not get implemented by a child template, a `RequiredBlockError` exception is raised at render time.

In this example, if the template were to be rendered directly, we would expect a `RequiredBlockError` due to the `content` block being required.

```liquid title="base"
<head>
  {% block head %}{% endblock %}
<head>
<body>
  <div id="content">{% block content required %}{% endblock %}</div>
  <div id="footer">{% block footer %}Default footer{% endblock %}</div>
</body>
```

### Super Blocks

A `block` object is available inside every `{% block %}` tag. It has just one property, `super`. If a `{% block %}` is overriding a parent block, `{{ block.super }}` will render the parent's implementation of that block.

In this example we use `{{ block.super }}` in the `footer` block to output the base template's footer with a year appended to it.

```liquid title="base"
<head>
  {% block head %}{% endblock %}
<head>
<body>
  <div id="content">{% block content required %}{% endblock %}</div>
  <div id="footer">{% block footer %}Default footer{% endblock %}</div>
</body>
```

```liquid title="child"
{% extends "base" %}
{% block content %}Hello, World!{% endblock %}
{% block footer %}{{ block.super }} - 2023{% endblock %}
```

```html title="output"
<body>
  <div id="content">Hello, World!</div>
  <div id="footer">Default footer - 2023</div>
</body>
```

## if (not)

**_New in version 1.5.0_**

A drop-in replacement for the standard [`if`](../language/tags.md#if) tag that supports a logical `not` operator and grouping terms with parentheses. See [the tag reference](../language/tags.md#expressions) for a description of standard `if` expressions.

In this example, `{% if not user %}` is equivalent to `{% unless user %}`, however, `not` can also be used after `and` and `or`, like `{% if user.active and not user.title %}`, potentially saving nested `if` and `unless` tags.

```python
from liquid import Environment
from liquid.extra.tags import IfNotTag

env = Environment()
env.add_tag(IfNotTag)

template = env.from_string("""\
{% if not user %}
  please log in
{% else %}
  hello user
{% endif %}
""")

data = {
  "user": {
    "eligible": False,
    "score": 5
  }
}

print(template.render(**data))
```

```plain title="output"
hello user
```

The `not` prefix operator uses Liquid truthiness. Only `false` and `nil` are not truthy. Empty strings, arrays and objects all evaluate to `true`.

### Parentheses

`and` and `or` operators in Liquid are right associative. Where `true and false and false or true` is equivalent to `(true and (false and (false or true)))`, evaluating to `false`. Python, on the other hand, would parse the same expression as `(((true and false) and false) or true)`, evaluating to `true`.

This implementation of `if` maintains that right associativity so that any standard `if` expression will behave the same, with or without non-standard `if`. Only when `not` or parentheses are used will behavior deviate from the standard.

```json title="data"
{
  "user": {
    "eligible": false,
    "score": 5
  },
  "exempt": true
}
```

```liquid title="template with parentheses"
{% if (user != empty and user.eligible and user.score > 100) or exempt %}
    user is special
{% else %}
    denied
{% endif %}
```

```plain title="output"
user is special
```

```liquid title="template without parentheses"
{% if user != empty and user.eligible and user.score > 100 or exempt %}
    user is special
{% else %}
    denied
{% endif %}
```

```plain title="output"
denied
```

## inline if / else

**_New in version 1.5.0_**

Drop-in replacements for the standard output statement, [`assign`](../language/tags.md#assign) tag, and [`echo`](../language/tags.md#echo) tag that support inline `if`/`else` expressions. You can find a BNF-like description of the inline conditional expression in [this gist](https://gist.github.com/jg-rp/e2dc4da9e5033e087e46016008a9d91c#file-inline_if_expression-bnf).

Inline `if`/`else` expressions are designed to be backwards compatible with standard filtered expressions. As long as there are no template variables called `if` or `else` within a filtered expression, standard output statements, `assign` tags and `echo` tags will behave the same.

```python
from liquid import Environment
from liquid.extra import add_inline_expression_tags

env = Environment()
add_inline_expression_tags(env)

template = env.from_string("{{ 'hello user' if user.logged_in else 'please log in' }}")

data = {
  "user": {
    "logged_in": False
  }
}

print(template.render(**data))
```

```plain title="output"
please log in
```

The `else` part of an inline expression is optional, defaulting to [undefined](../introduction/strictness.md#undefined-variables).

```liquid title="template"
{{ 'hello user' if user.logged_in }}!
```

```plain title="output"
!
```

Inline conditional expressions are evaluated lazily. If the condition is falsy, the leading object is not evaluated. Equally, if the condition is truthy, any expression following `else` will not be evaluated.

### With Filters

:::caution
The inline conditional expressions added to Python Liquid 1.5.0 differs slightly from those found in Python Liquid Extra. Previously, trailing filters would be applied regardless of which branch of the condition was taken. Now, "tail filters" are distinguished from alternative branch filters with a double pipe token (`||`). See examples below.
:::

Filters can appear before an inline `if` expression.

```liquid title="template"
{{ 'hello user' | capitalize if user.logged_in else 'please log in' }}
```

Or after an inline `if` expression. In which case filters will only be applied to the `else` clause.

```liquid title="template"
{% assign param = 'hello user' if user.logged_in else 'please log in' | url_encode %}
```

Or both.

```liquid title="template"
{{% assign param = 'hello user' | capitalize if user.logged_in else 'please log in' | url_encode %}
```

Use a double pipe (`||`) to start any filters you want to apply regardless of which branch is taken. Subsequent "tail filters" should be separated by a single pipe (`|`).

```liquid title="template"
{{% assign name =
  user.nickname | downcase
  if user.has_nickname
  else user.last_name | capitalize
  || prepend: user.title | strip
%}
```

## macro / call

**_New in version 1.5.0_**

```plain
{% macro <string> [[,] [ <object>, ... ] [ <identifier>: <object>, ... ]] %}
```

```plain
{% call <string> [[,] [ <object>, ... ] [ <identifier>: <object>, ... ]] %}
```

Define parameterized Liquid snippets using the `macro` tag, and call them using the `call` tag.

Using the `macro` tag is like defining a function. Its parameter list defines arguments, possibly with default values. A `macro` tag's block has its own scope including its arguments and template global variables, just like the `render` tag.

Note that argument defaults are bound late. They are evaluated when a `call` expression is evaluated, not when the macro is defined.

```python
from liquid import Environment
from liquid import StrictUndefined
from liquid.extra import add_macro_tags

env = Environment(undefined=StrictUndefined)
add_macro_tags(env)

template = env.from_string("""\
{% macro 'price' product, on_sale: false %}
  <div class="price-wrapper">
  {% if on_sale %}
    <p>Was {{ product.regular_price | prepend: '$' }}</p>
    <p>Now {{ product.price | prepend: '$' }}</p>
  {% else %}
    <p>{{ product.price | prepend: '$' }}</p>
  {% endif %}
  </div>
{% endmacro %}

{% call 'price' products[0], on_sale: true %}
{% call 'price' products[1] %}
""")

data = {
  "products": [
    {
      "title": "Some Shoes",
      "regular_price": "5.99",
      "price": "4.99"
    },
    {
      "title": "A Hat",
      "regular_price": "16.00",
      "price": "12.00"
    }
  ]
}

print(template.render(**data))
```

```html title="output"
<div class="price-wrapper">
  <p>Was $5.99</p>
  <p>Now $4.99</p>
</div>

<div class="price-wrapper">
  <p>$12.00</p>
</div>
```

### Excess Arguments

Excess arguments passed to `call` are collected into `args` and `kwargs`.

```liquid title="template"
{% macro 'foo' %}
  {% for arg in args %}
    - {{ arg }}
  {% endfor %}

  {% for arg in kwargs %}
    - {{ arg.0 }} => {{ arg.1 }}
  {% endfor %}
{% endmacro %}

{% call 'foo' 42, 43, 99, a: 3.14, b: 2.71828 %}
```

```plain title="output"
- 42
- 43
- 99

- a => 3.14
- b => 2.71828
```

## with

```plain
{% with <identifier>: <object> [, <identifier>: object ... ] %}
  <literal,statement,tag> ...
{% endwith %}
```

Extend the local namespace with block scoped variables.

Register `WithTag` with a [`liquid.Environment`](../api/environment.md) to make `with` available to templates rendered from that environment.

```python
from liquid import Environment
from liquid.extra.tags import WithTag

env = Environment()
env.add_tag(WithTag)
```

```json title="data"
{ "collection": { "products": [{ "title": "A Shoe" }] } }
```

```liquid title="template"
{% with p: collection.products.first %}
  {{ p.title }}
{% endwith %}
{{ p.title }}

{% with a: 1, b: 3.4 %}
  {{ a }} + {{ b }} = {{ a | plus: b }}
{% endwith %}
```

```plain title="output"
A Shoe

1 + 3.4 = 4.4
```
