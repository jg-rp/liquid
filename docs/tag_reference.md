All the tags described here are enabled by default in Python Liquid.

## Comments

Comments can be used to add documentation to your templates or "comment out" chunks of Liquid markup and text so that it wont be rendered.

### Block comments

```liquid2
{% comment %} ... {% endcomment %}
```

Block comments start with the `comment` tag and end with the `endcomment` tag. It is OK for comment text to contain matching `comment`/`endcomment` or `raw`/`endraw` pairs, but is a syntax error if `comment` or `raw` tags are unbalanced.

```liquid2
{% comment %}This is a comment{% endcomment %}
{% comment %}
    Comments can
    span
    multiple lines
{% endcomment %}
```

### Inline comments

```
{% # ... %}
```

An inline comment is a tag called `#`. Everything after the hash up to the end tag delimiter (`%}`) is comment text. Text can span multiple lines, but each line must start with a `#`.

```liquid2
{% # This is a comment %}
{%-
  # Comments can span multiple lines,
  # but every line must start with a hash.
-%}
```

Inside [liquid tags](#liquid), any line starting with a hash will be considered a comment.

```liquid2
{% liquid
  # This is a comment
  echo "Hello"
%}
```

## Output

```
{{ <expression> }}
```

An expression surrounded by double curly braces, `{{` and `}}`, is an _output statement_. When rendered, the expression will be evaluated and the result inserted into the output text.

In this example the expression is a variable, which will be resolved to a value and the value's string representation will output, but output statements can contain any primitive expression.

```liquid2
Hello, {{ you }}!
```

### Primitive expressions

| Primitive expression | Examples                                                      |
| -------------------- | ------------------------------------------------------------- |
| Boolean literal      | `true` or `false`                                             |
| Null literal         | `null` or `nil`                                               |
| Integer literal      | `123`                                                         |
| Float literal        | `1.23`                                                        |
| String literal       | `"Hello"` or `'Hello'`                                        |
| Range                | `(1..5)` or `(x..y)`                                          |
| A path to a variable | `foo` or `foo.bar` or `foo.bar[0]` or `foo["some thing"].bar` |

### Filters

```
{{ <expression> | <filter> [| <filter> ...] }}
```

Values can be modified prior to output using filters. Filters are applied to an expression using the pipe symbol (`|`), followed by the filter's name and, possibly, some filter arguments. Filter arguments appear after a colon (`:`) and are separated by commas (`,`).

Multiple filters can be chained together, effectively piping the output of one filter into the input of another. See the [filter reference](filter_reference.md) for details of all built in filters.

```liquid2
{{ user_name | upcase }}
{{ 42 | plus: 7 | modulo: 3 }}
```

## assign

```
{% assign <identifier> = <expression> %}
```

The `assign` tag is used to define and initialize new variables or reassign existing variables.

```liquid2
{% assign foo = "bar" %}
foo is equal to {{ foo }}.

{% assign foo = 42 %}
foo is now equal to {{ foo }}.
```

The _expression_ on the right-hand side of the assignment operator (`=`) follows the syntax described in [Output](#output) above. It can be any [primitive expression](#primitive-expressions) and it can include [filters](#filters).

## capture

```
{% capture <identifier> %} <liquid markup> {% endcapture %}
```

The `capture` tag evaluates the contents of its block and saves the resulting string as a new variable, or reassigns an existing variable, without immediately rendering it.

```liquid2
{% capture welcome_message %}
  Hello, {{ customer.name }}! Welcome to our store.
{% endcapture %}

{{ welcome_message }}
```

In some cases, it can be easier to use a template string.

```liquid2
{% assign welcome_message = "Hello, ${ customer.name }! Welcome to our store." %}
```

## case

```
{% case <expression> %}
  [ {% when <expression> %} <liquid markup> ] ...
  [ {% else %} <liquid markup> ]
{% endcase %}
```

The `case` tag evaluates an expression, matching the result against one or more `when` clauses. In the event of a match, the `when` block is rendered. The `else` clause is rendered if no `when` clauses match the `case` expression.

```liquid2
{% assign day = "Monday" %}

{% case day %}
  {% when "Monday" %}
    Start of the work week!
  {% when "Friday" %}
    It's almost the weekend!
  {% when "Saturday" or "Sunday" %}
    Enjoy your weekend!
  {% else %}
    Just another weekday.
{% endcase %}
```

## cycle

```
{% cycle [ <string or identifier>: ] <expression> [, <expression> ... ] %}
```

Render the next item in an iterator, initializing it and rendering the first value if it does not yet exist. When the items are exhausted, the iterator starts again from the beginning.

```liquid2
{% cycle 'odd', 'even' %}
{% cycle 'odd', 'even' %}
{% cycle 'odd', 'even' %}
```

You can give `cycle` a name to further distinguish multiple iterators with the same items.

```liquid2
{% cycle 'odd', 'even' %}
{% cycle 'odd', 'even' %}
{% cycle inner: 'odd', 'even' %}
```

## decrement

```
{% decrement <identifier> %}
```

The `decrement` tag renders the next value in a named counter, reducing the count by one each time. If a counter with the given name does not already exist, it is created automatically and initialized to zero, before subtracting 1 and outputting `-1`.

```liquid2
{% decrement some %}
{% decrement thing %}
{% decrement thing %}
```

## echo

```
{% echo <expression> %}
```

The `echo` tag is equivalent to output statements, an expression surrounded by `{{` and `}}`, just in tag form. It is mostly used inside [`{% liquid %}`](#liquid) tags where plain output statements are not allowed.

```liquid2
Hello, {% echo you %}!
Hello, {{ you }}!

{% liquid
  for product in collection.products
    echo product.title | capitalize
  endfor
%}
```

Just like output statements and the [`assign`](#assign) tag, the expression can be any [primitive expression](#primitive-expressions) and it can include [filters](#filters).

```liquid2
{% echo "bar" | upcase if x else "baz" | capitalize %}

{% liquid
  for product in collection.products
    echo product.title | capitalize
  endfor
%}
```

## for

```
{% for <identifier> in <expression>
    [ limit: <expression> ] [ offset: <expression> ] [ reversed ] %}
  <liquid markup>
  [ {% else %} <liquid markup> ]
{% endfor %}
```

The `for` tag renders its block once for each item in an iterable object, like an array/list or mapping/dict/hash. If the iterable is empty and an `else` block given, it will be rendered instead.

```liquid2
{% for product in collection %}
    - {{ product.title }}
{% else %}
    No products available
{% endfor %}
```

Range expression are often used with the `for` tag to loop over increasing integers.

```liquid2
{% for i in (1..4) %}
    {{ i }}
{% endfor %}
```

### limit

If a `limit` argument is given, the loop will stop after the specified number of iterations.

```liquid2
{% for product in collection.products limit: 2 %}
    - {{ product.title }}
{% endfor %}
```

### offset

If an `offset` argument is given, it should be an integer specifying how many items to skip before starting the loop.

```liquid2
{% for product in collection.products limit: 2 %}
    - {{ product.title }}
{% endfor %}
```

`offset` can also be given the special value `"continue"`, in which case the loop will start from where a previous loop with the same iterable left off.

```liquid2
{% for product in collection.products limit: 2 %}
    - {{ product.title }}
{% endfor %}

{% for product in collection.products offset: continue %}
    - {{ product.title }}!
{% endfor %}
```

### reversed

If the reversed flag is given, the target iterable will be iterated in reverse order.

```liquid2
{% for product in collection.products reversed %}
    - {{ product.title }}
{% endfor %}
```

### break

You can exit a loop early using the `break` tag.

```liquid2
{% for product in collection.products %}
    {% if product.title == "Shirt" %}
        {% break %}
    {% endif %}
    - {{ product.title }}
{% endfor %}
```

### continue

You can skip all or part of a loop iteration with the `continue` tag.

```liquid2
{% for product in collection.products %}
    {% if product.title == "Shirt" %}
        {% continue %}
    {% endif %}
    - {{ product.title }}
{% endfor %}
```

### forloop

A `forloop` object is available inside every `for` tag block.

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

```liquid2
{% for product in collection.products %}
    {% if forloop.first %}
      <b>{{ product.title }}</b> - {{ forloop.index0 }}
    {% else %}
      {{ product.title }} - {{ forloop.index0 }}
    {% endif %}
{% endfor %}
```

## if

```
{% if <expression> %}
  <liquid markup>
  [ {% elsif <expression> %} <liquid markup> [ {% elsif <expression> %} ... ]]
  [ {% else %} <liquid markup> ... ]
{% endif %}
```

The `if` tag conditionally renders its block if its expression evaluates to be truthy. Any number of `elsif` blocks can be given to add alternative conditions, and an `else` block is used as a default if no preceding conditions were truthy.

```liquid2
{% if product.title == "OK Hat" %}
  This hat is OK.
{% elsif product.title == "Rubbish Tie" %}
  This tie is rubbish.
{% else %}
  Not sure what this is.
{% endif %}
```

### Conditional expressions

Any primitive expression can be tested for truthiness, like `{% if some_variable %}`, or you can use a combination of the following operators. Only `false`, `nil`/`null` and the special _undefined_ object are falsy in Liquid.

| Operator | Description              | Example                             |
| -------- | ------------------------ | ----------------------------------- |
| `==`     | Equals                   | `product.title == "Nice Shoes"`     |
| `!=`     | Not equals               | `user.name != "anonymous"`          |
| `>`      | Greater than             | `product.was_price > product.price` |
| `<`      | Less than                | `collection.products.size < 10`     |
| `>=`     | Greater than or equal to | `user.age >= 18`                    |
| `<=`     | Less than or equal to    | `basket.size <= 0`                  |
| `and`    | Logical and              | `x and y`                           |
| `or`     | Logical or               | `x or y`                            |

### Operator precedence

In Liquid, `and` and `or` operators are right associative. Where `true and false and false or true` is equivalent to `(true and (false and (false or true)))`, evaluating to `false`. Python, on the other hand, would parse the same expression as `(((true and false) and false) or true)`, evaluating to `true`.

## include

```liquid2
{% include <template name>
    [ ( with | for ) <expression> [ as <identifier> ]]
    [[,] <identifier>: <expression> [, [<identifier>: <expression> ... ]]]
%}
```

The `include` tag loads and renders a named template, inserting the resulting text in its place. The name of the template to include can be a string literal or a variable resolving to a string. When rendered, the included template will share the same scope as the current template.

```liquid2
{% include "snippets/header.html" %}
```

### with

Using the optional `with` syntax, we can bind a value to a variable that will be in scope for the included template. By default, that variable will be the name of the included template. Alternatively we can specify the variable to use with the `as` keyword followed by an identifier.

Here, the template named `greeting` will have access to a variable called `greeting` with the value `"Hello"`.

```liquid2
{% assign greetings = "Hello,Goodbye" | split: "," %}
{% include "greeting" with greetings.first %}
```

### for

If an array-like object it given following the `for` keyword, the named template will be rendered once for each item in the sequence and, like `with` above, the item value will be bound to a variable named after the included template.

In this example the template named `greeting` will be rendered once with the variable `greeting` set to `"Hello"` and once with the variable `greeting` set to `"Goodbye"`.

```liquid2
{% assign greetings = "Hello, Goodbye" | split: ", " %}
{% include "greeting" for greetings as greeting %}
```

### Keyword arguments

Additional keyword arguments given to the `include` tag will be added to the included template's scope, then go out of scope after the included template has been rendered.

```liquid2
{% include "partial_template" greeting: "Hello", num: 3, skip: 2 %}
```

## increment

```
{% increment <identifier> %}
```

The `increment` tag renders the next value in a named counter, increasing the count by one each time. If a counter with the given name does not already exist, it is created automatically and initialized to zero, which is output **before** adding `1`.

```liquid2
{% increment some %}
{% increment thing %}
{% increment thing %}
```

## liquid

```
{% liquid
  <tag name> [<expression>]
  [ <tag name> [<expression>]]
  ...
%}
```

The `liquid` tag encloses _line statements_, where each line starts with a tag name and is followed by the tag's expression. Expressions inside `liquid` tags **must** fit on one line as we use `\n` as a delimiter indicating the end of the expression.

Note that output statement syntax (`{{ <expression> }}`) is not allowed inside `liquid` tags, so you must use the [`echo`](#echo) tag instead.

```liquid2
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

Also, inside `liquid` tags, any line starting with a hash will be considered a comment.

```liquid2
{% liquid
  # This is a comment
  echo "Hello"
%}
```

## raw

```
{% raw %} <text> {% endraw %}
```

Any text between `{% raw %}` and `{% endraw %}` will not be interpreted as Liquid markup, but output as plain text instead.

```liquid2
{% raw %}
  This will be rendered {{verbatim}}, with the curly brackets.
{% endraw %}
```

## render

```liquid2
{% render <string>
    [ ( with | for ) <expression> [ as <identifier> ]]
    [[,] <identifier>: <expression> [, [<identifier>: <expression> ... ]]]
%}
```

The `render` tag loads and renders a named template, inserting the resulting text in its place. The name of the template to include **must** be a string literal. When rendered, the included template will have its onw scope, without variables define in the calling template.

```liquid2
{% render "snippets/header.html" %}
```

### with

Using the optional `with` syntax, we can bind a value to a variable that will be in scope for the rendered template. By default, that variable will be the name of the rendered template. Alternatively we can specify the variable to use with the `as` keyword followed by an identifier.

Here, the template named `greeting` will have access to a variable called `greeting` with the value `"Hello"`.

```liquid2
{% assign greetings = "Hello,Goodbye" | split: "," %}
{% render "greeting" with greetings.first %}
```

### for

If an array-like object it given following the `for` keyword, the named template will be rendered once for each item in the sequence and, like `with` above, the item value will be bound to a variable named after the rendered template.

In this example the template named `greeting` will be rendered once with the variable `greeting` set to `"Hello"` and once with the variable `greeting` set to `"Goodbye"`.

```liquid2
{% assign greetings = "Hello, Goodbye" | split: ", " %}
{% render "greeting" for greetings as greeting %}
```

### Keyword arguments

Additional keyword arguments given to the `render` tag will be added to the rendered template's scope, then go out of scope after the it has been rendered.

```liquid2
{% render "partial_template" greeting: "Hello", num: 3, skip: 2 %}
```

## snippet

**_New in version 2.2.0_**

```plain
{% snippet <identifier> %}
  <liquid markup>
{% endsnippet %}
```

A snippet is a reusable block of Liquid markup. Traditionally we'd save a snippet to a file and include it in a template with the `{% render %}` tag.

```liquid
{% render  "some_snippet" %}
```

With the `{% snippet %}` tag we can define blocks for reuse inside a single template, potentially reducing the number of snippet files we need.

```liquid
{% snippet div %}
  <div>
    {{ content }}
  </div>
{% endsnippet %}
```

Defining a snippet does not render it. We use `{% render snippet_name %}` to render a snippet, where `snippet_name` is the name of your snippet without quotes (file-based snippet names must be quoted).

```liquid
{% snippet div %}
  <div>
    {{ content }}
  </div>
{% endsnippet %}

{% render div, content: "Some content" %}
{% render div, content: "Other content" %}
```

```html title="output"
<div>Some content</div>

<div>Other content</div>
```

Inline snippets share the same namespace as variables defined with `{% assign %}` and `{% capture %}`, so be wary of accidentally overwriting snippets with non-snippet data.

```liquid
{% snippet foo %}Hello{% endsnippet %}
{% foo = 42 %}
{% render foo %} {% # error %}
```

Snippets can be nested and follow the same scoping rules as file-based snippets.

```liquid
{% snippet a %}
  b
  {% snippet c %}
    d
  {% endsnippet %}
  {% render c %}
{% endsnippet %}

{% render a %}
{% render c %} {% # error, c is out of scope %}
```

Snippet blocks are bound to their names late. You can conditionally define multiple snippets with the same name and pick one at render time.

```liquid
{% if x %}
  {% snippet a %}b{% endsnippet %}
{% else %}
  {% snippet a %}c{% endsnippet %}
{% endif %}
{% render a %}
```

## tablerow

```plain
{% tablerow <identifier> in <expression>
    [ cols: <expression> ] [ limit: <expression> ] [ offset: <expression> ] %}
  <liquid markup>
{% endtablerow %}
```

The `tablerow` tag renders HTML `<tr>` and `<td>` elements for each item in an iterable. Text inside `<td>` elements will be the result of rendering the tag's block.

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

```liquid2 title="template"
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

By default, `tablerow` will output one row with one column for each item in the sequence. Use the `cols` parameter to set the number of columns.

```liquid2 title="template"
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

If `limit` is specified, the `tablerow` loop will stop after the given number of iterations.

```liquid2 title="template"
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

If `offset` is specified, the `tablerow` loop will start at the given index in the sequence.

```liquid2 title="template"
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
| `row`       | The current row number of the table                                 | integer |

```liquid2 title="template"
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
  <liquid markup>
  [ {% elsif <expression> %} <liquid markup> [ {% elsif <expression> %} ... ]]
  [ {% else %} <liquid markup> ... ]
{% endif %}
```

The `unless` tag conditionally renders its block if its expression evaluates to be falsy. Any number of elsif blocks can be given to add alternative conditions, and an else block is used as a default if none of preceding conditions were met.

```liquid2
{% unless product.title == "OK Hat" %}
  This hat is OK.
{% elsif product.title == "Rubbish Tie" %}
  This tie is rubbish.
{% else %}
  Not sure what this is.
{% endif %}
```

Otherwise `unless` behaves the same as [`if`](#if). See [Conditional expressions](#conditional-expressions).
