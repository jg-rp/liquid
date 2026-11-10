Standard filters
================

.. note::

    This page describes "standard" filters. Python Liquid also has some extra filters and
    extended expression syntax that are disabled by default. See :doc:`extra_filters` and
    :doc:`expressions` for documentation on non-standard features.

abs
---

.. code-block:: text

   <number> | abs

Return the absolute value of a number. Works on integers, floats and string
representations of integers or floats.

.. code-block:: liquid2

   {{ -42 | abs }}
   {{ 7.5 | abs }}
   {{ '42.0' | abs }}

.. code-block:: text
    :caption: output

    42
    7.5
    42.0

Given a value that can't be cast to an integer or float, ``0`` will be returned.

.. code-block:: liquid2

   {{ 'hello' | abs }}
   {{ nosuchthing | abs }}

.. code-block:: text
    :caption: output

    0
    0

append
------

.. code-block:: text

   <string> | append: <string>

Return the input value concatenated with the argument value.

.. code-block:: liquid2

   {{ 'Hello, ' | append: 'World!' }}

.. code-block:: text
    :caption: output

    Hello, World!

If either the input value or argument are not a string, they will be coerced to a string
before concatenation.

.. code-block:: liquid2

   {% assign a_number = 7.5 -%}
   {{ 42 | append: a_number }}
   {{ nosuchthing | append: 'World!' }}

.. code-block:: text
    :caption: output

    427.5
    World!

at_least
--------

.. code-block:: text

   <number> | at_least: <number>

Return the maximum of the filter's input value and its argument. If either input value or
argument are string representations of an integer or float, they will be cast to an
integer or float prior to comparison.

.. code-block:: liquid2

   {{ -5.1 | at_least: 8 }}
   {{ 8 | at_least: '5' }}

.. code-block:: text
    :caption: output

    8
    8

If either input value or argument can not be cast to an integer or float, ``0`` will be
used instead.

.. code-block:: liquid2

   {{ "hello" | at_least: 2 }}
   {{ "hello" | at_least: -2 }}
   {{ -1 | at_least: "abc" }}

.. code-block:: text
    :caption: output

    2
    0
    0

at_most
-------

.. code-block:: text

   <number> | at_most: <number>

Return the minimum of the filter's input value and its argument. If either input value or
argument are string representations of an integer or float, they will be cast to an
integer or float prior to comparison.

.. code-block:: liquid2

   {{ 5 | at_most: 8 }}
   {{ '8' | at_most: 5 }}

.. code-block:: text
    :caption: output

    5
    5

If either input value or argument can not be cast to an integer or float, ``0`` will be
used instead.

.. code-block:: liquid2

   {{ "hello" | at_most: 2 }}
   {{ "hello" | at_most: -2 }}
   {{ -1 | at_most: "abc" }}

.. code-block:: text
    :caption: output

    0
    -2
    -1

capitalize
----------

.. code-block:: text

   <string> | capitalize

Return the input string with the first character in upper case and the rest lowercase.

.. code-block:: liquid2

   {{ 'heLLO, World!' | capitalize }}

.. code-block:: text
    :caption: output

    Hello, world!

If the input value is not a string, it will be converted to a string.

.. code-block:: liquid2

   {{ 42 | capitalize }}

.. code-block:: text
    :caption: output

    42

ceil
----

.. code-block:: text

   <number> | ceil

Round the input value up to the nearest whole number. The input value will be converted to
a number if it is not an integer or float.

.. code-block:: liquid2

   {{ 5.1 | ceil }}
   {{ 5.0 | ceil }}
   {{ 5 | ceil }}
   {{ '5.4' | ceil }}

.. code-block:: text
    :caption: output

    6
    5
    5
    5

If the input is undefined or can't be converted to a number, ``0`` is returned.

.. code-block:: liquid2

   {{ 'hello' | ceil }}
   {{ nosuchthing | ceil }}

.. code-block:: text
    :caption: output

    0
    0

compact
-------

.. code-block:: text

   <array> | compact[: <string>]

Remove ``nil`` or ``null`` (or ``None`` in Python) values from an array-like object. If
given, the argument should be the name of a property that exists on each item (hash, dict
etc.) in the array-like sequence.

For example, if ``pages`` is an array of objects, some of which have a ``category``
property:


.. code-block:: json
    :caption: data

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

Without ``compact``, iterating those categories will include ``nil`` / ``null`` values.

