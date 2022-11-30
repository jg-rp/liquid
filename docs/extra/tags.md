# Extra Tags

**_New in version 1.5.0_**

This page documents extra tags that are not included in standard Liquid. See the [tag reference](../language/tags.md) for a details of all standard tags. Each tag described here must be registered with a [`liquid.Environment`](../api/environment.md) to make it available to templates rendered from that environment.

## if (not)

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
    "logged_in": false
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
