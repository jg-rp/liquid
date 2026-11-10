Tag
===

Liquid tags are defined by a pair of :class:`Protocols <typing.Protocol>`, :class:`liquid.Tag` and
:class:`liquid.Markup`.

``Tag`` has a single method, ``parse()``, that is called by the parser and given the
current token and the stateful parser instance as arguments. ``parse()`` then uses
methods on :class:`liquid.Parser` to process already scanned tokens, and returns a class
implementing :class:`Markup`.

.. code-block:: text
    :dedent: 0

                                 Template source text
                                          │
                                          ▼
                                        Lexer
                       (Tokenizes template, including expressions)
                                          │
                                          ▼
                                        Parser
                   (Steps through tokens, reads from the tag register)
                                          │
                                          ▼
                          Parser calls Tag.parse(token, parser)
                                          │
                                          ▼
                        Tag parses tokens using methods on `parser`
                                  and returns `Markup`
                                          │
                                          ▼
                         Parser adds `Markup` to the active block

.. tip::

    If built-in tokens and expressions will not do and you need to parse expression text
    yourself, use :meth:`liquid.Parser.raw_expression`. It returns source text up to the
    next end tag delimiter.

At render time, Liquid calls :meth:`liquid.Markup.render` whenever it needs to render a
tag, at which point the tag should write output text to the provided buffer.

.. code-block:: text
    :dedent: 0

                                Template.render(data)
                                          │
                                          ▼
                            Markup.render(context, buffer)

.. tip::

    It's often convenient to implement :class:`liquid.Tag` and :class:`liquid.Markup`
    with a single class, where ``Tag.parse()`` is a static or class method. All built-in
    filters do this.

API
---

.. autoclass:: liquid.Tag
    :members:
    :show-inheritance:

.. autoclass:: liquid.Markup
    :members:
    :show-inheritance:

.. autoclass:: liquid.Parser
    :members:

.. autoclass:: liquid.StringBuffer
    :members:

.. autotype:: liquid.Node

.. autotype:: liquid.Block