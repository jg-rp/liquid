# Extra Tags

This page documents extra tags that are not included in standard Liquid. See the [tag reference](../language/tags.md) for a details of all standard tags.

:::caution
These tags are not part of "standard" Liquid. If you choose to use them in your templates, those templates are unlikely to render correctly with other implementations of Liquid.
:::

## if (not)

```
{% if <expression> %}
  <literal,statement,tag> ...
  [ {% elsif <expression> %} <literal,statement,tag> ... [ {% elsif <expression> %} ... ]]
  [ {% else %} <literal,statement,tag> ... ]
{% endif %}
```

A drop-in replacement for the standard [`if`](../language/tags.md#if) tag that supports logical `not` and grouping with parentheses. See [the tag reference](../language/tags.md#expressions) for a description of standard if expressions.

Register `IfNotTag` with a [`liquid.Environment`](../api/environment.md) to make it available to templates rendered from that environment.

```python
from liquid import Environment
from liquid.extra.tags import IfNotTag

env = Environment()
env.add_tag(IfNotTag)
```

### not

A logical `not` operator. Reverse the truthiness of an object.

```json title="data"
{
  "user": {
    "eligible": false,
    "score": 5
  }
}
```

```liquid title="template"
{% if not user %}
    please log in
{% else %}
    hello user
{% endif %}
```

```plain title="output"
hello user
```

The `not` prefix operator uses Liquid _truthiness_. Only `false` and `nil` are not truthy. Empty strings, arrays and objects all evaluate to `true`. You can, however, use `not` in front of a comparison to `empty` or `blank`.

```liquid
{% if not something == empty %}
    ...
{% endif %}
```

### Parentheses

Control the order of evaluation with parentheses.

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

`and` and `or` operators in Liquid are right associative. Where `true and false and false or true` is equivalent to `(true and (false and (false or true)))`, evaluating to `false`. Python, on the other hand, would parse the same expression as `(((true and false) and false) or true)`, evaluating to `true`.

This implementation of `if` maintains that right associativity so that any standard `if` expression will behave the same, with or without non-standard `if`. Only when `not` or parentheses are used will behavior deviate from the standard.

## inline if / else

```
{{ <primitive,identifier> [| <filter> [| <filter> ... ]]
    [ if <expression> [ else <primitive,identifier> [| <filter> [| <filter> ... ]]]] }}
```

```
{% assign <identifier> = <primitive,identifier> [| <filter> [| <filter> ... ]]
    [ if <expression> [ else <primitive,identifier> [| <filter> [| <filter> ... ]]]] %}
```

```
{% echo <primitive,identifier> [| <filter> [| <filter> ... ]]
    [ if <expression> [ else <primitive,identifier> [| <filter> [| <filter> ... ]]]] %}
```

Drop-in replacements for the standard output statement and [`assign`](../language/tags.md#assign) and [`echo`](../language/tags.md#echo) tags that supports inline `if`/`else` expressions.

If the condition evaluates to `false` (Liquid truthiness), the leading object is not evaluated. Equally, if the condition evaluates to `true`, any `else` object is not evaluated. This is not terribly important if the objects are Liquid literals or simple Python objects, but could matter if the objects are custom drops that do time consuming IO or processing.

Register `InlineIfAssignTag`, `InlineIfEchoTag` and `InlineIfStatement` with a [`liquid.Environment`](../api/environment.md) to make them available to templates rendered from that environment.

```python
from liquid import Environment
from liquid.extra.tags import InlineIfAssignTag
from liquid.extra.tags import InlineIfEchoTag
from liquid.extra.tags import InlineIfStatement

env = Environment()
env.add_tag(InlineIfAssignTag)
env.add_tag(InlineIfEchoTag)
env.add_tag(InlineIfStatement)
```

```json title="data"
{
  "user": {
    "logged_in": false
  }
}
```

```liquid title="template"
{{ 'hello user' if user.logged_in else 'please log in' }}
```

```plain title="output"
please log in
```

The `else` part of an inline expression defaults to [undefined](../introduction/strictness.md#undefined-variables).

```liquid title="template"
{{ 'hello user' if user.logged_in }}!
```

```plain title="output"
!
```

### With Filters

Filters can appear before an inline `if` expression.

```liquid title="template"
{{ 'hello user' | capitalize if user.logged_in else 'please log in' }}
```

```plain title="output"
please log in
```

Or after an inline `if` expression. In which case filters will be applied even if the else clause is triggered.

```liquid title="template"
{% assign param = 'hello user' if user.logged_in else 'please log in' | url_encode %}
```

Or both.

```liquid title="template"
{{% assign param = 'hello user' | capitalize if user.logged_in else 'please log in' | url_encode %}
```

## macro / call

```plain
{% macro <string> [[,] [ <object>, ... ] [ <identifier>: <object>, ... ]] %}
```

```plain
{% call <string> [[,] [ <object>, ... ] [ <identifier>: <object>, ... ]] %}
```

Define parameterized Liquid snippets using the `macro` tag and call them using the `call` tag. Macros are intended to make code reuse easier, especially for small Liquid snippets that are only needed within one template.

`macro` is a bit like the standard [`capture`](../language/tags.md#capture) tag, where a block is stored on the render context for later use. Unlike `capture`, `macro` accepts parameters, possibly with default values, and the block is not evaluated until it is called using a `call` tag.

`call` is a bit like [`render`](../language/tags.md#render), in that a new context is created including any arguments supplied in the `call` expression. That context is then used to render the named macro. Unlike `render`, `call` can take positional arguments and does not hit any template loader or the template cache.

Similar to [`include`](../language/tags.md#include) and [`render`](../language/tags.md#render), `macro` and `call` take a string literal identifying the macro, followed by zero or more arguments. Neither `macro` or `call` accept `for` or `with`/`as` style expressions.

Note that argument defaults are bound late. Defaults are evaluated when a `call` expression is evaluated, not when the macro is defined.

Register `MacroTag` and `CallTag` with a [`liquid.Environment`](../api/environment.md) to make `macro` and `call` available to templates rendered from that environment.

```python
from liquid import Environment
from liquid import StrictUndefined

from liquid.extra.tags import MacroTag
from liquid.extra.tags import CallTag

# Setting strict undefined is strongly recommended.
env = Environment(undefined=StrictUndefined)
env.add_tag(MacroTag)
env.add_tag(CallTag)
```

```json title="data"
{
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
```

```liquid title="template"
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
