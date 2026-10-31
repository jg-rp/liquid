Configuration
=============

Template parsing and rendering behavior is configured using an instance of
:class:`liquid.Environment`. Once configured, you'd parse templates with
:meth:`liquid.Environment.parse` or :meth:`liquid.Environment.get_template`, both of
which return an instance of :class:`liquid.Template`.

The default environment
-----------------------

The default Liquid environment and a new instance of :class:`liquid.Environment` without
any arguments is equivalent to the following.

.. code-block:: python

    from liquid import (
        DictLoader,
        Environment,
        LegacyLexer,
        LegacyParser,
        ResourceLimits,
        Undefined,
    )

    env = Environment(
        autoescape=False,
        bare_brackets=True,
        conventional_operator_precedence=False,
        extra=False,
        globals=None,
        iterable_strings=False,
        loader=DictLoader({}),
        parser=LegacyParser,
        resource_limits=ResourceLimits(),
        shorthand_indexes=False,
        strict_filters=True,
        tokenizer=LegacyLexer,
        undefined=Undefined,
    )

All the features
----------------

If you're not concerned with Shopify/liquid compatibility and want a reasonable
configuration with extra tags and filters enabled, start with this.

.. code-block:: python

    from liquid import (
        CachingFileSystemLoader,
        Environment,
        ExtendedLexer,
        ExtendedParser,
        StrictUndefined,
    )

    env = Environment(
        autoescape=True,
        conventional_operator_precedence=True,
        extra=True,
        iterable_strings=True,
        loader=CachingFileSystemLoader("path/to/templates"),
        parser=ExtendedParser,
        strict_filters=True,
        tokenizer=ExtendedLexer,
        undefined=StrictUndefined,
    )

Tokenizers and parsers
----------------------

Some features are enabled and disabled by choosing a combination of template tokenizer
and parser, configured with the `tokenizer` and `parser` ``Environment`` constructor
arguments. Built-in choices are:

* :class:`liquid.LegacyLexer` or :class:`liquid.ExtendedLexer`
* :class:`liquid.LegacyParser`, :class:`liquid.ExtendedParser`,
  :class:`liquid.LaxLegacyParser` and :class:`liquid.LaxExtendedParser`.

``LegacyLexer`` and ``LegacyParser`` are the defaults. Together they implement
Shopify/liquid version 5.13 syntax and semantics. It is not possible to change markup
delimiters when using ``LegacyLexer``.

The extended lexer:

* Adds hash-style comments (``{# .. #}``).
* Adds proper string literal parsing without interfering with markup delimiters
  (``{{ "this is a delimiter '}}'" }}``).
* Allows custom markup delimiters.

The extended parser:

* Adds a logical ``not`` operator.
* Adds parentheses for grouping terms.
* Adds Python-style ternary expressions (``a if b else c``).
* Adds arithmetic operators (``+``, ``-``, ``*``, ``/`` and ``%``).
* Allows logical ``and`` and ``or`` in all tags and the output statement, with short
  circuit, last value semantics.
* Allows filter application (``|``) in all tags and the output statement with a well-
  defined precedence that plays nicely with parentheses.

Those last two points are important. With the extended parser, **expressions are composable
and all operators are available in every expression**.

