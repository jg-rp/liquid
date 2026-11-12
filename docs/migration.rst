Migration guide
===============

This is the documentation for Python Liquid version 3 (GitHub_). Archived documentation
for versions 1 and 2 can be found `here <https://jg-rp.github.io/python-liquid-docs-archive/>`_
and `here <https://github.com/jg-rp/liquid/blob/v2.3.6/docs/index.md>`_, respectively.

.. _GitHub: https://github.com/jg-rp/liquid

In version 3, Python Liquid improves template parsing performance, adds a few opt-in
template language features and makes several breaking API changes.

Python versions and dependencies
--------------------------------

The minimum supported Python version is now 3.12. Anyone still using Python version
3.9, 3.10 or 3.11 will not be able to use Python Liquid version 3.

We've added ``tzdata`` as a dependency and removed the ``pytz`` dependency in favour of
Python's built-in ``zoneinfo`` module.

New template language features
------------------------------

Extended syntax
^^^^^^^^^^^^^^^

Some new template language features are available when Liquid is
:doc:`configured <configure>` with an :class:`ExtendedLexer <liquid.ExtendedLexer>`
and/or an  :class:`ExtendedParser <liquid.ExtendedParser>`. 

The extended lexer:

* Adds hash-style comments (``{# .. #}``).
* Adds proper string literal parsing without interfering with markup delimiters
  (``{{ "this is a delimiter '}}'" }}``).
* Allows custom markup delimiters.

The extended parser:

* Adds a logical ``not`` operator and parentheses for grouping terms.
* Adds Python-style ternary expressions (``a if b else c``).
* Adds arithmetic operators (``+``, ``-``, ``*``, ``/`` and ``%``).
* Allows ``=`` as well as ``:`` between names and values in named tag and filter arguments.
* Allows logical ``and`` and ``or`` in all tags and the output statement, with short
  circuit, last value semantics.
* Allows filter application (``|``) in all tags and the output statement with a
  well-defined precedence that plays nicely with parentheses.

Those last two points are important. With the extended parser, **expressions are composable
and all operators are available in every expression**.

See :doc:`expressions` for examples.

Self
^^^^

We've added the ``self`` keyword and an option to disable bare brackets, as found in
Shopify/liquid in version 5.13 (See `Shopify/liquid #2060 <https://github.com/Shopify/liquid/pull/2060>`_).

This is most likely in preparation for future array literal syntax, which is yet to be
implemented in Ruby or Python Liquid.

New template engine features
----------------------------

Drops
^^^^^

The *Drop interface* (developer defined types for templates) has been redesigned to:

* Give drop methods access to context data and environment config at render time.
* Support lazy and/or async iteration with the ``{% for %}`` tag.
* Consolidate and give fine-grained control of coercion to Liquid primitive types.

See :doc:`drop_api`.


Lax parsing
^^^^^^^^^^^

The new lax parsers, :class:`liquid.LaxLegacyParser` and :class:`liquid.LaxExtendedParser`,
suppress syntax errors and attempt to continue parsing template source text. In some cases
an earlier error can lead to confusing or misleading error messages later on.

After parsing with a lax parser, a list of errors can be retrieved using
:meth:`liquid.Template.errors`.

.. code-block:: python

    from liquid import Environment, LaxLegacyParser

    env = Environment(parser=LaxLegacyParser)

    # Typo in the `if` expression.
    template = env.parse(
        "{% if a =! b %}TRUE{% else %}FALSE{% endif %}",
        name="some_template",

    )

    for error in template.errors():
        print(error)

.. code-block:: text
    :caption: output

    unknown or missing operator
      -> 'some_template' 1:8
      |
    1 | {% if a =! b %}TRUE{% else %}FALSE{% endif %}
      |         ^ unknown or missing operator

This can be useful for discovering multiple errors in one go, but it's usually best
to keep template parsing an rendering as strict as possible so errors don't go unnoticed.

Error capture and rendering
^^^^^^^^^^^^^^^^^^^^^^^^^^^

A list of (potentially many) render time exceptions can now be retrieved using
:meth:`liquid.Template.render_with_errors`. It returns a ``(rendered string, error list)``
tuple, with error messages written to the output string at the point they occurred.

API changes
-----------

* ``Template(source)`` can no longer be used to parse a template from a string. Use
  :func:`liquid.parse` or :meth:`liquid.Environment.parse` instead.

* Removed ``Environment.from_string()``. Use :func:`liquid.parse` or
  :meth:`liquid.Environment.parse` instead.

* Changed :func:`liquid.render`, :meth:`liquid.Environment.render` and
  :meth:`liquid.Template.render` to accept data as a dict (or any mapping) instead of
  keyword arguments.

* Renamed class ``BoundTemplate`` to :class:`liquid.Template`.

* Removed :class:`liquid.Environment` class variables in favour of constructor arguments.

* Renamed several :class:`liquid.Environment` constructor arguments.

* Removed ``Environment.add_tag()`` and ``Environment.add_filter()``. Update dictionaries
  :attr:`liquid.Environment.tags` and :attr:`liquid.Environment.filters` directly
  instead.

* Removed ``DebugUndefined``. Use :meth:`liquid.Template.render_with_errors` instead.

* Removed ``StrictDefaultUndefined``. Use ``FalsyStrictUndefined`` instead.

* Renamed ``BaseLoader`` to :class:`liquid.Loader`.

* ``__html__`` is no longer used to serialize a drop to an HTML safe string. Use
  :meth:`liquid.LiquidPrimitive.__liquid__()` with the ``"output"`` hint instead.

Drops
^^^^^

Drops (developer defined types for templates) are no longer tied to Python's
:class:`collections.abc.Mapping` interface. They are now defined by protocols with
``__liquid_<...>__`` methods. It's still OK to add custom ``Mapping``
objects to render context data, but they are just mappings.

Whereas before you'd implement ``__getitem__(self, key)`` and possibly
``__getitem_async__(self, key)``, now you'd implement the :class:`liquid.LiquidObject`
protocol and the :class:`liquid.LiquidAsyncObject` protocol.

See :doc:`data`.

Tags
^^^^

Abstract classes ``liquid.Tag`` and ``liquid.Node`` have been removed in favour of a
pair of :class:`Protocols <typing.Protocol>`, :class:`liquid.Tag` and :class:`liquid.Markup`,
without any concrete base class.

Typically one would implement ``Tag`` and ``Markup`` with a single class, where
``Tag.parse()`` is a static or class method.

:meth:`liquid.Tag.parse` receives the last token and an instance of :class:`liquid.Parser`,
which has useful methods for parsing expressions and blocks from an existing token stream.

If built-in tokens and expressions will not do and you need to parse expression text
yourself, use :meth:`liquid.Parser.raw_expression`. It returns source text up to the
next end tag delimiter.

See :doc:`tag_api`.

Filters
^^^^^^^

We no longer use decorators to coerce filter inputs to acceptable types. Nor do we use
decorators to indicate that a filter accepts the active render context or environment.

Instead we define filters as callables. They can be functions or classes with a
``__call__`` method.

.. autotype:: liquid.Filter
    :no-index:

The first argument is always an instance of :class:`liquid.FilterContext`, which has
access to the render context and active environment.

The second argument is the result of evaluating the left hand side of the filter
expression, and remaining arguments are defined by the filter.

Instances of ``FilterContext`` also have convenient methods for coercing objects to
primitive types, and methods for testing objects for Liquid truthiness and nullish-ness.

See :doc:`filter_api`.
