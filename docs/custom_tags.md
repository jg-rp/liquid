A Liquid tag is defined by a class extending [`Tag`](api/tag.md). It has just one abstract method, [`parse()`](api/tag.md#liquid.Tag.parse), which takes an instance of [`TokenStream`](api/tokens.md#liquid.TokenStream) and returns a [`Node`](api/ast.md#liquid.Node). The returned node will be added to a template's abstract syntax tree and, when rendered, its [`render_to_output()`](api/ast.md#liquid.Node.render_to_output) method will be called.

`render_to_output()` receives the active [render context](api/render_context.md) and an output buffer. It is responsible for either updating the render context or writing to the buffer, or both.

!!! tip

    See [liquid/builtin/tags](https://github.com/jg-rp/liquid/tree/main/liquid/builtin/tags) for lots of examples.

## Add a tag

This example implements the `with` tag, which allows template authors to define block scoped variables. `{% with %}` is a _block tag_. It has a start tag, an end tag (`{% endwith %}`), and Liquid markup in between. We should ensure that we leave the closing tag token at the head of the stream.

### The tag

```python title="with_tag.py"
from typing import TextIO

from liquid import BlockNode
from liquid import Node
from liquid import RenderContext
from liquid import Tag
from liquid import Token
from liquid import TokenStream
from liquid.builtin.expressions import KeywordArgument
from liquid.parser import get_parser
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_TAG


class WithTag(Tag):

    name = "with"
    block = True

    def parse(self, stream: TokenStream) -> Node:
        # Assert that the token at the head of the stream is a tag token
        # and consume it.
        token = stream.eat(TOKEN_TAG)

        # Using the KeywordArgument.parse static method ensure consistent
        # parsing behavior between tags.
        args = KeywordArgument.parse(self.env, stream.into_inner(tag=token))

        # Parse Liquid markup until we reach a tag called "endwith" or the end
        # of the stream
        block = get_parser(self.env).parse_block(stream, ("endwith", TOKEN_EOF))

        # Assert that the token at the head of the stream is a tag token
        # called "endwith".
        stream.expect(TOKEN_TAG, value="endwith")

        return WithNode(token, args, block)

```

When `parse()` is called, the token at the head of the stream is guaranteed to be of type `TOKEN_TAG`, representing the start of our tag. For block tags, like `{% with %}`, we use `TokenStream.eat()` to both assert the current token type and consume it.

`{% with %}` expects one or more arguments in the form of key/value pairs. `TokenStream.into_inner()` asserts that the next token is of type `TOKEN_EXPRESSION` and returns a new stream of tokens over the tag's expression. Here we've passed it straight to `KeywordArgument.parse()` because we only want to accepts key/value arguments in this example.

Next we get an instance of [`Parser`](api/parser.md) and use it to parse a block of Liquid markup until we reach a tag called "endwith". `TokenStream.expect()` asserts that we did find an "endwith" tag an not reach the end of the stream.

### The node

```python title="with_tag.py (continued)"
class WithNode(Node):
    __slots__ = ("args", "block")

    def __init__(self, token: Token, args: list[KeywordArgument], block: BlockNode):
        super().__init__(token)
        self.args = args
        self.block = block
        self.blank = self.block.blank

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        namespace = dict(arg.evaluate(context) for arg in self.args)

        with context.extend(namespace):
            return self.block.render(context, buffer)
```

`WithNode.render_to_output()` evaluates its arguments, extends the render context and renders its block to the output buffer. The [`RenderContext.extend`](api/render_context.md#liquid.RenderContext.extend) context manager is used to ensure the variables added by our tag go out of scope after the block has been rendered.

### Usage

We can now register `WithTag` with a Liquid environment using [`Environment.add_tag`](api/environment.md#liquid.Environment.add_tag).

```python
from liquid import Environment

from .with_tag import WithTag

env = Environment()
env.add_tag(WithTag)

template = env.from_string(
"{% with greeting: 'Hello', name: 'Sally' -%}"
"  {{ greeting }}, {{ name }}!"
"{%- endwith %}"
)

print(template.render()) # Hello, Sally
```

## Replace a tag

[`Environment.add_tag`](api/environment.md#liquid.Environment.add_tag) uses the `name` class attribute of its argument when registering tags. If your custom tag has a name matching a builtin tag, `add_tag()` will replace it without warning.

```python
from liquid import Environment
from .my_tag import MyTag

env = Environment()
env.add_tag(MyTag)

# ...
```

## Remove a tag

Remove a built-in tag by deleting it from your [environment's](environment.md) [`tags`](api/environment.md#liquid.Environment.tags) dictionary. The example removes the builtin `ifchanged` tag

```python
from liquid import Environment

env = Environment()
del env.tags["ifchanged"]

# ...
```

!!! tip

    You can add, remove and replace tags on `liquid.DEFAULT_ENVIRONMENT` too. Convenience functions [`parse()`](api/convenience.md#liquid.parse) and [`render()`](api/convenience.md#liquid.render) use `DEFAULT_ENVIRONMENT`
