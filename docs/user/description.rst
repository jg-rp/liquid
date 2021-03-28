.. _description:

.. _reference documentation: https://shopify.github.io/liquid/

Language Description
====================

This page describes the Liquid template language. What follows is targeted at
developers rather than end users, and should be read in addition to the
`reference documentation`_.

If you're already familiar with Liquid template syntax, you might want to skip
ahead to :ref:`rendering`.

.. note::

    I use the term ``output statement`` or ``statement`` where the reference
    documentation would use ``object``. I find the definitions presented here
    to be more accurate and inline with what a developer would expect and 
    ``object`` to be.

Templates
---------

A template is any text, possibly read from a file or database, with placeholders
for `variables`_, and `tags <block tags>`_ for things like conditional logic and
repeating blocks.

This is an example template showing Liquid being used with some HTML.

.. code-block:: liquid

    <h1>{{ page.heading }}</h1>
    
    {% if contacts != empty %}
      <ul>
        {% for contact in contacts %}
          <li>{{ contact.name | capitalize }}</li>
        {% endfor %}
      </ul>
    {% else %}
      <p>no contacts</p>
    {% endif %}


Output Statements
-----------------

Output statements are placeholders within a template. When a template engine
encounters an output statement, the statement is substituted with the result of
its expression.

This is an output statement:

.. code-block:: liquid

    {{ page.title }}

Here, ``{{`` is the statement start sequence, ``page.title`` is the expression,
and ``}}`` is the statement end sequence. Any whitespace either side of an
expression is insignificant.

The expression part can be any single literal or identifier, followed by zero or
more `filters`_.

Literals
~~~~~~~~

A literal `string`, `integer`, `float` or `boolean` is a valid output statement
expression. There is no such thing as an object/dictionary or array/list literal
in Liquid.

.. table:: Examples of output statement literals
    :width: 100%

    ============ ================== ===========
    Literal      Example            Output
    ============ ================== ===========
    String       ``{{ "hello" }}``  ``hello``
                 ``{{ 'hello' }}``  ``hello``
    Integer      ``{{ -5 }}``       ``-5``
                 ``{{ 42 }}``       ``42``
    Float        ``{{ -1.1 }}``     ``-1.1``
                 ``{{ 3.14 }}``     ``3.14``
    Boolean      ``{{ true }}``     ``true``
                 ``{{ false }}``    ``false``
    ============ ================== ===========

An output statement containing only a constant expression is not terribly
useful, but literals do come in handy as arguments to `filters`_ and in
`assignment <assign>`_ expressions.

Variables
~~~~~~~~~

Variables are set using the built-in `assign`_ or `capture`_ tags. Referencing
a variable by name is also a valid output statement expression.

**Template**

.. code-block:: liquid

    {% assign foo = 'bar' %}
    {{ foo }}

**Output**

.. code-block:: text

    bar

Context
~~~~~~~

Objects from the active render context can be referenced by name. If an object
has properties, you can access those properties using dot or bracket notation.
These three statement are equivalent.

.. code-block:: text

    {{ section.settings.menu.links }}
    {{ section["settings"]["menu"]["links"] }}
    {{ section["settings"]["menu"].links }}

As is this

.. code-block:: text

    {% assign foo = "settings" %}
    {{ section[foo].menu.links }}

If the object is an `array` (or array-like), you can access the object at a
given index, again using dot or bracket notation. If ``links`` is an `array`:
    
.. code-block:: text

    {{ links.0 }}
    {{ links[0] }}

Operators (or lack thereof)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Output statements **can not** contain arithmetic operators (``+``, ``*``,
etc.), assignment operators (``=``, ``+=``, etc.), comparison operators
(``<=``, ``>``, etc.) or logical operators (``and``, ``or``, etc.).

There are, however, some built-in `filters`_ that cover basic arithmetic. Such
as `plus`_, `minus`_ and `modulo`_


Scope
~~~~~

TODO:


Filters
-------

TODO:

minus
~~~~~

TODO:

modulo
~~~~~~

TODO:

plus
~~~~

TODO:

Built-in Objects
----------------

TODO:

nil
~~~

TODO:

blank
~~~~~

TODO:

empty
~~~~~

TODO:

Block Tags
----------

TODO:

capture
~~~~~~~

for
~~~

TODO:

if
~~~

TODO:

Inline Tags
-----------

TODO:

assign
~~~~~~

TODO:

render
~~~~~~

TODO:

Template Literals
-----------------

TODO:

Whitespace Control
------------------

TODO: