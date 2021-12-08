# Custom Tags

Tags allow us to include logic, like loops and conditions, in our Liquid templates. A tag can be
an _inline_ tag or a _block_ tag, and can add to rendered output text or not.

Block tags have a start and end tag, with any number of statements in between. Here, the `if` tag
is a block tag (notice the `endif`), whereas `render` is not.

```liquid
{% if product.available %}
  {% render "product.html" with product %}
{% endif %}
```

See [the tag reference](../language/tags) for an explanation of each built-in tag. Also see the
[python-liquid-extra](https://github.com/jg-rp/liquid-extra) project, where several additional tags
and filters are maintained.

## Add a Tag

Register a new tag with an [Environment](../api/Environment) by calling its [add_tag](../api/Environment#add_tag)
method. Then render templates from that environment.

:::info
API documentation for `liquid.tag.Tag`, `liquid.ast.Node` and `liquid.expression.Expression` is a
work in progress. Please do ask questions on the [issue tracker](https://github.com/jg-rp/liquid/issues)
if you need assistance.
:::

All tags must inherit from `liquid.tag.Tag` and implement its `parse` method. `parse` takes a single
argument of type `TokenStream` that wraps an iterator of `Token`s, and returns an `ast.Node`
instance. More often than not, a new subclass of `ast.node` will accompany each `Tag`. These
`Node`s make up the parse tree, and are responsible for writing rendered text to the output stream
via the required `render_to_output` method.

Taking inspiration from [Django's Template Language](https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#with),
lets implement a `with` tag, which extends the active context for the life of its block.

This implementation sticks with Liquid style arguments, using colons rather than equals like Django.
And any variables set inside the `with` block using `assign` or `capture` will persist after it
ends. We could have copied rather than extended the `context` passed to `render_to_output`, creating
a proper block scope.

```python title="withblock.py"
from __future__ import annotations

import sys

from functools import partial

from typing import TYPE_CHECKING
from typing import Dict
from typing import NamedTuple
from typing import Optional
from typing import TextIO

from liquid.ast import Node
from liquid.ast import BlockNode

from liquid.context import Context
from liquid.expression import Expression

from liquid.lex import include_expression_rules
from liquid.lex import _compile_rules
from liquid.lex import _tokenize

from liquid.parse import expect
from liquid.parse import get_parser
from liquid.parse import parse_expression
from liquid.parse import parse_unchained_identifier

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_AS
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_COMMA


if TYPE_CHECKING:
    from liquid import Environment

TAG_WITH = sys.intern("with")
TAG_ENDWITH = sys.intern("endwith")

with_expression_keywords = frozenset(
    [
        TOKEN_TRUE,
        TOKEN_FALSE,
        TOKEN_NIL,
        TOKEN_NULL,
        TOKEN_AS,
    ]
)

# We're borrowing token rules from the `include` tag, with our own set of valid
# keywords.
tokenize_with_expression = partial(
    _tokenize,
    rules=_compile_rules(include_expression_rules),
    keywords=with_expression_keywords,
)


class WithKeywordArg(NamedTuple):
    name: str
    expr: Expression


class WithNode(Node):
    def __init__(self, tok: Token, args: Dict[str, Expression], block: BlockNode):
        self.tok = tok
        self.args = args
        self.block = block

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        namespace = {k: v.evaluate(context) for k, v in self.args.items()}

        with context.extend(namespace):
            self.block.render(context, buffer)


class WithTag(Tag):
    name = TAG_WITH
    end = TAG_ENDWITH

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=TAG_WITH)
        tok = stream.current

        stream.next_token()
        expect(stream, TOKEN_EXPRESSION)
        expr_stream = TokenStream(tokenize_with_expression(stream.current.value))

        # A dictionary to help handle duplicate keywords.
        args = {}

        while expr_stream.current.type != TOKEN_EOF:
            key, expr = self.parse_argument(expr_stream)
            args[key] = expr

            if expr_stream.current.type == TOKEN_COMMA:
                expr_stream.next_token()  # Eat comma

        stream.next_token()
        block = self.parser.parse_block(stream, (TAG_ENDWITH, TOKEN_EOF))
        expect(stream, TOKEN_TAG, value=TAG_ENDWITH)

        return WithNode(tok=tok, args=args, block=block)

    def parse_argument(self, stream: TokenStream) -> WithKeywordArg:
        key = str(parse_unchained_identifier(stream))
        stream.next_token()

        expect(stream, TOKEN_COLON)
        stream.next_token()  # Eat colon

        val = parse_expression(stream)
        stream.next_token()

        return WithKeywordArg(key, val)
```

We can then add `WithTag` tag to an environment like this. Notice that `add_tag` take a class, not
a class instance.

```python
from liquid import Environment
from withblock import WithTag

env = Environment()
env.add_tag(WithTag)
```

Things worthy of note:

- Block tags (those that have a start and end tag with any number of statements in
  between) are expected to leave the stream with their closing tag as the current token.

- The template lexer does not attempt to tokenize tag expressions. It is up to the
  `Tag` to tokenize and parse its expression, if any, possibly using or extending a
  built-in expression lexer found in `liquid.lex`.

- The `expect` and `expect_peek` helper functions inspect tokens from the stream and
  raise an appropriate exception should a token's type or value not meet a tag's
  expectations.

- You can find parsers for common expression types in `liquid.parse`, all of which return a
  `liquid.expression.Expression`. `Expression`s have an `evaluate(context)` method for use from
  `ast.Node.render_to_output`.

All built-in tags are implemented in this way, so have a look in [liquid/builtin/tags/](https://github.com/jg-rp/liquid/tree/main/liquid/builtin/tags) for examples.

## Replace a Tag

[Environment.add_tag()](../api/Environment#add_tag) registers a tag using the `name` property
defined on the `Tag` class. If you register a tag with the same name as an existing tag, it will be
replaced without warning.

For example, the [if (not)](https://github.com/jg-rp/liquid-extra#if-not) tag from
[python-liquid-extra](https://github.com/jg-rp/liquid-extra) is a drop-in replacement for the
standard `if` tag.

## Remove a Tag

Remove a tag, either built-in or custom, by deleting it from [Environment.tags](../api/Environment).
It's a regular dictionary mapping tag names to `Tag` classes.

```python
from liquid import Environment
from liquid.builtin.tags.ifchanged_tag import IfChangedTag

env = Environment()
del env.filters[IfChangedTag.name]
```
