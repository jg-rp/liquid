---
sidebar_position: 2
---

# Liquid Tags

:::info
Some of the examples here are borrowed from [Shopify's Liquid documentation](https://shopify.github.io/liquid/).
You can find their license [here](https://github.com/Shopify/liquid/blob/master/LICENSE).
:::

This page documents the standard tags built-in to Liquid. See [custom tags](../guides/custom-tags)
for examples of how to write your own and the [liquid-extra](https://github.com/jg-rp/liquid-extra)
project for some non-standard tags.

## assign

`{% assign <identifier> = <primitive,identifier> [| <filter> [| <filter> ... ]] %}`

Set the value of a named variable for later use.

```liquid
{% assign some_variable = false %}
{%- if some_variable != true -%}
Lets go!
{%- endif -%}
```

```plain title="output"
Lets go!
```

## capture

`{% capture <identifier> %} <literal,statement,tag> ... {% endcapture %}`

Set the value of a named variable by rendering and capturing the tag's block. `capture` blocks can
contain any number of other tags and/or statements.

```liquid
{% assign favorite_food = "pizza" -%}
{% assign age = 35 -%}

{% capture about_me -%}
I am {{ age }} and my favorite food is {{ favorite_food }}.
{%- endcapture -%}

{{ about_me }}
```

```plain title="output"
I am 35 and my favourite food is pizza.
```

## case

```plain
{% case <identifier> %}
  [ {% when <primitive,identifier> %} <literal,statement,tag> ... ] ...
  [ {% else %} <literal,statement,tag> ... ]
{% endcase %}
```

Switch on a variable, executing a block of code when the `case` expression is equal to one or more
`when` expressions, or the optional `else` block if no `when` expressions match.

```liquid
{% assign handle = "cake" %}
{% case handle %}
  {% when "cake" %}
     This is a cake
  {% when "cookie", "biscuit" %}
     This is a cookie
  {% else %}
     This is not a cake nor a cookie
{% endcase %}
```

```plain title="output"
This is a cake
```

If multiple `when` expression match the `case` expression, multiple blocks will be evaluated (or
even the same block multiple time, in some cases).

```liquid
{% assign handle = "cake" %}
{% assign favorite = "cake" %}
{% case handle %}
  {% when "cake" %}
    This is a cake
  {% when "cookie", "biscuit" %}
    This is a cookie
  {% when favorite %}
    This is my favorite
  {% else %}
    This is not a cake nor a cookie
{% endcase %}
```

```plain title="output"
This is a cake
This is my favorite
```

## comment

`{% comment %} ... {% endcomment %}`

Mark a block of template text as a comment. Comment blocks are never evaluated or rendered.

```liquid
{% assign verb = "turned" %}
{% comment %}
{% assign verb = "converted" %}
{% endcomment %}
Anything you put between {% comment %} and {% endcomment %} tags
is {{ verb }} into a comment.
```

```plain title="output"


Anything you put between  tags
is turned into a comment.
```

## cycle

`{% cycle [ <string>: ] object [, object ... ] %}`

Yield the next in a sequence of objects each time `cycle` appears. When the sequence is exhausted, it will start again from the beginning.

:::info
Ruby Liquid's documentation says `cycle` must be used within a `for` loop. Running the [golden-liquid](https://github.com/jg-rp/golden-liquid) test suit against Ruby Liquid suggests this is not the case. `cycle` tags in Python Liquid do not require a `for` loop.
:::

:::caution
While Python Liquid will accept `cycle` arguments of any type, including identifiers to be resolved, this behavior is considered "unintended" or "undefined" in Ruby Liquid (see [issue #1519](https://github.com/Shopify/liquid/issues/1519)). If you need interoperability between Python Liquid and Ruby Liquid, only use strings or number as arguments to `cycle`.
:::

```liquid
{% cycle "one", "two", "three" %}
{% cycle "one", "two", "three" %}
{% cycle "one", "two", "three" %}
{% cycle "one", "two", "three" %}
```

```plain title="output"
one
two
three
one
```

If `cycle` arguments differ, a new iterator is created.

```liquid
{% cycle "one", "two", "three" %}
{% cycle "one", "two" %}
{% cycle 1, 2 %}
{% cycle "one", "two", "three" %}
{% cycle "one", "two", "three" %}
{% cycle "one", "two", "three" %}
```

```plain title="output"
one
one
1
two
three
one
```

You can give `cycle` a name to further distinguish multiple iterators with the same items.

```liquid
{% cycle "one", "two", "three" %}
{% cycle "foo": "one", "two", "three" %}
{% cycle "foo": "one", "two", "three" %}
{% cycle "one", "two", "three" %}
{% cycle "one", "two", "three" %}
{% cycle "one", "two", "three" %}
```

```plain title="output"
one
one
two
two
three
one
```

## decrement

`{% decrement <identifier> %}`

Output the next value in a named counter. Starting at `0`, each time `decrement` appears, the
counter is reduced by `1` before being output.

```liquid
{% decrement my_counter %}
{% decrement my_counter %}
{% decrement my_counter %}
```

```plain title="output"
-1
-2
-3
```

Named counters use a separate namespace from variables created with `assign` or `capture` tags.

```liquid
{% assign my_counter = 5 %}
{{ my_counter }}
{% decrement my_counter %}
{% decrement my_counter %}
{% decrement my_counter %}
{{ my_counter }}
```

```plain title="output"
5
-1
-2
-3
5
```

## echo

`{% echo <primitive,identifier> [| <filter> [| <filter> ... ]] %}`

A tag equivalent to the output statement (`{{ ... }}`). `echo` is intended to be used inside
[liquid](#liquid) tags, where output statements are not allowed.

```json title="data"
{
  "collection": {
    "products": [{ "title": "Hat" }, { "title": "Shirt" }, { "title": "Pants" }]
  }
}
```

```liquid title="template"
{% liquid
for product in collection.products
  echo product.title | capitalize
endfor
%}
```

```plain title="output"
Hat
Shirt
Pants
```

## for

```plain
{% for <identifier> in <identifier,range>
    [ limit: <integer> ] [ offset: <integer,'continue'> ] [ reversed ] %}
  <literal,statement,tag> ...
  [ {% else %} <literal,statement,tag> ... ]
{% endfor %}
```

Render a block once for each item in a sequence.

```json title="data"
{
  "collection": {
    "products": [{ "title": "Hat" }, { "title": "Shirt" }, { "title": "Pants" }]
  }
}
```

```liquid title="template"
{% for product in collection.products %}
    {{ product.title }}
{% endfor %}
```

```plain title="output"
Hat
Shirt
Pants
```

### break

Exit a loop early with the `{% break %}` tag.

```liquid title="template"
{% for product in collection.products %}
    {% if product.title == "Shirt" %}
        {% break %}
    {% endif %}
    {{ product.title }}
{% endfor %}
```

```plain title="output"
Hat
```

### continue

Skip all or part of a loop iteration with the `{% continue %}` tag.

```liquid title="template"
{% for product in collection.products %}
    {% if product.title == "Shirt" %}
        {% continue %}
    {% endif %}
    {{ product.title }}
{% endfor %}
```

```plain title="output"
Hat
Pants
```

### else

Render a default block if the sequence is empty or undefined.

```liquid title="template"
{% for product in empty_collection %}
    {{ product.title }}
{% else %}
    No products available
{% endfor %}
```

```plain title="output"
No products available
```

### forloop

A `forloop` object is available inside every `for` loop block.

| Property     | Description                                                          | Type    |
| ------------ | -------------------------------------------------------------------- | ------- |
| `name`       | The loop variable name and target identifier, separated by a hyphen. | string  |
| `length`     | The length of the sequence being iterated.                           | integer |
| `index`      | The 1-base index of the current iteration.                           | integer |
| `index0`     | The 0-base index of the current iteration.                           | integer |
| `rindex`     | The 1-base index of the current iteration counting from the end.     | integer |
| `rindex0`    | The 0-base index of the current iteration counting from the end.     | integer |
| `first`      | `true` if the current iteration is the first, `false` otherwise.     | bool    |
| `last`       | `true` is the current iteration is the last, `false` otherwise.      | bool    |
| `parentloop` | the `forloop` object of an enclosing `for` loop.                     | forloop |

```liquid title="template"
{% for product in collection.products %}
    {% if forloop.first %}
      <b>{{ product.title }}</b> - {{ forloop.index0 }}
    {% else %}
      {{ product.title }} - {{ forloop.index0 }}
    {% endif %}
{% endfor %}
```

```plain title="output"
<b>Hat</b> - 0
Shirt - 1
Pants - 2
```

### forloop.parentloop

Access a parent `forloop` object when `for` tags are nested.

```liquid title="template"
{% assign colors = "Red, Blue, Green" | split: ", " %}
{% for product in collection.products %}
  {% for color in colors %}
    {% if forloop.parentloop.first %}
      <b>{{ color }} {{ product.title }}</b>
    {% else %}
      {{ color }} {{ product.title }}
    {% endif %}

  {% endfor %}
{% endfor %}
```

```plain title="output"
<b>Red Hat</b>
<b>Blue Hat</b>
<b>Green Hat</b>
Red Shirt
Blue Shirt
Green Shirt
Red Pants
Blue Pants
Green Pants
```

### limit

If a limit is specified, the loop will stop after the given number of iterations.

```liquid title="template"
{% for product in collection.products limit: 2 %}
    {{ product.title }}
{% endfor %}
```

```plain title="output"
Hat
Shirt
```

### offset

If an offset is specified, the loop will start at the given index in the sequence.

```liquid title="template"
{% for product in collection.products offset: 1 %}
    {{ product.title }}
{% endfor %}
```

```plain title="output"
Shirt
Pants
```

### offset: continue

After using `limit`, you can start a new loop from where the previous one left off using
`offset: continue`.

```liquid title="template"
{% for product in collection.products limit: 2 %}
    {{ product.title }}
{% endfor %}

{% for product in collection.products offset: continue %}
    {{ product.title }}!
{% endfor %}
```

```plain title="output"
Hat
Shirt

Pants!
```

### reversed

If the `reversed` flag is given, the target sequence will be iterated in reverse order.

```liquid title="template"
{% for product in collection.products reversed %}
    {{ product.title }}
{% endfor %}
```

```plain title="output"
Pants
Shirt
Hat
```

### range

`(<number>..<number>)`

Ranges are also valid sequences in for loop expressions. A range expression yields a sequence of
integers inclusive of start and stop.

```liquid title="template"
{% for i in (1..4) %}
    {{ i }}
{% endfor %}
```

```plain title="output"
1
2
3
4
```

## if

```
{% if <expression> %}
  <literal,statement,tag> ...
  [ {% elsif <expression> %} <literal,statement,tag> ... [ {% elsif <expression> %} ... ]]
  [ {% else %} <literal,statement,tag> ... ]
{% endif %}
```

Render a block if the tag's expression evaluates to `true`.

```json title="data"
{
  "product": {
    "title": "Awesome Shoes"
  }
}
```

```liquid
{% if product.title == "Awesome Shoes" %}
  These shoes are awesome!
{% endif %}
```

```plain title="output"
These shoes are awesome!
```

Use the `else` tag to render a block if the `if` expression and any `elsif` expression all evaluate
to `false`.

```liquid
{% if product.title == "OK Hat" %}
  This hat is OK.
{% elsif product.title == "Rubbish Tie" %}
  This tie is rubbish.
{% else %}
  Not sure what this is.
{% endif %}
```

```plain title="output"
Not sure what this is.
```

### Expressions

`if` expressions are free to use the following comparison and logical operators.

#### Comparison Operators

| Operator | Name                     | Example                             |
| -------- | ------------------------ | ----------------------------------- |
| `==`     | Equal                    | `product.title == "Nice Shoes"`     |
| `!=`     | Not equal                | `user.name != "anonymous"`          |
| `>`      | Greater than             | `product.was_price > product.price` |
| `<`      | Less than                | `collection.products.size < 10`     |
| `>=`     | Greater than or equal to | `user.age >= 18`                    |
| `<=`     | Less than or equal to    | `basket.size <= 0`                  |

#### Logical Operators

`<left> <operator> <right>`

| Operator | Description                                                     |
| -------- | --------------------------------------------------------------- |
| `and`    | Returns true if both left and right statements evaluate to true |
| `or`     | Returns true if either statement evaluates to true              |

:::info
Standard Liquid does not have a logical `not` operator, nor does it support grouping terms with
parentheses. The [liquid-extra](https://github.com/jg-rp/liquid-extra) project maintains an `if` tag
that supports logical `not` and grouping with parentheses.
:::

In Liquid, `and` and `or` operators are right associative. Where `true and false and false or true`
is equivalent to `(true and (false and (false or true)))`, evaluating to `false`. Python, on the
other hand, would parse the same expression as `(((true and false) and false) or true)`, evaluating
to `true`.

#### Membership Operators

`<string,array> contains <string>`

| Operator   | Description                                                                                          |
| ---------- | ---------------------------------------------------------------------------------------------------- |
| `contains` | Returns true if the string on the right is a member or substring of the array or string on the left. |

### Truthy and Falsy

`false` and `nil` are falsy, everything else is truthy. Even empty string and arrays. Compare
strings and arrays to `empty` to check for emptiness.

```liquid
{% if somearray != empty %}
  Do something with the array.
{% endif %}
```

## ifchanged

`{% ifchanged %} <literal,statement,tag> ... {% endifchanged %}`

Render a block if, when rendered, it has not changed since the last occurrence of `ifchanged`.

:::caution
The `ifchanged` tag is an undocumented feature of Ruby Liquid. You can find the Ruby Liquid
implementation [here](https://github.com/Shopify/liquid/blob/master/lib/liquid/tags/ifchanged.rb).
:::

```liquid
{% assign greeting = "Hello" %}

{% ifchanged %}
  {{ greeting }}, World!
{% endifchanged %}

{% ifchanged %}
  {{ greeting }}, World!
{% endifchanged %}

{% assign greeting = "Goodbye" %}

{% ifchanged %}
  {{ greeting }}, World!
{% endifchanged %}
```

```plain title="output"
Hello, World!
Goodbye, World!
```

## include

```
{% include <string,identifier>
    [ ( with | for ) <identifier> [ as <identifier> ]]
    [[,] <identifier>: <object> [, [<identifier>: <object> ... ]]]
%}
```

Render the content of a named template. The name can be a string literal or a variable containing a
string. The included template will share the namespace of the current template.

:::caution
Shopify have depreciated the `include` tag in favour of the `render` tag. If `include` is ever
dropped from "standard" Liquid, we'll maintain an implementation in the
[liquid-extra](https://github.com/jg-rp/liquid-extra) project.
:::

:::info
`include` is not allowed inside a template rendered with `render`. You should expect a
`DisabledTagError` from Python Liquid if you do so.
:::

```liquid title="partial_template"
{% comment %} I'm a partial template {% endcomment %}
{{ greeting }}, World!
```

```liquid title=template
{% assign greeting = "Hello" %}
{% include "partial_template" %}
```

```plain title="output"
Hello, World!
```

### for / as

Render a template once for each item in a sequence using `for` / `as` syntax.

```liquid title=template
{% assign greetings = "Hello, Goodbye" | split: ", " %}
{% include "partial_template" for greetings as greeting %}
```

```plain title="output"
Hello, World!
Goodbye, World!
```

### with / as

Add an object to the included template's scope. By default the object will have the same name as
the included template. Use `as` to change the objects name.

:::info
When using `with` / `as`, there's no functional difference to using keyword arguments.
:::

```liquid title="greeting"
{% comment %} I'm a partial template {% endcomment %}
{{ greeting }}, World!
```

```liquid title=template
{% assign greetings = "Hello, Goodbye" | split: ", " %}
{% include "greeting" with greetings[1] %}
```

```plain title="output"
Goodbye, World!
```

### Keyword Arguments

Add one or more variables to the included template's scope.

```liquid title="partial_template"
{% comment %} I'm a partial template {% endcomment %}
{% for i in (1..num) %}
  {% if i == skip %}
    {% continue %}
  {% endif %}
  {{ greeting }}, World! {i}
{% endfor %}
```

```liquid title=template
{% include "partial_template" greeting: "Hello", num: 3, skip: 2 %}
```

```plain title="output"
Hello, World! 1
Hello, World! 3
```

## increment

`{% increment <identifier> %}`

Output the next value in a named counter. Starting at `0`, each time `increment` appears, the
counter is output, then incremented by `1`.

```liquid
{% increment my_counter %}
{% increment my_counter %}
{% increment my_counter %}
```

```plain title="output"
0
1
2
```

Named counters use a separate namespace from variables created with `assign` or `capture` tags.

```liquid
{% assign my_counter = 5 %}
{{ my_counter }}
{% increment my_counter %}
{% increment my_counter %}
{% increment my_counter %}
{{ my_counter }}
```

```plain title="output"
5
0
1
2
5
```

## liquid

```
{% liquid
<tag name> <expression>
[ <tag name> <expression> ... ]
[ end<tag name> ]
...
%}
```

Combine multiple Liquid tags in a concise, shorthand syntax. Omitting the usual tag start and end
sequences (`{%` and `%}`), each line starts with a tag name and, separated by spaces or tabs,
finishes with the tag's expression.

Output statements (`{{ ... }}`) are not valid inside `liquid` tags. Use [echo](#echo) instead.

```liquid
{% liquid
assign username = "Brian"

if username
  echo "Hello, " | append: username
else
  echo "Hello, user"
endif

for i in (1..3)
  echo i
endfor
%}
```

```plain title="output"
Hello, Brian123
```

## raw

`{% raw %} <literal> {% endraw %}`

Render text containing literal `{{`, `}}`, `{%` and `%}` strings. Everything inside a `raw` block
will not be parsed as a Liquid template.

```liquid
{% raw %}
In Handlebars, {{ this }} will be HTML-escaped, but {{{ that }}} will not.
{% endraw %}
```

```plain title="output"

In Handlebars, {{ this }} will be HTML-escaped, but {{{ that }}} will not.

```

## render

`{% render <string> [ ( with | for ) <identifier> [ as <identifier> ]] [[,] <identifier>: <object> [, [<identifier>: <object> ... ]]] %}`

Render a named template. The template name must be a string literal. The template will be rendered
with its own namespace. That is, it wont have access to variables set with [assign](#assign) or
[capture](#capture) in the parent template.

:::info
`include` is not allowed inside a template rendered with `render`. You should expect a
`DisabledTagError` from Python Liquid if you do so.
:::

```json title="data"
{
  "product": {
    "title": "A Hat",
    "variants": [{ "title": "Red" }, { "title": "Blue" }]
  }
}
```

```liquid title="partial_template"
<h4>Some Heading</h4>
```

```liquid title="template"
<h3>{{ product.title }}</h3>
{% render "partial_template" %}
```

```plain title="output"
<h3>A Hat</h3>
<h4>Some Heading</h4>
```

### for / as

Render a template once for each item in a sequence using `for` / `as` syntax.

:::info
A [forloop](#forloop) object is available inside templates rendered with the `for` / `as` syntax.
`forloop.parentloop` will always be undefined.
:::

```liquid title="partial_template"
<li>{{ variant.title }}</li>
```

```liquid title="template"
<h3>{{ product.title }}</h3>
<ol>
  {% render "partial_template" for product.variants as variant %}
</ol>
```

```plain title="output"
<h3>A Hat</h3>
<ol>
  <li>Red</li>
  <li>Blue</li>
</ol>
```

### with / as

Add an object to the rendered template's namespace using `with` / `as` syntax.

```liquid title="partial_template"
<li>{{ variant.title }}</li>
```

```liquid title="template"
<h3>{{ product.title }}</h3>
<ol>
  {% render "partial_template" with product.variants[0] as variant %}
</ol>
```

```plain title="output"
<h3>A Hat</h3>
<ol>
  <li>Red</li>
</ol>
```

### Keyword Arguments

Add one or more variables to the rendered template's scope.

```liquid title="partial_template"
{% comment %} I'm a partial template {% endcomment %}
{% for i in (1..num) %}
  {% if i == skip %}
    {% continue %}
  {% endif %}
  {{ greeting }}, World! {i}
{% endfor %}
```

```liquid title=template
{% render "partial_template" greeting: "Hello", num: 3, skip: 2 %}
```

```plain title="output"
Hello, World! 1
Hello, World! 3
```

## tablerow

```plain
{% tablerow <identifier> in <identifier,range>
    [ cols: <integer> ] [ limit: <integer> ] [ offset: <integer> ] %}
  <identifier>
{% endtablerow %}
```

Render HTML table row (`<tr></tr>`) and table data (`<td></td>`) elements for each item in a
sequence.

```json title="data"
{
  "collection": {
    "products": [
      { "title": "Cool Shirt" },
      { "title": "Alien Poster" },
      { "title": "Batman Poster" },
      { "title": "Bullseye Shirt" },
      { "title": "Another Classic Vinyl" },
      { "title": "Awesome Jeans" }
    ]
  }
}
```

```liquid title="template"
<table>
{% tablerow product in collection.products %}
  {{ product.title }}
{% endtablerow %}
</table>
```

```html title="output"
<table>
  <tr class="row1">
    <td class="col1">Cool Shirt</td>
    <td class="col2">Alien Poster</td>
    <td class="col3">Batman Poster</td>
    <td class="col4">Bullseye Shirt</td>
    <td class="col5">Another Classic Vinyl</td>
    <td class="col6">Awesome Jeans</td>
  </tr>
</table>
```

### cols

By default, `tablerow` will output one row, and one column for each item in the sequence. Use the
`cols` parameter to set the number of columns.

```liquid title="template"
{% tablerow product in collection.products cols:2 %}
  {{ product.title }}
{% endtablerow %}
```

```html title="output"
<table>
  <tr class="row1">
    <td class="col1">Cool Shirt</td>
    <td class="col2">Alien Poster</td>
  </tr>
  <tr class="row2">
    <td class="col1">Batman Poster</td>
    <td class="col2">Bullseye Shirt</td>
  </tr>
  <tr class="row3">
    <td class="col1">Another Classic Vinyl</td>
    <td class="col2">Awesome Jeans</td>
  </tr>
</table>
```

### limit

If a limit is specified, the `tablerow` loop will stop after the given number of iterations.

```liquid title="template"
<table>
{% tablerow product in collection.products limit:2 %}
  {{ product.title }}
{% endtablerow %}
</table>
```

```html title="output"
<table>
  <tr class="row1">
    <td class="col1">Cool Shirt</td>
    <td class="col2">Alien Poster</td>
  </tr>
</table>
```

### offset

If an offset is specified, the `tablerow` loop will start at the given index in the sequence.

```liquid title="template"
<table>
{% tablerow product in collection.products offset:4 %}
  {{ product.title }}
{% endtablerow %}
</table>
```

```html title="output"
<table>
  <tr class="row1">
    <td class="col1">Another Classic Vinyl</td>
    <td class="col2">Awesome Jeans</td>
  </tr>
</table>
```

### tablerowloop

A `tablerowloop` object is available inside every `tablerow` block.

| Property    | Description                                                         | Type    |
| ----------- | ------------------------------------------------------------------- | ------- |
| `length`    | The length of the sequence being iterated                           | integer |
| `index`     | The 1-base index of the current iteration                           | integer |
| `index0`    | The 0-base index of the current iteration                           | integer |
| `rindex`    | The 1-base index of the current iteration counting from the end     | integer |
| `rindex0`   | The 0-base index of the current iteration counting from the end     | integer |
| `first`     | `true` if the current iteration is the first, `false` otherwise     | bool    |
| `last`      | `true` is the current iteration is the last, `false` otherwise      | bool    |
| `col`       | The 1-based column number                                           | integer |
| `col0`      | The 0-based column number                                           | integer |
| `col_first` | `true` if the current column is the first column, `false` otherwise | integer |
| `col_last`  | `true` if the current column is the last column, `false` otherwise  | integer |

```liquid title="template"
{% tablerow product in collection.products cols:2 %}
  {{ product.title }} - {{ tablerowloop.col0 }}
{% endtablerow %}
```

```html title="output"
<table>
  <tr class="row1">
    <td class="col1">Cool Shirt - 0</td>
    <td class="col2">Alien Poster - 1</td>
  </tr>
  <tr class="row2">
    <td class="col1">Batman Poster - 0</td>
    <td class="col2">Bullseye Shirt< - 1/td></td>
  </tr>
  <tr class="row3">
    <td class="col1">Another Classic Vinyl - 0</td>
    <td class="col2">Awesome Jeans - 1</td>
  </tr>
</table>
```

## unless

```
{% unless <expression> %}
  <literal,statement,tag> ...
  [ {% elsif <expression> %} <literal,statement,tag> ... [ {% elsif <expression> %} ... ]]
  [ {% else %} <literal,statement,tag> ... ]
{% endif %}
```

Render a block if the tag's expression evaluates to `false`. The opposite of [if](#if). See
[if expressions](#expressions) for details.

```json title="data"
{
  "product": {
    "title": "Rubbish Hat"
  }
}
```

```liquid title="template"
{% unless product.title == "Awesome Shoes" %}
  These shoes are not awesome.
{% endunless %}
```

```plain title="output"
These shoes are not awesome.
```

Use an `else` tag to define a block to render in case the `unless` expression evaluates to `true`.

```liquid title="template"
{% unless product.title == "Rubbish Hat" %}
  These shoes are not awesome.
{% else %}
  I need a new hat.
{% endunless %}
```

```plain title="output"
I need a new hat.
```

`unless` also supports any number of `elsif` tags. Unlike an `unless` expression, `elsif` blocks
are rendered if their expression evaluates to `true`.

```liquid title="template"
{% unless product.title == "Rubbish Hat" %}
  These shoes are not awesome.
{% elsif product.title == "Boring Tie" %}
  This tie is not awesome.
{% else %}
  I need a new hat.
{% endunless %}
```

```plain title="output"
I need a new hat.
```
