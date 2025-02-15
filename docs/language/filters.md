# Liquid Filters

This page documents standard filters that are available with every [`Environment`](../api/environment.md) by default. See [custom filters](../guides/custom-filters.md) for examples of how to write your own and the [extra filter reference](../extra/filters.md) for some non-standard filters.

:::info
Some of the examples here are borrowed from [Shopify's Liquid documentation](https://shopify.github.io/liquid/).
You can find their license [here](https://github.com/Shopify/liquid/blob/master/LICENSE).
:::

## abs

`<number> | abs`

Return the absolute value of a number. Works on integers, floats and string representations of integers or floats.

```liquid
{{ -42 | abs }}
{{ 7.5 | abs }}
{{ '42.0' | abs }}
```

```plain title="output"
42
7.5
42.0
```

Given a value that can't be cast to an integer or float, `0` will be returned.

```liquid
{{ 'hello' | abs }}
{{ nosuchthing | abs }}
```

```plain title="output"
0
0
```

## append

`<string> | append: <string>`

Return the input value concatenated with the argument value.

```liquid
{{ 'Hello, ' | append: 'World!' }}
```

```plain title="output"
Hello, World!
```

If either the input value or argument are not a string, they will be coerced to a string before concatenation.

```liquid
{% assign a_number = 7.5 -%}
{{ 42 | append: a_number }}
{{ nosuchthing | append: 'World!' }}
```

```plain title="output"
427.5
World!
```

## at_least

`<number> | at_least: <number>`

Return the maximum of the filter's input value and its argument. If either input value or argument are string representations of an integer or float, they will be cast to an integer or float prior to comparison.

```liquid
{{ -5.1 | at_least: 8 }}
{{ 8 | at_least: '5' }}
```

```plain title="output"
8
8
```

If either input value or argument can not be cast to an integer or float, `0` will be used instead.

```liquid
{{ "hello" | at_least: 2 }}
{{ "hello" | at_least: -2 }}
{{ -1 | at_least: "abc" }}
```

```plain title="output"
2
0
0
```

## at_most

`<number> | at_most: <number>`

Return the minimum of the filter's input value and its argument. If either input value or argument are string representations of an integer or float, they will be cast to an integer or float prior to comparison.

```liquid
{{ 5 | at_most: 8 }}
{{ '8' | at_most: 5 }}
```

```plain title="output"
5
5
```

If either input value or argument can not be cast to an integer or float, `0` will be used instead.

```liquid
{{ "hello" | at_most: 2 }}
{{ "hello" | at_most: -2 }}
{{ -1 | at_most: "abc" }}
```

```plain title="output"
0
-2
-1
```

## base64_decode

`<string> | base64_decode`

Decode a base64 encoded string. The decoded value is assumed to be UTF-8 and will be decoded as UTF-8.

:::caution
While Python Liquid assumes UTF-8 character encoding, Ruby Liquid does not seem to do so,
potentially introducing byte strings into the render context.
:::

```liquid
{{ 'SGVsbG8sIFdvcmxkIQ==' | base64_decode }}
```

```plain title="output"
Hello, World!
```

If the input value is not a valid base64 encoded string, an exception will be raised.

```liquid
{{ 'notbase64' | base64_decode }}
```

```plain title="output"
FilterError: invalid base64-encoded string, on line 1
```

## base64_encode

`<string> | base64_encode`

Encode a string using base64.

:::info
Python Liquid returns a `str` from `base64_encode`, not `bytes`.
:::

```liquid
{{ 'Hello, World!' | base64_encode }}
```

```plain title="output"
SGVsbG8sIFdvcmxkIQ==
```

If the input value is not a string, it will be converted to a string before base64 encoding.

```liquid
{{ 5 | base64_encode }}
```

```plain title="output"
NQ==
```

## base64_url_safe_decode

`<string> | base64_url_safe_decode`

Decode a URL safe base64 encoded string. Substitutes `-` instead of `+` and `_` instead of `/` in
the standard base64 alphabet. The decoded value is assumed to be UTF-8 and will be decoded as UTF-8.

:::caution
While Python Liquid assumes UTF-8 character encoding, Ruby Liquid does not seem to do so,
potentially introducing byte strings into the render context.
:::

```liquid
{{ 'SGVsbG8sIFdvcmxkIQ==' | base64_url_safe_decode }}
```

```plain title="output"
Hello, World!
```

If the input value is not a valid base64 encoded string, an exception will be raised.

```liquid
{{ 'notbase64' | base64_url_safe_decode }}
```

```plain title="output"
FilterError: invalid base64-encoded string, on line 1
```

## base64_url_safe_encode

`<string> | base64_url_safe_encode`

Encode a string using URL safe base64. Substitutes `-` instead of `+` and `_` instead of `/` in
the standard base64 alphabet.

:::info
Python Liquid returns a `str` from `base64_url_safe_encode`, not `bytes`.
:::

```liquid
{{ 'Hello, World!' | base64_url_safe_encode }}
```

```plain title="output"
SGVsbG8sIFdvcmxkIQ==
```

If the input value is not a string, it will be converted to a string before base64 encoding.

```liquid
{{ 5 | base64_url_safe_encode }}
```

```plain title="output"
NQ==
```

## capitalize

`<string> | capitalize`

Return the input string with the first character in upper case and the rest lowercase.

```liquid
{{ 'heLLO, World!' | capitalize }}
```

```plain title="output"
Hello, world!
```

If the input value is not a string, it will be converted to a string.

```liquid
{{ 42 | capitalize }}
```

```plain title="output"
42
```

## ceil

`<number> | ceil`

Round the input value up to the nearest whole number. The input value will be converted to a number if it is not an integer or float.

```liquid
{{ 5.1 | ceil }}
{{ 5.0 | ceil }}
{{ 5 | ceil }}
{{ '5.4' | ceil }}
```

```plain title="output"
6
5
5
5
```

If the input is undefined or can't be converted to a number, `0` is returned.

```liquid
{{ 'hello' | ceil }}
{{ nosuchthing | ceil }}
```

```plain title="output"
0
0
```

## compact

`<array> | compact[: <string>]`

Remove `nil` (or `None` in Python) values from an array-like object. If given, the argument should be the name of a property that exists on each object (hash, dict etc.) in the array-like sequence.

If `pages` is an array of objects, some of which have a `category` property:

```json title="data"
{
  "pages": [
    { "category": "business" },
    { "category": "celebrities" },
    {},
    { "category": "lifestyle" },
    { "category": "sports" },
    {},
    { "category": "technology" }
  ]
}
```

Without `compact`, iterating those categories will include `nil` values.

```liquid
{% assign categories = pages | map: "category" -%}

{% for category in categories -%}
- {{ category }}
{%- endfor %}
```

```plain title="output"
- business
- celebrities
-
- lifestyle
- sports
-
- technology
```

With `compact`, we can remove those missing categories before the loop.

```liquid
{% assign categories = pages | map: "category" | compact %}

{% for category in categories %}
- {{ category }}
{% endfor %}
```

```plain title="output"
- business
- celebrities
- lifestyle
- sports
- technology
```

Using the optional argument to `compact`, we could avoid using `map` and create an array of pages with a `category` property, rather than an array of categories.

```liquid
{% assign pages_with_category = pages | compact: "category" %}

{% for page in pages_with_category %}
- {{ page.category }}
{% endfor %}
```

```plain title="output"
- business
- celebrities
- lifestyle
- sports
- technology
```

## concat

`<array> | concat: <array>`

Create a new array by joining one array-like object with another.

```liquid
{% assign fruits = "apples, oranges, peaches" | split: ", " %}
{% assign vegetables = "carrots, turnips, potatoes" | split: ", " %}

{% assign everything = fruits | concat: vegetables %}

{% for item in everything %}
- {{ item }}
{% endfor %}
```

```plain title="output"
- apples
- oranges
- peaches
- carrots
- turnips
- potatoes
```

If the input value is not array-like, it will be converted to an array. No conversion is attempted for the argument value.

```liquid
{% assign fruits = "apples, oranges, peaches" | split: ", " %}
{% assign things = "hello" | concat: fruits %}

{% for item in things %}
- {{ item }}
{% endfor %}
```

```plain title="output"
- hello
- apples
- oranges
- peaches
```

If the input is a nested array, it will be flattened before concatenation. The argument is not flattened.

```json title="data"
{
  "a": [
    ["a", "x"],
    ["b", ["y", ["z"]]]
  ],
  "b": ["c", "d"]
}
```

```liquid
{{ a | concat: b | join: '#' }}
```

```plain title="output"
a#x#b#y#z#c#d
```

## date

`<datetime> | date: <string>`

Format a date and/or time according the the given format string. The input can be a string, in which case the string will be parsed as a date/time before formatting.

:::caution
Python Liquid uses [dateutil](https://dateutil.readthedocs.io/en/stable/) for parsing strings to
`datetimes`, and `strftime` for formatting. There are likely to be some inconsistencies between this
and Ruby Liquid's [Time.parse](https://ruby-doc.org/stdlib-3.0.3/libdoc/time/rdoc/Time.html#method-c-parse)
equivalent parsing and formatting of dates and times.

In general, Python Liquid will raise an exception if the input value can not be converted to a date
and/or time. Whereas Ruby Liquid will usually return something without erroring.
:::

```liquid
{{ "March 14, 2016" | date: "%b %d, %y" }}
```

```plain title="output"
Mar 14, 16
```

The special `'now'` or `'today'` input values can be used to get the current timestamp. `'today'` is an alias for `'now'`. Both include time information.

```liquid
{{ "now" | date: "%Y-%m-%d %H:%M" }}
```

```plain title="output"
2021-12-02 10:17
```

If the input is undefined, an empty string is returned.

```liquid
{{ nosuchthing | date: "%Y-%m-%d %H:%M" }}
```

```plain title="output"

```

## default

`<object> | default[: <object>[, allow_false:<bool>]]`

Return a default value if the input is undefined, `nil`, `false` or empty, or return the input unchanged otherwise.

:::info
The `default` filter is the only built-in filter to use a keyword argument.
:::

```liquid
{{ product_price | default: 2.99 }}

{%- assign product_price = "" %}
{{ product_price | default: 2.99 }}

{%- assign product_price = 4.99 %}
{{ product_price | default: 2.99 }}
```

```plain title="output"
2.99
2.99
4.99
```

If the optional `allow_false` argument is `true`, an input of `false` will not return the default. `allow_false` defaults to `false`.

```liquid
{% assign product_reduced = false -%}
{{ product_reduced | default: true, allow_false: true }}
```

```plain title="output"
false
```

If no argument is given, the default value will be an empty string.

```liquid
{{ product_price | default }}
```

```plain title="output"

```

Empty strings, arrays and objects all cause the default value to be returned. `0` does not.

```liquid
{{ "" | default: "hello" }}
{{ 0 | default: 99 }}
```

```plain title="output"
hello
0
```

## divided_by

`<number> | divided_by: <number>`

Divide a number by another number. The result is rounded down to the nearest integer if the divisor is an integer.

```liquid
{{ 16 | divided_by: 4 }}
{{ 5 | divided_by: 3 }}
```

```plain title="output"
4
1
```

If you divide by a float, the result will be a float.

```liquid
{{ 20 | divided_by: 7 }}
{{ 20 | divided_by: 7.0 }}
```

```plain title="output"
2
2.857142857142857
```

If either the input or argument are not an integer or float, Liquid will try to convert them to an integer or float. If the input can't be converted, `0` will be used instead. If the argument can't be converted, an exception is raised.

```liquid
{{ "20" | divided_by: "7" }}
{{ "hello" | divided_by: 2 }}
```

```plain title="output"
2
0
```

## downcase

`<string> | downcase`

Return the input string with all characters in lowercase.

```liquid
{{ 'Hello, World!' | downcase }}
```

```plain title="output"
hello, world!
```

If the input is not a string, Liquid will convert it to a string before forcing characters to lowercase.

```liquid
{{ 5 | downcase }}
```

```plain title="output"
5
```

If the input is undefined, an empty string is returned.

## escape

`<string> | escape`

Return the input string with characters `&`, `<` and `>` converted to HTML-safe sequences.

```liquid
{{ "Have you read 'James & the Giant Peach'?" | escape }}
```

```plain title="output"
Have you read &#39;James &amp; the Giant Peach&#39;?
```

## escape_once

`<string> | escape_once`

Return the input string with characters `&`, `<` and `>` converted to HTML-safe sequences, while
preserving existing HTML escape sequences.

```liquid
{{ "Have you read 'James &amp; the Giant Peach'?" | escape_once }}
```

```plain title="output"
Have you read &#39;James &amp; the Giant Peach&#39;?
```

## find

`<array> | find: <string>[, <object>]`

**_New in version 2.0.0_**

Return the first item in the input array that contains a property, given as the first argument, equal to the value given as the second argument. If no such item exists, `null` is returned.

In this example we select the first page in the "Programming" category.

```json title="data"
{
  "pages": [
    {
      "id": 1,
      "title": "Introduction to Cooking",
      "category": "Cooking",
      "tags": ["recipes", "beginner", "cooking techniques"]
    },
    {
      "id": 2,
      "title": "Top 10 Travel Destinations in Europe",
      "category": "Travel",
      "tags": ["Europe", "destinations", "travel tips"]
    },
    {
      "id": 3,
      "title": "Mastering JavaScript",
      "category": "Programming",
      "tags": ["JavaScript", "web development", "coding"]
    }
  ]
}
```

```liquid
{% assign page = pages | find: 'category', 'Programming' %}
{{ page.title }}
```

```plain title="output"
Mastering JavaScript
```

## find_index

`<array> | find_index: <string>[, <object>]`

**_New in version 2.0.0_**

Return the index of the first item in the input array that contains a property, given as the first argument, equal to the value given as the second argument. If no such item exists, `null` is returned.

In this example we find the index for the first page in the "Programming" category.

```json title="data"
{
  "pages": [
    {
      "id": 1,
      "title": "Introduction to Cooking",
      "category": "Cooking",
      "tags": ["recipes", "beginner", "cooking techniques"]
    },
    {
      "id": 2,
      "title": "Top 10 Travel Destinations in Europe",
      "category": "Travel",
      "tags": ["Europe", "destinations", "travel tips"]
    },
    {
      "id": 3,
      "title": "Mastering JavaScript",
      "category": "Programming",
      "tags": ["JavaScript", "web development", "coding"]
    }
  ]
}
```

```liquid
{% assign index = pages | find_index: 'category', 'Programming' %}
{{ pages[index].title }}
```

```plain title="output"
Mastering JavaScript
```

## first

`<sequence> | first`

Return the first item of the input sequence. The input could be array-like or a mapping, but not a
string.

```liquid
{{ "Ground control to Major Tom." | split: " " | first }}
```

```plain title="output"
Ground
```

If the input sequence is undefined, empty or not a sequence, `nil` is returned.

## floor

`<number> | floor`

Return the input down to the nearest whole number. Liquid tries to convert the input to a number
before the filter is applied.

```liquid
{{ 1.2 | floor }}
{{ 2.0 | floor }}
{{ 183.357 | floor }}
{{ -5.4 | floor }}
{{ "3.5" | floor }}
```

```plain title="output"
1
2
183
-6
3
```

If the input can't be converted to a number, `0` is returned.

## has

`<array> | has: <string>[, <object>]`

**_New in version 2.0.0_**

Return `true` if the input array contains an object with a property identified by the first argument that is equal to the object given as the second argument. `false` is returned if none of the items in the input array contain such a property/value.

In this example we test to see if any pages are in the "Programming" category.

```json title="data"
{
  "pages": [
    {
      "id": 1,
      "title": "Introduction to Cooking",
      "category": "Cooking",
      "tags": ["recipes", "beginner", "cooking techniques"]
    },
    {
      "id": 2,
      "title": "Top 10 Travel Destinations in Europe",
      "category": "Travel",
      "tags": ["Europe", "destinations", "travel tips"]
    },
    {
      "id": 3,
      "title": "Mastering JavaScript",
      "category": "Programming",
      "tags": ["JavaScript", "web development", "coding"]
    }
  ]
}
```

```liquid
{% assign has_programming_page = pages | has: 'category', 'Programming' %}
{{ has_programming_page }}
```

```plain title="output"
true
```

## join

`<array> | join[: <string>]`

Return the items in the input array as a single string, separated by the argument string. If the
input is not an array, Liquid will convert it to one. If input array items are not strings, they
will be converted to strings before joining.

```liquid
{% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}

{{ beatles | join: " and " }}
```

```plain title="output"
John and Paul and George and Ringo
```

If an argument string is not given, it defaults to a single space.

```liquid
{% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}

{{ beatles | join }}
```

```plain title="output"
John Paul George Ringo
```

## last

`<array> | last`

Return the last item in the array-like input.

```liquid
{{ "Ground control to Major Tom." | split: " " | last }}
```

```plain title="output"
Tom.
```

If the input is undefined, empty, string or a number, `nil` will be returned.

## lstrip

`<string> | lstrip`

Return the input string with all leading whitespace removed. If the input is not a string, it will
be converted to a string before stripping whitespace.

```liquid
{{ "          So much room for activities          " | lstrip }}!
```

```plain title="output"
So much room for activities          !
```

## map

`<array> | map: <string>`

Extract properties from an array of objects into a new array.

If `pages` is an array of objects with a `category` property:

```json title="data"
{
  "pages": [
    { "category": "business" },
    { "category": "celebrities" },
    { "category": "lifestyle" },
    { "category": "sports" },
    { "category": "technology" }
  ]
}
```

```liquid
{% assign categories = pages | map: "category" -%}

{% for category in categories -%}
- {{ category }}
{%- endfor %}
```

```plain title="output"
- business
- celebrities
- lifestyle
- sports
- technology
```

## minus

`<number> | minus: <number>`

Subtract one number from another. If either the input or argument are not a number, Liquid will try
to convert them to a number. If that conversion fails, `0` is used instead.

```liquid
{{ 4 | minus: 2 }}
{{ "16" | minus: 4 }}
{{ 183.357 | minus: 12.2 }}
{{ "hello" | minus: 10 }}
```

```plain title="output"
2
12
171.157
-10
```

## modulo

`<number> | modulo: <number>`

Return the remainder from the division of the input by the argument.

```liquid
{{ 3 | modulo: 2 }}
{{ "24" | modulo: "7" }}
{{ 183.357 | modulo: 12 }}
```

```plain title="output"
1
3
3.357
```

If either the input or argument are not an integer or float, Liquid will try to convert them to an
integer or float. If the input can't be converted, `0` will be used instead. If the argument can't
be converted, an exception is raised.

## newline_to_br

`<string> | newline_to_br`

Return the input string with `\n` and `\r\n` replaced with `<br />\n`.

```liquid
{% capture string_with_newlines %}
Hello
there
{% endcapture %}

{{ string_with_newlines | newline_to_br }}
```

```plain title="output"


<br />
Hello<br />
there<br />

```

## plus

`<number> | plus: <number>`

Add one number to another. If either the input or argument are not a number, Liquid will try to
convert them to a number. If that conversion fails, `0` is used instead.

```liquid
{{ 4 | plus: 2 }}
{{ "16" | plus: "4" }}
{{ 183.357 | plus: 12 }}
```

```plain title="output"
6
20
195.357
```

## prepend

`<string> | prepend: <string>`

Return the argument concatenated with the filter input.

```liquid
{{ "apples, oranges, and bananas" | prepend: "Some fruit: " }}
```

```plain title="output"
Some fruit: apples, oranges, and bananas
```

If either the input value or argument are not a string, they will be coerced to a string before
concatenation.

```liquid
{% assign a_number = 7.5 -%}
{{ 42 | prepend: a_number }}
{{ nosuchthing | prepend: 'World!' }}
```

```plain title="output"
7.542
World!
```

## reject

`<array> | reject: <string>[, <object>]`

**_New in version 2.0.0_**

Return a copy of the input array including only those objects that have a property, named with the first argument, **that is not equal to** a value, given as the second argument. If a second argument is not given, only elements with the named property that are falsy will be included.

```json title="data"
{
  "products": [
    { "title": "Vacuum", "type": "house", "available": true },
    { "title": "Spatula", "type": "kitchen", "available": false },
    { "title": "Television", "type": "lounge", "available": true },
    { "title": "Garlic press", "type": "kitchen", "available": true }
  ]
}
```

```liquid
All products:
{% for product in products -%}
- {{ product.title }}
{% endfor %}

{%- assign kitchen_products = products | reject: "type", "kitchen" -%}

Non kitchen products:
{% for product in kitchen_products -%}
- {{ product.title }}
{% endfor %}

{%- assign unavailable_products = products | reject: "available" -%}

Unavailable products:
{% for product in unavailable_products -%}
- {{ product.title }}
{% endfor %}
```

```plain title="output"
All products:
- Vacuum
- Spatula
- Television
- Garlic press
Non kitchen products:
- Vacuum
- Television
Unavailable products:
- Spatula
```

## remove

`<string> | remove: <string>`

Return the input with all occurrences of the argument string removed.

```liquid
{{ "I strained to see the train through the rain" | remove: "rain" }}
```

```plain title="output"
I sted to see the t through the
```

If either the filter input or argument are not a string, they will be coerced to a string before
substring removal.

## remove_first

`<string> | remove_first: <string>`

Return a copy of the input string with the first occurrence of the argument string removed.

```liquid
{{ "I strained to see the train through the rain" | remove_first: "rain" }}
```

```plain title="output"
I sted to see the train through the rain
```

If either the filter input or argument are not a string, they will be coerced to a string before substring removal.

## remove_last

`<string> | remove_last: <string>`

Return a copy of the input string with the last occurrence of the argument string removed.

```liquid
{{ "I strained to see the train through the rain" | remove_last: "rain" }}
```

```plain title="output"
I strained to see the train through the
```

If either the filter input or argument are not a string, they will be coerced to a string before substring removal.

## replace

`<string> | replace: <string>[, <string>]`

Return the input with all occurrences of the first argument replaced with the second argument. If
the second argument is omitted, it will default to an empty string, making `replace` behave like
`remove`.

```liquid
{{ "Take my protein pills and put my helmet on" | replace: "my", "your" }}
```

```plain title="output"
Take your protein pills and put your helmet on
```

If either the filter input or argument are not a string, they will be coerced to a string before
replacement.

## replace_first

`<string> | replace_first: <string>[, <string>]`

Return a copy of the input string with the first occurrence of the first argument replaced with the second argument. If the second argument is omitted, it will default to an empty string, making `replace_first` behave like `remove_first`.

```liquid
{{ "Take my protein pills and put my helmet on" | replace_first: "my", "your" }}
```

```plain title="output"
Take your protein pills and put my helmet on
```

If either the filter input or argument are not a string, they will be coerced to a string before replacement.

## replace_last

`<string> | replace_last: <string>, <string>`

Return a copy of the input string with the last occurrence of the first argument replaced with the second argument.

```liquid
{{ "Take my protein pills and put my helmet on" | replace_first: "my", "your" }}
```

```plain title="output"
Take my protein pills and put your helmet on
```

If either the filter input or argument are not a string, they will be coerced to a string before replacement.

## reverse

`<array> | reverse`

Return a copy of the input array with the items in reverse order. If the filter input is a string,
`reverse` will return the string unchanged.

```liquid
{% assign my_array = "apples, oranges, peaches, plums" | split: ", " -%}

{{ my_array | reverse | join: ", " }}
```

```plain title="output"
plums, peaches, oranges, apples
```

## round

`<number> | round[: <number>]`

Return the input number rounded to the given number of decimal places. The number of digits defaults
to `0`.

```liquid
{{ 1.2 | round }}
{{ 2.7 | round }}
{{ 183.357 | round: 2 }}
```

```plain title="output"
1
3
183.36
```

If either the filter input or its optional argument are not an integer or float, they will be
converted to an integer or float before rounding.

## rstrip

`<string> | rstrip`

Return the input string with all trailing whitespace removed. If the input is not a string, it will
be converted to a string before stripping whitespace.

```liquid
{{ "          So much room for activities          " | rstrip }}!
```

```plain title="output"
          So much room for activities!
```

## safe

`<string> | safe`

Return the input string marked as safe to use in an HTML or XML document. If the filter input is not
a string, it will be converted to an HTML-safe string.

:::caution
`safe` is a non-standard feature added to Python Liquid for use with
[HTML auto-escaping](../introduction/auto-escape.md).
:::

With auto-escape enabled and the following global variables:

```json title="data"
{
  "username": "Sally",
  "greeting": "</p><script>alert('XSS!');</script>"
}
```

```liquid title="template"
<p>{{ greeting }}, {{ username }}</p>
<p>{{ greeting | safe }}, {{ username }}</p>
```

```html title="output"
<p>&lt;/p&gt;&lt;script&gt;alert(&#34;XSS!&#34;);&lt;/script&gt;, Sally</p>
<p></p><script>alert('XSS!');</script>, Sally</p>
```

## size

`<object> | size`

Return the size of the input object. Works on strings, arrays and hashes.

```liquid
{{ "Ground control to Major Tom." | size }}
{{ "apples, oranges, peaches, plums" | split: ", " | size }}
```

```plain title="output"
28
4
```

## slice

`<sequence> | slice: <int>[, <int>]`

Return a substring or subsequence of the input string or array. The first argument is the zero-based
start index. The second, optional argument is the length of the substring or sequence, which
defaults to `1`.

```liquid
{{ "Liquid" | slice: 0 }}
{{ "Liquid" | slice: 2 }}
{{ "Liquid" | slice: 2, 5 }}
{% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}
{{ beatles | slice: 1, 2 | join: " " }}
```

```plain title="output"
L
q
quid
Paul George
```

If the first argument is negative, the start index is counted from the end of the sequence.

```liquid
{{ "Liquid" | slice: -3 }}
{{ "Liquid" | slice: -3, 2 }}
{% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}
{{ beatles | slice: -2, 2 | join: " " }}
```

```plain title="output"
u
ui
George Ringo
```

## sort

`<array> | sort[: <string>]`

Return a copy of the input array with its elements sorted.

```liquid
{% assign my_array = "zebra, octopus, giraffe, Sally Snake" | split: ", " -%}
{{ my_array | sort | join: ", " }}
```

```plain title="output"
Sally Snake, giraffe, octopus, zebra
```

The optional argument is a sort key. If given, it should be the name of a property and the filter's
input should be an array of objects.

```json title="data"
{
  "collection": {
    "products": [
      { "title": "A Shoe", "price": "9.95" },
      { "title": "A Tie", "price": "0.50" },
      { "title": "A Hat", "price": "2.50" }
    ]
  }
}
```

```liquid title="template"
{% assign products_by_price = collection.products | sort: "price" -%}
{% for product in products_by_price %}
  <h4>{{ product.title }}</h4>
{% endfor %}
```

```plain title="output"
<h4>A Tie</h4>
<h4>A Hat</h4>
<h4>A Shoe</h4>
```

## sort_natural

`<array> | sort_natural[: <string>]`

Return a copy of the input array with its elements sorted case-insensitively. Array elements
compared by their string representations, forced to lowercase.

```liquid
{% assign my_array = "zebra, octopus, giraffe, Sally Snake" | split: ", " -%}
{{ my_array | sort_natural | join: ", " }}
```

```plain title="output"
giraffe, octopus, Sally Snake, zebra
```

The optional argument is a sort key. If given, it should be the name of a property and the filter's
input should be an array of objects. Array elements are compared using the lowercase string
representation of that property.

```json title="data"
{
  "collection": {
    "products": [
      { "title": "A Shoe", "company": "Cool Shoes" },
      { "title": "A Tie", "company": "alpha Ties" },
      { "title": "A Hat", "company": "Beta Hats" }
    ]
  }
}
```

```liquid title="template"
{% assign products_by_company = collection.products | sort_natural: "company" %}
{% for product in products_by_company %}
  <h4>{{ product.title }}</h4>
{% endfor %}
```

```plain title="output"
<h4>A Tie</h4>
<h4>A Hat</h4>
<h4>A Shoe</h4>
```

## split

`<string> | split: <string>`

Return an array of strings that are the input string split on the filter's argument string.

```liquid
{% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}

{% for member in beatles %}
  {{- member }}
{% endfor %}
```

```plain title="output"
John
Paul
George
Ringo
```

If the argument is undefined or an empty string, the input will be split at every character.

```liquid
{{ "Hello there" | split: nosuchthing | join: "#" }}
```

```plain title="output"
H#e#l#l#o# #t#h#e#r#e
```

## strip

`<string> | strip`

Return the input string with all leading and trailing whitespace removed. If the input is not a
string, it will be converted to a string before stripping whitespace.

```liquid
{{ "          So much room for activities          " | strip }}!
```

```plain title="output"
So much room for activities!
```

## strip_html

`<string> | strip_html`

Return the input string with all HTML tags removed.

```liquid
{{ "Have <em>you</em> read <strong>Ulysses</strong>?" | strip_html }}
```

```plain title="output"
Have you read Ulysses?
```

## strip_newlines

`<string> | strip_newlines`

Return the input string with `\n` and `\r\n` removed.

```liquid
{% capture string_with_newlines %}
Hello
there
{% endcapture -%}

{{ string_with_newlines | strip_newlines }}
```

```plain title="output"
Hellothere
```

## sum

`<array> | sum[: <string>]`

**_New in version 1.9.3_**

Return the sum of all numeric elements in an array.

```liquid
{% assign array = '1,2,3' | split: ',' -%}
{{ array | sum }}
```

```plain title="output"
6
```

If the optional string argument is given, it is assumed that array items are hash/mapping-like, and the argument should be the name of a property/key. The values at `array[property]` will be summed.

## times

`<number> | times: <number>`

Return the product of the input number and the argument number. If either the input or argument are
not a number, Liquid will try to convert them to a number. If that conversion fails, `0` is used
instead.

```liquid
{{ 3 | times: 2 }}
{{ "24" | times: "7" }}
{{ 183.357 | times: 12 }}
```

```plain title="output"
6
168
2200.284
```

## truncate

`<string> | truncate[: <integer>[, <string>]]`

Return a truncated version of the input string. The first argument, length, defaults to `50`. The
second argument defaults to an ellipsis (`...`).

If the length of the input string is less than the given length (first argument), the input string
will be truncated to `length` minus the length of the second argument, with the second argument
appended.

```liquid
{{ "Ground control to Major Tom." | truncate: 20 }}
{{ "Ground control to Major Tom." | truncate: 25, ", and so on" }}
{{ "Ground control to Major Tom." | truncate: 20, "" }}
```

```plain title="output"
Ground control to...
Ground control, and so on
Ground control to Ma
```

## truncatewords

`<string> | truncatewords[: <integer>[, <string>]]`

Return the input string truncated to the specified number of words, with the second argument
appended. The number of words (first argument) defaults to `15`. The second argument defaults to an
ellipsis (`...`).

If the input string already has fewer than the given number of words, it is returned unchanged.

```liquid
{{ "Ground control to Major Tom." | truncatewords: 3 }}
{{ "Ground control to Major Tom." | truncatewords: 3, "--" }}
{{ "Ground control to Major Tom." | truncatewords: 3, "" }}
```

```plain title="output"
Ground control to...
Ground control to--
Ground control to
```

## uniq

`<array> | uniq[: <string>]`

Return a copy of the input array with duplicate elements removed.

```liquid
{% assign my_array = "ants, bugs, bees, bugs, ants" | split: ", " -%}
{{ my_array | uniq | join: ", " }}
```

```plain title="output"
ants, bugs, bees
```

If an argument is given, it should be the name of a property and the filter's input should be an
array of objects.

```json title="data"
{
  "collection": {
    "products": [
      { "title": "A Shoe", "company": "Cool Shoes" },
      { "title": "A Tie", "company": "alpha Ties" },
      { "title": "Another Tie", "company": "alpha Ties" },
      { "title": "A Hat", "company": "Beta Hats" }
    ]
  }
}
```

```liquid title="template"
{% assign one_product_from_each_company = collections.products | uniq: "company" -%}
{% for product in one_product_from_each_company -%}
  - product.title
{% endfor %}
```

```plain title="output"
- A Shoe
- A Tie
- A Hat
```

## upcase

`<string> | upcase`

Return the input string with all characters in uppercase.

```liquid
{{ 'Hello, World!' | upcase }}
```

```plain title="output"
HELLO, WORLD!
```

## url_decode

`<string> | url_decode`

Return the input string with `%xx` escapes replaced with their single-character equivalents. Also
replaces `'+'` with `' '`.

```liquid
{{ "My+email+address+is+bob%40example.com%21" | url_decode }}
```

```plain title="output"
My email address is bob@example.com!
```

## url_encode

`<string> | url_encode`

Return the input string with URL reserved characters %-escaped. Also replaces `' '` with `'+'`.

```liquid
{{ My email address is bob@example.com! | url_encode }}
```

```plain title="output"
My+email+address+is+bob%40example.com%21
```

## where

`<array> | where: <string>[, <object>]`

Return a copy of the input array including only those objects that have a property, named with the
first argument, equal to a value, given as the second argument. If a second argument is not given,
only elements with the named property that are truthy will be included.

```json title="data"
{
  "products": [
    { "title": "Vacuum", "type": "house", "available": true },
    { "title": "Spatula", "type": "kitchen", "available": false },
    { "title": "Television", "type": "lounge", "available": true },
    { "title": "Garlic press", "type": "kitchen", "available": true }
  ]
}
```

```liquid
All products:
{% for product in products -%}
- {{ product.title }}
{% endfor %}

{%- assign kitchen_products = products | where: "type", "kitchen" -%}

Kitchen products:
{% for product in kitchen_products -%}
- {{ product.title }}
{% endfor %}

{%- assign available_products = products | where: "available" -%}

Available products:
{% for product in available_products -%}
- {{ product.title }}
{% endfor %}
```

```plain title="output"
All products:
- Vacuum
- Spatula
- Television
- Garlic press

Kitchen products:
- Spatula
- Garlic press

Available product:
- Vacuum
- Television
- Garlic press
```