.. code-block:: liquid2

   {% assign categories = pages | map: "category" -%}

   {% for category in categories -%}
   - {{ category }}
   {%- endfor %}

.. code-block:: text
    :caption: output

    - business 
    - celebrities
    -
    - lifestyle
    - sports
    -
    - technology

With ``compact``, we can remove those missing categories before the loop.

.. code-block:: liquid2

   {% assign categories = pages | map: "category" | compact %}

   {% for category in categories %}
   - {{ category }}
   {% endfor %}

.. code-block:: text
    :caption: output

    - business
    - celebrities
    - lifestyle
    - sports
    - technology

Using the optional argument to ``compact``, we could avoid using ``map`` and create an
array of pages with a ``category`` property, rather than an array of categories.

.. code-block:: liquid2

   {% assign pages_with_category = pages | compact: "category" %}

   {% for page in pages_with_category %}
   - {{ page.category }}
   {% endfor %}

.. code-block:: text
    :caption: output

    - business
    - celebrities
    - lifestyle
    - sports
    - technology

concat
------

.. code-block:: text

   <array> | concat: <array>

Create a new array by joining one array-like object with another.

.. code-block:: liquid2

   {% assign fruits = "apples, oranges, peaches" | split: ", " %}
   {% assign vegetables = "carrots, turnips, potatoes" | split: ", " %}

   {% assign everything = fruits | concat: vegetables %}

   {% for item in everything %}
   - {{ item }}
   {% endfor %}

.. code-block:: text
    :caption: output

    - apples
    - oranges
    - peaches
    - carrots
    - turnips
    - potatoes

If the input value is not array-like, it will be converted to an array. No conversion is
attempted for the argument value.

.. code-block:: liquid2

   {% assign fruits = "apples, oranges, peaches" | split: ", " -%}
   {% assign things = "hello" | concat: fruits -%}

   {% for item in things -%}
   - {{ item }}
   {% endfor %}

.. code-block:: text
    :caption: output

    - h
    - e
    - l
    - l
    - o
    - apples
    - oranges
    - peaches

If the input is a nested array, it will be flattened before concatenation. The argument is
not flattened.

.. code-block:: json
    :caption: data

    {
      "a": [
        ["a", "x"],
        ["b", ["y", ["z"]]]
      ],
      "b": ["c", "d"]
    }

.. code-block:: liquid2

   {{ a | concat: b | join: '#' }}

.. code-block:: text
    :caption: output

    a#x#b#y#z#c#d

date
----

.. code-block:: text

   <datetime> | date: <string>

Format a date and/or time according the the given format string. The input can be a
string, in which case the string will be parsed as a date/time before formatting.

.. code-block:: liquid2

   {{ "March 14, 2016" | date: "%b %d, %y" }}

.. code-block:: text
    :caption: output

    Mar 14, 16

The special ``'now'`` or ``'today'`` input values can be used to get the current
timestamp. ``'today'`` is an alias for ``'now'``. Both include time information.

.. code-block:: liquid2

   {{ "now" | date: "%Y-%m-%d %H:%M" }}

.. code-block:: text
    :caption: output

    2021-12-02 10:17

If the input is undefined, an empty string is returned.

default
-------

.. code-block:: text

    <expression> | default[: <object>[, allow_false:<bool>]]

Return a default value if the input is undefined, ``nil``, ``null``, ``false`` or empty,
or return the input unchanged otherwise.

.. code-block:: liquid2

   {{ product_price | default: 2.99 }}

   {%- assign product_price = "" %}
   {{ product_price | default: 2.99 }}

   {%- assign product_price = 4.99 %}
   {{ product_price | default: 2.99 }}

.. code-block:: text
    :caption: output

    2.99
    2.99
    4.99

If the optional ``allow_false`` argument is ``true``, an input of ``false`` will not
return the default. ``allow_false`` defaults to ``false``.

.. code-block:: liquid2

   {% assign product_reduced = false -%}
   {{ product_reduced | default: true, allow_false: true }}

.. code-block:: text
    :caption: output

    false

If no argument is given, the default value will be an empty string.

Empty strings, arrays and objects all cause the default value to be returned. ``0`` does
not.

.. code-block:: liquid2

   {{ "" | default: "hello" }}
   {{ 0 | default: 99 }}

.. code-block:: text
    :caption: output

    hello
    0

divided_by
----------

.. code-block:: text

   <number> | divided_by: <number>

Divide a number by another number. The result is rounded down to the nearest integer if
the divisor is an integer.

