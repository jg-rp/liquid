---
sidebar_position: 1
---

# Introduction to Liquid

Liquid is a template language, where source text (the template) contains placeholders for variables,
conditional expressions for including or excluding blocks of text, and loops for repeating blocks of
text. Any block can contain more variables, conditions and loops.

Output text is the result of _rendering_ a template given some data model. It is that data model
that provides the variables and objects referenced in a template's expressions.

Liquid is most commonly used with HTML, but can be used with any text-based content. Consider this
template.

```liquid
{% assign greeting = "Hello" %}
{% for person in people %}
{{ greeting }}, {{ person.name }}!
{% endfor %}
```

## Output

`{{ person.name }}` and `{{ greeting }}` are output statements. Expressions inside double curly
braces are evaluated and the result is inserted into the output text at that location. These
expressions can be simple variables, elements from Liquid arrays (Python lists or tuples) or objects
(Python dicts or classes) with properties.

## Tags

Tags allow us to include logic, like loops and conditions, in our Liquid templates. A tag can be
an _inline_ tag or a _block_ tag, and can add to rendered output text or not.

`{% for person in people %}` is the start of a block tag. Enclosed by `{%` and `%}` by default.
Where `for` is the name of the tag and `person in people` is the tag's expression. The `for` tag
behaves like a for-each loop, rendering its block once for each item in an iterable object. Every
block tag must have a matching _end tag_, which, by convention, follows the pattern
`{% end<tag name> %}`.

`{% assign greeting = "Hello" %}` is an inline tag. Inline tags don't have a block or an associated
end tag. See the [tag reference](tags) for details of all tags built-in to Liquid.

## Literals

`, ` and `!\n` are template literals. With the exception of [whitespace control](whitespace-control),
template literals are output unchanged.

## Filters

Variables can be modified prior to output or assignment using _filters_. Filters are applied to a
variable using the pipe symbol (`|`), followed by the filter's name and, possibly, some filter
arguments. Filter arguments appear after a colon (`:`) and are separated by commas (`,`).

Multiple filters can be chained, effectively piping the output of one filter into the input of
another. Here we use the [sort](../language/filters#sort) and [first](../language/filters#first)
filters to get the cheapest item in a collection of products.

```liquid
{% assign cheapest = collection.products | sort: "price" | first %}
```

See the [filter reference](filters) for details of all filters built-in to Liquid.

## Types

:::info
Being a Ruby project, the reference implementation of Liquid borrows terms and types found in Ruby.
Like "array" and "hash". Python equivalents would be "list" and "dictionary", or anything that
implements the [Sequence](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)
or [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)
interfaces, respectively.
:::

Liquid supports literal strings (`"hello"` or `'hello'`), integers (`1`, `-35`), floats (`0.42`,
`-99`) and booleans (`true` and `false`).

There is no literal syntax for creating arrays or hashes, although these types (or their Python
equivalents) can be added to a template's render context, and many tags and filters are designed to
work with them.

A _range_ literal is a start and stop integer, separated by two periods (`..`), and enclosed in parentheses. The resulting range is inclusive of its stop value. Ranges can be iterated and many of
the built-in filters that accept an array will also work with a range.

```liquid
{% assign foo = (1..5) %}
{{ foo | join: ',' }}

{% for i in (3..6) %}
    {{ i | plus: forloop.index }}
{% endfor %}
```

The reserved word `nil` is used to represent the absence of a value. In Python Liquid, `nil` is
equal to `None`.
