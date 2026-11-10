Extra tags
==========

The tags described on this page are **not** enabled by default. You can enable all
:ref:`extra-features`, or import and register just the tags you need individually (see
:ref:`managing-tags-and-filters`).

If we were to register all extra tags manually, it would look like this.

.. code-block:: python

    import liquid
    from liquid.tags import BlockTag, CallTag, ExtendsTag, MacroTag, TranslateTag, WithTag

    env = liquid.Environment()
    env.tags["block"] = BlockTag
    env.tags["call"] = CallTag
    env.tags["extends"] = ExtendsTag
    env.tags["macro"] = MacroTag
    env.tags["translate"] = TranslateTag
    env.tags["with"] = WithTag

extends
-------

.. code-block:: text

   {% extends <template name> %}

Together with the ```block`` <#block>`__ tag, the ``extends`` tag allows you to inherit
content and Liquid markup from parent templates and define blocks that can be overridden
by child templates.

In this example ``page.html`` inherits from ``base.html`` and overrides the ``content``
block. As ``page.html`` does not define a ``footer`` block, the footer from ``base.html``
is used.

.. code-block:: liquid2
    :caption: base.html

    <body>
      <div id="content">{% block content required %}{% endblock %}</div>
      <div id="footer">{% block footer %}Default footer{% endblock %}</div>
    </body>

.. code-block:: liquid2
    :caption: page.html

    {% extends 'base.html' %}
    {% block content %}Hello, {{ you }}!{% endblock %}

block
~~~~~

.. code-block:: text

    {% block <name> [required] %} <Liquid markup> {% endblock [<name>] %}

Every ``block`` tag must have a name that is unique to the template. ``endblock`` tags can
include a name too. If given, the ``endblock`` name must match the name given at the start
of the block.

If the optional ``required`` argument is given, the block must be overridden by a child
template, otherwise a ``RequiredBlockError`` will be raised.

.. code-block:: liquid2

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

Super blocks
^^^^^^^^^^^^

A ``block`` object is available inside every ``{% block %}`` tag. It has just one
property, ``super``. If a ``{% block %}`` is overriding a parent block,
``{{ block.super }}`` will render the parent's implementation of that block.

In this example we use ``{{ block.super }}`` in the ``footer`` block to output the base
template's footer with a year appended to it.

.. code-block:: liquid2
    :caption: base

    <head>
      {% block head %}{% endblock %}
    <head>
    <body>
      <div id="content">{% block content required %}{% endblock %}</div>
      <div id="footer">{% block footer %}Default footer{% endblock %}</div>
    </body>

.. code-block:: liquid2
    :caption: child

    {% extends "base" %}
    {% block content %}Hello, World!{% endblock %}
    {% block footer %}{{ block.super }} - 2025{% endblock %}

.. code-block:: html
    :caption: output

    <body>
      <div id="content">Hello, World!</div>
      <div id="footer">Default footer - 2025</div>
    </body>

macro and call
--------------

.. code-block:: text

    {% macro <name> [[,] [ <identifier>[: <expression>]] ... ] %}
      <liquid markup>
    {% endmacro %}

.. code-block:: text

    {% call <name> [[,] [ <identifier>[: <expression>]] ... ] %}

The ``macro`` tag defines a parameterized block that can later be called using the
``call`` tag.

A macro is like defining a function. You define a parameter list, possibly with default
values, that are expected to be provided by a ``call`` tag. A macro tag's block has its
own scope including its arguments and template global variables.

Note that argument defaults are bound late. They are evaluated when a call expression is
evaluated, not when the macro is defined.

.. code-block:: liquid2

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

Excess arguments passed to ``call`` are collected into variables called ``args`` and
``kwargs``, so variadic macros a possible too.

.. code-block:: liquid2

    {% macro 'foo' %}
      {% for arg in args %}
        - {{ arg }}
      {% endfor %}
 
      {% for arg in kwargs %}
        - {{ arg.0 }} => {{ arg.1 }}
      {% endfor %}
    {% endmacro %}
 
    {% call 'foo' 42, 43, 99, a: 3.14, b: 2.71828 %}

.. _translate-tag:

translate
---------

.. code-block:: text

    {% translate
        [context: <string>]
        [, count: <number>]
        [, <identifier>: <object> ] ... %}
      <text,variable> ...
    [ {% plural %} <text,variable> ... ]
    {% endtranslate %}

The ``translate`` tag defines text to be translated into another language. Said text can
contain placeholders for variables. These placeholders look like Liquid output statements,
but can't use dotted or bracketed property syntax or filters.

If a German translations object is found in the current render context, this example would
output ``Hallo Welt!``.

.. code-block:: liquid2

    {% translate %}
      Hello, World!
    {% endtranslate %}

If a ``{% plural %}`` block follows the message text and the special ``count`` argument is
considered plural, the ``{% plural %}`` block will be rendered instead. Again, with a
German translations object, this example would render ``Hallo Welten!``.

.. code-block:: liquid2

    {% translate count: 2 %}
      Hello, World!
    {% plural %}
      Hello, Worlds!
    {% endtranslate %}

Keyword arguments are used to add (or shadow existing) variables.

.. code-block:: liquid2

    {% translate you: 'Sue' %}
      Hello, {{ you }}!
    {% endtranslate %}

with
----

.. code-block:: text

    {% with <identifier>: <expression> [, <identifier>: <expression> ... ] %}
      <liquid markup>
    {% endwith %}

The ``with`` tag extends the template namespace with block scoped variables. These
variables have the potential to shadow global variables or variables assigned with
``{% assign %}`` and ``{% capture %}``.

.. code-block:: liquid2

    {% with p: collection.products.first %}
      {{ p.title }}
    {% endwith %}
 
    {% with a: 1, b: 3.4 %}
      {{ a }} + {{ b }} = {{ a | plus: b }}
    {% endwith %}
