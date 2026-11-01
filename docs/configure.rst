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

All features
------------

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
and parser, configured with the `tokenizer` and `parser` arguments to the
:class:`liquid.Environment` constructor. Built-in choices are:

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
* Allows ``=`` as well as ``:`` between names and values in named tag and filter arguments.
* Allows logical ``and`` and ``or`` in all tags and the output statement, with short
  circuit, last value semantics.
* Allows filter application (``|``) in all tags and the output statement with a
  well-defined precedence that plays nicely with parentheses.

Those last two points are important. With the extended parser, **expressions are composable
and all operators are available in every expression**.

Custom markup delimiters
^^^^^^^^^^^^^^^^^^^^^^^^

You can choose alternative markup delimiters by subclassing :class:`liquid.ExtendedLexer`
and defining class variables for ``out_start``, ``out_end``, ``tag_start`` and
``tag_end``. Then pass the subclass to the `tokenizer` argument of the
:class:`liquid.Environment` constructor.

In this example we use square brackets instead of braces in all delimiters.

.. code-block:: python

    from liquid import Environment, ExtendedLexer


    class MyTokenizer(ExtendedLexer):
        comment_start: str = "[#"
        comment_end: str = "#]"

        out_start: str = "[["
        out_end: str = "]]"

        tag_start: str = "[%"
        tag_end: str = "%]"


    env = Environment(tokenizer=MyTokenizer)

    source = """\
    [% for x in y %]
        * [[ x -]]
    [% endfor %]
    """

    print(env.render(source, {"y": [1, 2, 3]}))
    #   * 1
    #   * 2
    #   * 3

Lax parsing
^^^^^^^^^^^

Python Liquid's lax parsers, :class:`liquid.LaxLegacyParser` and
:class:`liquid.LaxExtendedParser`, suppress syntax errors and attempt to continue
parsing template source text. In some cases an earlier error can lead to confusing or
misleading errors messages later on.

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

Managing tags and filters
-------------------------

New instances of :class:`liquid.Environment` and the default environment have all
"standard" :doc:`tags <./tags>` and :doc:`filters <./filters>` enabled by default.
"standard" tags and filters are those included in the reference implementation,
`Shopify/liquid`_, which is not to be confused with the variation of Liquid available
on Shopify's e-commerce platform.

.. _Shopify/liquid: https://github.com/Shopify/liquid

We can add to, remove or replace tags and filters by updating an environment's `tags` and
`filters` properties. They are regular dictionaries mapping tag/filter names to
:class:`liquid.Tag` and :type:`liquid.Filter`, respectively.

In this example we remove all base64 filters and add the non-standard ``{% with %}`` tag.

.. code-block:: python

    from liquid import Environment
    from liquid.tags import WithTag

    env = Environment()

    del env.filters["base64_decode"]
    del env.filters["base64_encode"]
    del env.filters["base64_url_safe_decode"]
    del env.filters["base64_url_safe_encode"]

    env.tags["with"] = WithTag

Alternatively you can subclass :class:`liquid.Environment` and override
`setup_tags_and_filters`.

.. code-block:: python

    from liquid import Environment
    from liquid.tags import WithTag


    class MyLiquidEnvironment(Environment):
        def setup_tags_and_filters(self, *, extra: bool = False) -> None:
            super().setup_tags_and_filters(extra=extra)

            del self.filters["base64_decode"]
            del self.filters["base64_encode"]
            del self.filters["base64_url_safe_decode"]
            del self.filters["base64_url_safe_encode"]

            self.tags["with"] = WithTag


    env = MyLiquidEnvironment()

Global variables
----------------

A template's global variables are those added by application developers rather than
created by template authors using ``{% assign %}`` and ``{% capture %}``.

We can pin or attach global variables to instances of :class:`liquid.Environment` and/or
:class:`liquid.Template`. At render time those pinned variables are combined with
variables passed to :meth:`liquid.Template.render` and added to the template scope.

By default, if there's a name conflict, globals variables attached to a template take
priority over global variables attached to the environment.

.. code-block:: python

    from liquid import Environment

    env = Environment(
        globals={
            "greeting": "Hello",
            "name": "World",
            "punctuation": "?",
        }
    )

    template = env.parse(
        "{{ greeting }}, {{ name }}{{ punctuation }}",
        globals={
            "punctuation": "!",
        },
    )

    print(template.render())  # Hello, World!
    print(template.render({"greeting": "Goodbye"}))  # Goodbye, World!
    print(template.render({"name": "Liquid", "punctuation": "."}))  # Hello, Liquid.

HTML auto escape
----------------

TODO:

Resource limits
---------------

TODO:

