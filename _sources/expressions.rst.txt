Extended expressions
====================

Extended expression syntax is available when Python Liquid is configured with an
:class:`liquid.ExtendedParser`. See :ref:`tokenizers-and-parsers` for more information.

Unlike the legacy parser, the extended parser makes expressions composable. Logical
operators, arithmetic operators, conditional expressions and filters can be combined
freely wherever an expression is expected. This applies not just to output statements,
but also to tag arguments and filter arguments.

Logical expressions
-------------------

The extended parser adds a logical ``not`` operator and parentheses, ``(`` and ``)``, for
grouping terms.

In standard Liquid you might write something like this.

.. code-block:: liquid2

    {% if user.active or user.trial %}
      {% unless user.suspended %}
        Access granted.
      {% endunless %}
    {% endif %}

Using ``not`` and parens, we could write it like this.

.. code-block:: liquid2

    {% if (user.active or user.trial) and not user.suspended %}
      Access granted.
    {% endif %}

Or, with a ternary expression, like this.

.. code-block:: liquid2

    {{ "Access granted." if (user.active or user.trial) and not user.suspended }}

Short circuit, last value
^^^^^^^^^^^^^^^^^^^^^^^^^

``and`` and ``or`` are short circuiting operators with last value semantics, just like
Python.

Instead of a multi-branch ``{% if %}`` tag:

.. code-block:: liquid2

    {% if user.nickname %}
      {{ user.nickname }}
    {% elsif user.name %}
      {{ user.name }}
    {% else %}
      Guest
    {% endif %}

We can use a single ``or`` expression directly inside an output statement.

.. code-block:: liquid2

    {{ user.nickname or user.name or "Guest" }}

Or, if ``user`` is potentially undefined or ``null``:

.. code-block:: liquid2

   {{ user.nickname if user and user.nickname else "Guest" }}

Often, we can use ``or`` instead of the ``default`` filter.

.. code-block:: liquid2

    {{ product.sale_price | default: product.price }}
    {{ product.sale_price or product.price }}

Logical operators are not limited to *left values* either, they can be used in filter
arguments.

.. code-block:: liquid2

    {{ items | join: (separator or ", ") }}

Arithmetic
----------

The extended parser adds arithmetic operators ``+``, ``-``, ``*``, ``/`` and ``%``, which
behave exactly the same as their equivalent filters, type coercion and all.

Instead of using filters like this.

.. code-block:: liquid2

    {% assign total = price | times: quantity | plus: shipping %}

We can use arithmetic operators and parens, if needed.

.. code-block:: liquid2

    {% assign total = price * quantity + shipping %}

Like all operators, arithmetic is not limited to ``{% assign %}`` and output statements.

.. code-block:: liquid2

    {% if price * quantity > budget %}
      Over budget!
    {% endif %}

Ternary Expressions
-------------------

The extended parser supports Python-style ternary expressions.

.. code-block:: text

    <expression> if <condition>[ else <expression>]

If the *condition* is falsy and no ``else`` branch is given, the expression evaluates to
the special value ``NOTHING``, which is similar to ``null``.

.. code-block:: liquid2

    {{ "Welcome back!" if user else "Please sign in." }}

Keyword assignment
------------------

The extended parser accepts ``=`` as well as ``:`` between named arguments and their
value expressions. In this example we use the :ref:`with-tag` tag to create temporary,
block-scoped variables.

.. code-block:: liquid2

    {% with
      a = 1,
      b = 3.4,
      c = a + b,
    %}
      {{ a }} + {{ b }} = {{ c }}
    {% endwith %}

Operator Precedence
-------------------

+-----------+----------------+----------------------------------------+---------------------------------+
| Priority  | Operator       | Operators / Syntax                     | Examples                        |
|           | Category       |                                        |                                 |
+===========+================+========================================+=================================+
| 1         | Primary &      | Literals, Variables, ``(...)``,        | ``(a + b)``                     |
| (Highest) | Grouping       |                                        |                                 |
+-----------+----------------+----------------------------------------+---------------------------------+
| 2         | Unary          | ``-``, ``+``                           | ``-count``                      |
+-----------+----------------+----------------------------------------+---------------------------------+
| 3         | Multiplicative | ``*``, ``/``, ``%``                    | ``total * tax_rate``            |
+-----------+----------------+----------------------------------------+---------------------------------+
| 4         | Additive       | ``+``, ``-``                           | ``price + shipping``            |
+-----------+----------------+----------------------------------------+---------------------------------+
| 5         | Filter Pipe    | \|                                     | ``name | upcase``               |
+-----------+----------------+----------------------------------------+---------------------------------+
| 6         | Comparison &   | ``==``, ``!=``, ``<``, ``>``, ``<=``,  | ``item.qty > 0``,               |
|           | Ordering       | ``>=``, ``contains``                   | ``tags contains tag``           |
+-----------+----------------+----------------------------------------+---------------------------------+
| 7         | Logical NOT    | ``not``                                | ``not user.logged_in``          |
+-----------+----------------+----------------------------------------+---------------------------------+
| 8         | Logical AND    | ``and``                                | ``has_stock and visible``       |
+-----------+----------------+----------------------------------------+---------------------------------+
| 9         | Logical OR     | ``or``                                 | ``is_admin or is_owner``        |
+-----------+----------------+----------------------------------------+---------------------------------+
| 10        | Inline         | ``... if ... else ...``                | ``a if condition else b``       |
| (Lowest)  | Conditional    |                                        |                                 |
+-----------+----------------+----------------------------------------+---------------------------------+