.. code-block:: liquid2

   {{ 16 | divided_by: 4 }}
   {{ 5 | divided_by: 3 }}

.. code-block:: text
    :caption: output

    4
    1

If you divide by a float, the result will be a float.

.. code-block:: liquid2

   {{ 20 | divided_by: 7 }}
   {{ 20 | divided_by: 7.0 }}

.. code-block:: text
    :caption: output

    2
    2.857142857142857

If either the input or argument are not an integer or float, Liquid will try to convert
them to an integer or float. If the input can't be converted, ``0`` will be used instead.
If the argument can't be converted, an exception is raised.

.. code-block:: liquid2

   {{ "20" | divided_by: "7" }}
   {{ "hello" | divided_by: 2 }}

.. code-block:: text
    :caption: output

    2
    0

downcase
--------

.. code-block:: text

   <string> | downcase

Return the input string with all characters in lowercase.

.. code-block:: liquid2

   {{ 'Hello, World!' | downcase }}

.. code-block:: text
    :caption: output

    hello, world!

If the input is not a string, Liquid will convert it to a string before forcing characters
to lowercase.

.. code-block:: liquid2

   {{ 5 | downcase }}

.. code-block:: text
    :caption: output

    5

If the input is undefined, an empty string is returned.

.. _escape-filter:

escape
------

.. code-block:: text

   <string> | escape

Escape special characters in a string for safe use in HTML.

This filter replaces the characters ``&``, ``<``, ``>``, ``'``, and ``"`` with their
corresponding HTML-safe sequences:

- ``&`` -> ``&amp;``
- ``<`` -> ``&lt;``
- ``>`` -> ``&gt;``
- ``'`` -> ``&#39;``
- ``"`` -> ``&#34;``

This helps prevent HTML injection when rendering untrusted content in HTML element bodies
or attributes.

.. warning:: 

   This filter does **not** make strings safe for use in JavaScript, including in
   ``<script>`` blocks, inline event handler attributes (e.g. ``onerror``), or other
   JavaScript contexts. For those cases, use the `escapejs`_ filter instead.

.. code-block:: liquid2

   {{ "Have you read 'James & the Giant Peach'?" | escape }}

.. code-block:: text
    :caption: output

    Have you read &#39;James &amp; the Giant Peach&#39;?

.. _escapejs-filter:

escapejs
--------

**New in version 2.1.0**

.. code-block:: text

   <string> | escapejs

Escape characters for safe use in JavaScript string literals.

This filter escapes a string for embedding inside **JavaScript string literals**, using
either single or double quotes (e.g. ``'...'`` or ``"..."``). It replaces control
characters and potentially dangerous symbols with their corresponding Unicode escape
sequences.

Escaped characters include:

- ASCII control characters (U+0000 to U+001F)
- Characters like quotes, angle brackets, ampersands, equals signs - Line/paragraph
  separators (U+2028, U+2029)

.. warning::

   This filter does **not** make strings safe for use in JavaScript template literals
   (backtick strings), or in raw JavaScript expressions. Use it only when placing data
   inside quoted JS strings within inline ``<script>`` blocks or event handlers.

.. code-block:: liquid2

   {% assign some_string = "<script>alert('x')</script>" %}
   <img src="" onerror="{{ some_string | escapejs }}" />

.. code-block:: text
    :caption: output

    <img src="" onerror="\u003Cscript\u003Ealert(\u0027x\u0027)\u003C/script\u003E" />

escape_once
-----------

.. code-block:: text

   <string> | escape_once

Escape a string for HTML, but avoid double-escaping existing entities.

Converts characters like ``&``, ``<``, and ``>`` to their HTML-safe sequences, but leaves
existing HTML entities untouched (e.g., ``&amp;`` stays ``&amp;``).

This is useful when escaping content that may already be partially escaped.

See the `escape`_ filter for details and limitations.

.. code-block:: liquid2

   {{ "Have you read 'James &amp; the Giant Peach'?" | escape_once }}

.. code-block:: text
    :caption: output

    Have you read &#39;James &amp; the Giant Peach&#39;?

find
----

.. code-block:: text

   <array> | find: <string>[, <object>]

Return the first item in the input array that contains a property, given as the first
argument, equal to the value given as the second argument. If no such item exists,
``null`` is returned.

In this example we select the first page in the “Programming” category.

.. code-block:: json
    :caption: data

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

.. code-block:: liquid2

   {% assign page = pages | find: 'category', 'Programming' %}
   {{ page.title }}

.. code-block:: text
    :caption: output

    Mastering JavaScript

find_index
----------

Return the index of the first item in the input array that contains a property, given as
the first argument, equal to the value given as the second argument. If no such item
exists, ``null`` is returned.

In this example we find the index for the first page in the “Programming” category.

.. code-block:: json
    :caption: data

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

.. code-block:: liquid2

   {% assign index = pages | find_index: "category", "Programming" %}
   {{ pages[index]["title"] }}

.. code-block:: text
    :caption: output

    Mastering JavaScript

first
-----

.. code-block:: text

   <sequence> | first

Return the first item of the input sequence. The input could be array-like or a mapping,
but not a string.

.. code-block:: liquid2

   {{ "Ground control to Major Tom." | split: " " | first }}

.. code-block:: text
    :caption: output

    Ground

If the input sequence is undefined, empty or not a sequence, ``nil`` is returned.

floor
-----

.. code-block:: text

   <number> | floor

Return the input down to the nearest whole number. Liquid tries to convert the input to a
number before the filter is applied.

.. code-block:: liquid2

   {{ 1.2 | floor }}
   {{ 2.0 | floor }}
   {{ 183.357 | floor }}
   {{ -5.4 | floor }}
   {{ "3.5" | floor }}

.. code-block:: text
    :caption: output

    1
    2
    183
    -6
    3

If the input can't be converted to a number, ``0`` is returned.

has
---

.. code-block:: text

   <array> | has: <string>[, <object>]

Return ``true`` if the input array contains an object with a property identified by the
first argument that is equal to the object given as the second argument. ``false`` is
returned if none of the items in the input array contain such a property/value.

In this example we test to see if any pages are in the “Programming” category.

.. code-block:: json
    :caption: data

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

.. code-block:: liquid2

   {% assign has_programming_page = pages | has: 'category', 'Programming' %}
   {{ has_programming_page }}

.. code-block:: text
    :caption: output

    true

join
----

.. code-block:: text

   <array> | join[: <string>]

Return the items in the input array as a single string, separated by the argument string.
If the input is not an array, Liquid will convert it to one. If input array items are not
strings, they will be converted to strings before joining.

.. code-block:: liquid2

   {% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}

   {{ beatles | join: " and " }}

.. code-block:: text
    :caption: output

    John and Paul and George and Ringo

If an argument string is not given, it defaults to a single space.

.. code-block:: liquid2

   {% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}

   {{ beatles | join }}

.. code-block:: text
    :caption: output

    John Paul George Ringo

last
----

.. code-block:: text

   <array> | last

Return the last item in the array-like input.

.. code-block:: liquid2

   {{ "Ground control to Major Tom." | split: " " | last }}

.. code-block:: text
    :caption: output

    Tom.

If the input is undefined, empty, string or a number, ``nil`` will be returned.

lstrip
------

.. code-block:: text

   <string> | lstrip

Return the input string with all leading whitespace removed. If the input is not a string,
it will be converted to a string before stripping whitespace.

.. code-block:: liquid2

   {{ "          So much room for activities          " | lstrip }}!

.. code-block:: text
    :caption: output

    So much room for activities          !

map
---

.. code-block:: text

   <array> | map: <string>

Extract properties from an array of objects into a new array.

For example, if ``pages`` is an array of objects with a ``category`` property:

.. code-block:: json
    :caption: data

    {
      "pages": [
        { "category": "business" },
        { "category": "celebrities" },
        { "category": "lifestyle" },
        { "category": "sports" },
        { "category": "technology" }
      ]
    }

.. code-block:: liquid2

   {% assign categories = pages | map: "category" -%}

   {% for category in categories -%}
   - {{ category }}
   {%- endfor %}

.. code-block:: text
    :caption: output

    - business
    - celebrities
    - lifestyle
    - sports
    - technology

minus
-----

.. code-block:: text

   <number> | minus: <number>

Return the result of subtracting one number from another. If either the input or argument
are not a number, Liquid will try to convert them to a number. If that conversion fails,
``0`` is used instead.

.. code-block:: liquid2

   {{ 4 | minus: 2 }}
   {{ "16" | minus: 4 }}
   {{ 183.357 | minus: 12.2 }}
   {{ "hello" | minus: 10 }}

.. code-block:: text
    :caption: output

    2
    12
    171.157
    -10

modulo
------

