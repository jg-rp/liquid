.. _tags:

Template Tags
=============

TODO:

Custom Tags
-----------

Register a new tag with an ``Environment`` by calling its ``add_tag`` method. All tags
must  inherit from ``liquid.tag.Tag`` and implement its ``parse`` method.

``parse`` takes a single argument of type ``TokenStream`` that wraps an iterator of
``Token``\s, and returns an ``ast.Node`` instance. More often than not, a new subclass
of ``ast.node`` will accompany each ``Tag``. These ``Node``\s make up the parse tree,
and are responsible for writing rendered text to the output stream via the required
``render_to_output`` method.

Here's the implementation of ``UnlessTag``, which parses a boolean expression and a
block of statements before returning a ``UnlessNode``.

.. code-block:: python

    class UnlessTag(Tag):

        name = TAG_UNLESS
        end = TAG_ENDUNLESS

        def parse(self, stream: TokenStream) -> Node:
            parser = get_parser(self.env)

            expect(stream, TOKEN_TAG, value=TAG_UNLESS)
            tok = stream.current
            stream.next_token()

            expect(stream, TOKEN_EXPRESSION)
            expr_iter = tokenize_boolean_expression(stream.current.value)
            expr = parse_boolean_expression(TokenStream(expr_iter))

            stream.next_token()
            consequence = parser.parse_block(stream, ENDUNLESSBLOCK)

            expect(stream, TOKEN_TAG, value=TAG_ENDUNLESS)

            return UnlessNode(
                tok=tok,
                condition=expr,
                consequence=consequence
            )

Things worthy of note: 

- Block tags (those that have a start and end tag with any number of statements in
  between) are expected to leave the stream with their closing tag as the current token.

- The template lexer does not attempt to tokenize tag expressions. It is up to the
  ``Tag`` to tokenize and parse its expression, if any, possibly using or extending a
  built-in expression lexer found in ``liquid.lex``.

- The ``expect`` and ``expect_peek`` helper functions inspect tokens from the stream and
  raise an appropriate exception should a token's type or value not meet a tag's
  expectations.

- You can find parsers for common expression types in ``liquid.parse``, all of which
  return a ``liquid.expression.Expression``. ``Expression``\s have an
  ``evaluate(context)`` method for use from ``ast.Node.render_to_output``.


All built-in tags are implemented in this way, so have a look in
``liquid/builtin/tags/`` for examples. 