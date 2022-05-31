# Custom Tags

A Liquid [tag](../language/introduction.md#tags) is defined by a pair of Python classes. One a subclass of [`liquid.tag.Tag`](../api/tag.md) and one a subclass of [`liquid.ast.Node`](../api/node.md). The required `parse()` method of a `Tag` is responsible for parsing a tag's expression and returning a `Node`, which will be added to a template's parse tree.

You can add to, remove or modify Liquid's built-in tags to suit your needs by registering tags with an [`Environment`](../api/environment.md), then rendering your templates from that environment.

:::info
All built-in tags are implemented in this way, so have a look in [liquid/builtin/tags/](https://github.com/jg-rp/liquid/tree/main/liquid/builtin/tags) for examples.
:::

## Add a Tag

Taking inspiration from [Django's Template Language](https://docs.djangoproject.com/en/3.2/ref/templates/builtins/#with), lets implement a `with` tag, which extends the local scope for the duration of its block. Our `with` tag's expressions consists of one or more named arguments separated by commas. Each argument is a variable name, followed by a colon, then a Liquid keyword, string, integer, float, range expression or identifier.

```plain
{% with <identifier>: <object> [, <identifier>: object ... ] %}
  <literal,statement,tag> ...
{% endwith %}
```

This implementation keeps any variables set inside the `with` block (using `assign` or `capture`) alive after the block has been rendered.

### Example Tag

A [`Tag`](../api/tag.md) is free to parse its expression any way it chooses. Built in tags use regular expressions to generate a stream of tokens, then step through those tokens yielding `Expression` objects.

Here we'll reuse the tokenizer from the [`include`](../language/tags.md#include) tag, as it, too, accepts any number of comma separated named arguments. We will, however, supply a different set of allowed keywords to the tokenizer function.

```python title="with_tag.py"
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

tokenize_with_expression = partial(
    _tokenize,
    rules=_compile_rules(include_expression_rules),
    keywords=with_expression_keywords,
)


class WithKeywordArg(NamedTuple):
    name: str
    expr: Expression

# ...
```

The [`parse()`](../api/tag.md#parse) method of a `Tag` object receives a `TokenStream` as its only argument. This stream of tokens includes template literals, output statements, tags and unparsed tag expressions.

The current token in the stream will always be of the type `TOKEN_TAG`, representing the start of the tag we're parsing. By convention, this token is used to populate the `token` property of the associated `Node` object. If the tag has an expression (anything after the tag's name), it will immediately follow the `TOKEN_TAG` in the stream as a `TOKEN_EXPRESSION`. In the example bellow we use `expect()` to confirm that an expression has been provided.

We retrieve a `Parser` from the active [`Environment`](../api/environment.md), then use its `parse_block` method parse our `with` tag's block, which could contain any number of other tags and output statements. Every block tag is expected to leave the stream with it's "end" tag as the current token.

Note that `parse_argument` is an implementation detail and a required method of [`liquid.tag.Tag`](../api/tag.md).

```python title="with_tag.py (continued)"
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

# ...
```

### Example Node

Every [`Node`](../api/node.md) must implement a [`render_to_output()`](../api/node.md#rendertooutput) method and, optionally, a [`render_to_output_async()`](../api/node.md#rendertooutputasync) method. By referencing its `Expression`'s and the active render context, `render_to_output()` is responsible for writing text to the output buffer.

Our `WithNode` simply evaluates each of its arguments and uses the results to extend the scope of the active render context before rendering its block.

```python title="with_tag.py (continued)"
class WithNode(Node):
    def __init__(self, tok: Token, args: Dict[str, Expression], block: BlockNode):
        self.tok = tok
        self.args = args
        self.block = block

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        namespace = {k: v.evaluate(context) for k, v in self.args.items()}

        with context.extend(namespace):
            self.block.render(context, buffer)

```

### Example Tag Usage

We can add `WithTag` tag to an [`Environment`](../api/environment.md) like this. Notice that [`Environment.add_tag()`](../api/environment.md#addtag) takes a class, not a class instance.

```python
from liquid import Environment
from with_tag import WithTag

env = Environment()
env.add_tag(WithTag)

template = env.from_string(
    "{% with greeting: 'Hello', name: 'Sally' -%}"
    "  {{ greeting }}, {{ name }}!"
    "{%- endwith %}"
)

print(template.render()) # Hello, Sally
```

## Replace a Tag

[Environment.add_tag()](../api/environment.md#add_tag) registers a tag using the `name` property
defined on the `Tag` class. If you register a tag with the same name as an existing tag, it will be replaced without warning.

For example, the [if (not)](https://github.com/jg-rp/liquid-extra#if-not) tag from [python-liquid-extra](https://github.com/jg-rp/liquid-extra) is a drop-in replacement for the standard `if` tag.

## Remove a Tag

Remove a tag, either built-in or custom, by deleting it from [Environment.tags](../api/environment.md). It's a regular dictionary mapping tag names to `Tag` classes.

```python
from liquid import Environment
from liquid.builtin.tags.ifchanged_tag import IfChangedTag

env = Environment()
del env.filters[IfChangedTag.name]
```