.. code-block:: text

   <number> | modulo: <number>

Return the remainder from the division of the input by the argument.

.. code-block:: liquid2

   {{ 3 | modulo: 2 }}
   {{ "24" | modulo: "7" }}
   {{ 183.357 | modulo: 12 }}

.. code-block:: text
    :caption: output

    1
    3
    3.357

If either the input or argument are not an integer or float, Liquid will try to convert
them to an integer or float. If the input can't be converted, ``0`` will be used instead.
If the argument can't be converted, an exception is raised.

newline_to_br
-------------

.. code-block:: text

   <string> | newline_to_br

Return the input string with ``\n`` and ``\r\n`` replaced with ``<br />\n``.

.. code-block:: liquid2

   {% capture string_with_newlines %}
   Hello
   there
   {% endcapture %}

   {{ string_with_newlines | newline_to_br }}

.. code-block:: text
    :caption: output

    <br />
    Hello<br />
    there<br />

plus
----

.. code-block:: text

    <number> | plus: <number>

Return the result of adding one number to another. If either the input or argument are
not a number, Liquid will try to convert them to a number. If that conversion fails,
``0`` is used instead.

.. code-block:: liquid2

   {{ 4 | plus: 2 }}
   {{ "16" | plus: "4" }}
   {{ 183.357 | plus: 12 }}

.. code-block:: text
    :caption: output

    6
    20
    195.357

prepend
-------

.. code-block:: text

   <string> | prepend: <string>

Return the argument concatenated with the filter input.

.. code-block:: liquid2

   {{ "apples, oranges, and bananas" | prepend: "Some fruit: " }}

.. code-block:: text
    :caption: output

    Some fruit: apples, oranges, and bananas

If either the input value or argument are not a string, they will be coerced to a string
before concatenation.

.. code-block:: liquid2

   {% assign a_number = 7.5 -%}
   {{ 42 | prepend: a_number }}
   {{ nosuchthing | prepend: 'World!' }}

.. code-block:: text
    :caption: output

    7.542
    World!

reject
------

.. code-block:: text

   <array> | reject: <string>[, <object>]

Return a copy of the input array including only those objects that have a property, named
with the first argument, **that is not equal to** a value, given as the second argument.
If a second argument is not given, only elements with the named property that are falsy
will be included.

.. code-block:: json
    :caption: data

    {
      "products": [
        { "title": "Vacuum", "type": "house", "available": true },
        { "title": "Spatula", "type": "kitchen", "available": false },
        { "title": "Television", "type": "lounge", "available": true },
        { "title": "Garlic press", "type": "kitchen", "available": true }
      ]
    }

.. code-block:: liquid2

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

.. code-block:: text
    :caption: output

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

remove
------

.. code-block:: text

   <string> | remove: <string>

Return the input with all occurrences of the argument string removed.

.. code-block:: liquid2

   {{ "I strained to see the train through the rain" | remove: "rain" }}

.. code-block:: text
    :caption: output

    I sted to see the t through the

If either the filter input or argument are not a string, they will be coerced to a string
before substring removal.

remove_first
------------

.. code-block:: text

   <string> | remove_first: <string>

Return a copy of the input string with the first occurrence of the argument string
removed.

.. code-block:: liquid2

   {{ "I strained to see the train through the rain" | remove_first: "rain" }}

.. code-block:: text
    :caption: output

    I sted to see the train through the rain

If either the filter input or argument are not a string, they will be coerced to a string
before substring removal.

remove_last
-----------

.. code-block:: text

   <string> | remove_last: <string>

Return a copy of the input string with the last occurrence of the argument string removed.

.. code-block:: liquid2

   {{ "I strained to see the train through the rain" | remove_last: "rain" }}

.. code-block:: text
    :caption: output

    I strained to see the train through the

If either the filter input or argument are not a string, they will be coerced to a string
before substring removal.

replace
-------

.. code-block:: text

   <string> | replace: <string>[, <string>]

Return the input with all occurrences of the first argument replaced with the second
argument. If the second argument is omitted, it will default to an empty string, making
``replace`` behave like ``remove``.

.. code-block:: liquid2

   {{ "Take my protein pills and put my helmet on" | replace: "my", "your" }}

.. code-block:: text
    :caption: output

    Take your protein pills and put your helmet on

If either the filter input or argument are not a string, they will be coerced to a string
before replacement.

replace_first
-------------

.. code-block:: text

   <string> | replace_first: <string>[, <string>]

Return a copy of the input string with the first occurrence of the first argument replaced
with the second argument. If the second argument is omitted, it will default to an empty
string, making ``replace_first`` behave like ``remove_first``.

.. code-block:: liquid2

   {{ "Take my protein pills and put my helmet on" | replace_first: "my", "your" }}

.. code-block:: text
    :caption: output

    Take your protein pills and put my helmet on

If either the filter input or argument are not a string, they will be coerced to a string
before replacement.

replace_last
------------

.. code-block:: text

   <string> | replace_last: <string>, <string>

Return a copy of the input string with the last occurrence of the first argument replaced
with the second argument.

.. code-block:: liquid2

   {{ "Take my protein pills and put my helmet on" | replace_first: "my", "your" }}

.. code-block:: text
    :caption: output

    Take my protein pills and put your helmet on

If either the filter input or argument are not a string, they will be coerced to a string
before replacement.

reverse
-------

.. code-block:: text

   <array> | reverse

Return a copy of the input array with the items in reverse order. If the filter input is a
string, ``reverse`` will return the string unchanged.

.. code-block:: liquid2

   {% assign my_array = "apples, oranges, peaches, plums" | split: ", " -%}

   {{ my_array | reverse | join: ", " }}

.. code-block:: text
    :caption: output

    plums, peaches, oranges, apples

round
-----

.. code-block:: text

   <number> | round[: <number>]

Return the input number rounded to the given number of decimal places. The number of
digits defaults to ``0``.

.. code-block:: liquid2

   {{ 1.2 | round }}
   {{ 2.7 | round }}
   {{ 183.357 | round: 2 }}

.. code-block:: text
    :caption: output

    1
    3
    183.36

If either the filter input or its optional argument are not an integer or float, they will
be converted to an integer or float before rounding.

rstrip
------

.. code-block:: text

   <string> | rstrip

Return the input string with all trailing whitespace removed. If the input is not a
string, it will be converted to a string before stripping whitespace.

.. code-block:: liquid2

   {{ "          So much room for activities          " | rstrip }}!

.. code-block:: text
    :caption: output

              So much room for activities!

safe
----

.. code-block:: text

   <string> | safe

Return the input string marked as safe to use in an HTML or XML document. If the filter
input is not a string, it will be converted to an HTML-safe string.

With auto-escape enabled and the following global variables:

.. code-block:: json
    :caption: data

    {
      "username": "Sally",
      "greeting": "</p><script>alert('XSS!');</script>"
    }

.. code-block:: liquid2
    :caption: template

    <p>{{ greeting }}, {{ username }}</p>
    <p>{{ greeting | safe }}, {{ username }}</p>

.. code-block:: text
    :caption: output

    <p>&lt;/p&gt;&lt;script&gt;alert(&#34;XSS!&#34;);&lt;/script&gt;, Sally</p>
    <p></p><script>alert('XSS!');</script>, Sally</p>

size
----

.. code-block:: text

   <object> | size

Return the size of the input object. Works on strings, arrays and hashes.

.. code-block:: liquid2

   {{ "Ground control to Major Tom." | size }}
   {{ "apples, oranges, peaches, plums" | split: ", " | size }}

.. code-block:: text
    :caption: output

    28
    4

slice
-----

.. code-block:: text

   <sequence> | slice: <int>[, <int>]

Return a substring or subsequence of the input string or array. The first argument is the
zero-based start index. The second, optional argument is the length of the substring or
sequence, which defaults to ``1``.

.. code-block:: liquid2

   {{ "Liquid" | slice: 0 }}
   {{ "Liquid" | slice: 2 }}
   {{ "Liquid" | slice: 2, 5 }}
   {% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}
   {{ beatles | slice: 1, 2 | join: " " }}

.. code-block:: text
    :caption: output

    L
    q
    quid
    Paul George

If the first argument is negative, the start index is counted from the end of the
sequence.

.. code-block:: liquid2

   {{ "Liquid" | slice: -3 }}
   {{ "Liquid" | slice: -3, 2 }}
   {% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}
   {{ beatles | slice: -2, 2 | join: " " }}

.. code-block:: text
    :caption: output

    u
    ui
    George Ringo

sort
----

.. code-block:: text

   <array> | sort[: <string>]


Return a copy of the input array with its elements sorted.

.. code-block:: liquid2

   {% assign my_array = "zebra, octopus, giraffe, Sally Snake" | split: ", " -%}
   {{ my_array | sort | join: ", " }}

.. code-block:: text
    :caption: output

    Sally Snake, giraffe, octopus, zebra

The optional argument is a sort key. If given, it should be the name of a property and the
filter's input should be an array of objects.

.. code-block:: json
    :caption: data

    {
      "collection": {
        "products": [
          { "title": "A Shoe", "price": "9.95" },
          { "title": "A Tie", "price": "0.50" },
          { "title": "A Hat", "price": "2.50" }
        ]
      }
    }

.. code-block:: liquid2
    :caption: template

    {% assign products_by_price = collection.products | sort: "price" -%}
    {% for product in products_by_price %}
      <h4>{{ product.title }}</h4>
    {% endfor %}

.. code-block:: text
    :caption: output

    <h4>A Tie</h4>
    <h4>A Hat</h4>
    <h4>A Shoe</h4>

sort_natural
------------

.. code-block:: text

   <array> | sort_natural[: <string>]

Return a copy of the input array with its elements sorted case-insensitively. Array items
will be compared by their string representations, forced to lowercase.

.. code-block:: liquid2

   {% assign my_array = "zebra, octopus, giraffe, Sally Snake" | split: ", " -%}
   {{ my_array | sort_natural | join: ", " }}

.. code-block:: text
    :caption: output

    giraffe, octopus, Sally Snake, zebra

The optional argument is a sort key. If given, it should be the name of a property and the
filter's input should be an array of objects. Array elements are compared using the
lowercase string representation of that property.

.. code-block:: json
    :caption: data

    {
      "collection": {
        "products": [
          { "title": "A Shoe", "company": "Cool Shoes" },
          { "title": "A Tie", "company": "alpha Ties" },
          { "title": "A Hat", "company": "Beta Hats" }
        ]
      }
    }

.. code-block:: liquid2
    :caption: template

    {% assign products_by_company = collection.products | sort_natural: "company" %}
    {% for product in products_by_company %}
      <h4>{{ product.title }}</h4>
    {% endfor %}

.. code-block:: text
    :caption: output

    <h4>A Tie</h4>
    <h4>A Hat</h4>
    <h4>A Shoe</h4>

split
-----

.. code-block:: text

   <string> | split: <string>

Return an array of strings that are the input string split on the filter's argument
string.

.. code-block:: liquid2

   {% assign beatles = "John, Paul, George, Ringo" | split: ", " -%}

   {% for member in beatles %}
     {{- member }}
   {% endfor %}

.. code-block:: text
    :caption: output

    John
    Paul
    George
    Ringo

If the argument is undefined or an empty string, the input will be split at every
character.

.. code-block:: liquid2

   {{ "Hello there" | split: nosuchthing | join: "#" }}

.. code-block:: text
    :caption: output

    H#e#l#l#o# #t#h#e#r#e

squish
------

**New in version 2.2.0**

.. code-block:: text

   <string> | squish

Return the input string with all leading and trailing whitespace removed, and any other
runs of whitespace replaced with a single space.

.. code-block:: liquid2

   {{ "    Hello, \n\t World! \r\n" | squish }}

.. code-block:: text
    :caption: output

    Hello, World!

strip
-----

.. code-block:: text

   <string> | strip

Return the input string with all leading and trailing whitespace removed. If the input is
not a string, it will be converted to a string before stripping whitespace.

.. code-block:: liquid2

   {{ "          So much room for activities          " | strip }}!

.. code-block:: text
    :caption: output

    So much room for activities!

strip_html
----------

.. code-block:: text

   <string> | strip_html

Return the input string with all HTML tags removed.

.. code-block:: liquid2

   {{ "Have <em>you</em> read <strong>Ulysses</strong>?" | strip_html }}

.. code-block:: text
    :caption: output

    Have you read Ulysses?

strip_newlines
--------------

.. code-block:: text

   <string> | strip_newlines

Return the input string with ``\n`` and ``\r\n`` removed.

.. code-block:: liquid2

   {% capture string_with_newlines %}
   Hello
   there
   {% endcapture -%}

   {{ string_with_newlines | strip_newlines }}

.. code-block:: text
    :caption: output

    Hellothere

sum
---

.. code-block:: text

   <array> | sum[: <string>]

Return the sum of all numeric elements in an array.

.. code-block:: liquid2

   {% assign array = '1,2,3' | split: ',' -%}
   {{ array | sum }}

.. code-block:: text
    :caption: output

    6

If the optional string argument is given, it is assumed that array items are
hash/dict/mapping-like, and the argument should be the name of a property/key. The values
at ``array[property]`` will be summed.

times
-----

.. code-block:: text

   <number> | times: <number>

Return the product of the input number and the argument. If either the input or argument
are not a number, Liquid will try to convert them to a number. If that conversion fails,
``0`` is used instead.

.. code-block:: liquid2

   {{ 3 | times: 2 }}
   {{ "24" | times: "7" }}
   {{ 183.357 | times: 12 }}

.. code-block:: text
    :caption: output

    6
    168
    2200.284

truncate
--------

.. code-block:: text

   <string> | truncate[: <integer>[, <string>]]

Return a truncated version of the input string. The first argument, length, defaults to
``50``. The second argument defaults to an ellipsis (``...``).

If the length of the input string is less than the given length (first argument), the
input string will be truncated to ``length`` minus the length of the second argument, with
the second argument appended.

.. code-block:: liquid2

   {{ "Ground control to Major Tom." | truncate: 20 }}
   {{ "Ground control to Major Tom." | truncate: 25, ", and so on" }}
   {{ "Ground control to Major Tom." | truncate: 20, "" }}

.. code-block:: text
    :caption: output

    Ground control to...
    Ground control, and so on
    Ground control to Ma

truncatewords
-------------

.. code-block:: text

   <string> | truncatewords[: <integer>[, <string>]]

Return the input string truncated to the specified number of words, with the second
argument appended. The number of words (first argument) defaults to ``15``. The second
argument defaults to an ellipsis (``...``).

If the input string already has fewer than the given number of words, it is returned
unchanged.

.. code-block:: liquid2

   {{ "Ground control to Major Tom." | truncatewords: 3 }}
   {{ "Ground control to Major Tom." | truncatewords: 3, "--" }}
   {{ "Ground control to Major Tom." | truncatewords: 3, "" }}

.. code-block:: text
    :caption: output

    Ground control to...
    Ground control to--
    Ground control to

uniq
----

.. code-block:: text

   <array> | uniq[: <string>]

Return a copy of the input array with duplicate elements removed.

.. code-block:: liquid2

   {% assign my_array = "ants, bugs, bees, bugs, ants" | split: ", " -%}
   {{ my_array | uniq | join: ", " }}

.. code-block:: text
    :caption: output

    ants, bugs, bees

If an argument is given, it should be the name of a property and the filter's input should
be an array of objects.

.. code-block:: json
    :caption: data

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


.. code-block:: liquid2
    :caption: template

    {% assign one_product_from_each_company = collections.products | uniq: "company" -%}
    {% for product in one_product_from_each_company -%}
      - product.title
    {% endfor %}

.. code-block:: text
    :caption: output

    - A Shoe
    - A Tie
    - A Hat

upcase
------

.. code-block:: text

   <string> | upcase

Return the input string with all characters in uppercase.

.. code-block:: liquid2

   {{ 'Hello, World!' | upcase }}

.. code-block:: text
    :caption: output

    HELLO, WORLD!

url_decode
----------

.. code-block:: text

   <string> | url_decode

Return the input string with ``%xx`` escapes replaced with their single-character
equivalents. Also replaces ``'+'`` with ``' '``.

.. code-block:: liquid2

   {{ "My+email+address+is+bob%40example.com%21" | url_decode }}

.. code-block:: text
    :caption: output

    My email address is bob@example.com!

url_encode
----------

.. code-block:: text

   <string> | url_encode

Return the input string with URL reserved characters %-escaped. Also replaces ``' '`` with
``'+'``.

.. code-block:: liquid2

   {{ "My email address is bob@example.com!" | url_encode }}

.. code-block:: text
    :caption: output

    My+email+address+is+bob%40example.com%21

where
-----

.. code-block:: text

   <array> | where: <string>[, <object>]

Return a copy of the input array including only those objects that have a property, named
with the first argument, equal to a value, given as the second argument. If a second
argument is not given, only elements with the named property that are truthy will be
included.

.. code-block:: json
    :caption: data

    {
      "products": [
        { "title": "Vacuum", "type": "house", "available": true },
        { "title": "Spatula", "type": "kitchen", "available": false },
        { "title": "Television", "type": "lounge", "available": true },
        { "title": "Garlic press", "type": "kitchen", "available": true }
      ]
    }

.. code-block:: liquid2

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

.. code-block:: text
    :caption: output

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
