import collections.abc
import re
import sys
from typing import Optional, Any, List, TextIO, Iterator

from liquid.token import Token, TOKEN_EXPRESSION, TOKEN_TAG_NAME
from liquid.parse import get_parser, expect, parse_loop_expression
from liquid.stream import TokenStream
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import TokenStream, tokenize_loop_expression
from liquid.expression import LoopExpression
from liquid.exceptions import BreakLoop, ContinueLoop

RE_FOR_EXPRESSION = re.compile(r"^(\w[a-zA-Z0-9_\-]*)\s+in\s+([a-zA-Z0-9_\-:.()]+)$")

TAG_FOR = sys.intern("for")
TAG_ENDFOR = sys.intern("endfor")
TAG_ELSE = sys.intern("else")

TAG_BREAK = sys.intern("break")
TAG_CONTINUE = sys.intern("continue")

ENDFORBLOCK = (TAG_ENDFOR, TAG_ELSE)
ENDFORELSEBLOCK = (TAG_ENDFOR,)


class ForLoop(collections.abc.Mapping):
    """Loop helper variables."""

    __slots__ = (
        "name",
        "it",
        "length",
        "item",
        "first",
        "last",
        "index",
        "index0",
        "rindex",
        "rindex0",
        "keys",
    )

    def __init__(self, name: str, it: Iterator[Any], length: int):
        self.name = name
        self.it = it
        self.length = length

        self.item = None
        self.first = False
        self.last = False
        self.index = 0
        self.index0 = -1
        self.rindex = self.length + 1
        self.rindex0 = self.length

        self.keys: List[str] = [
            "length",
            "index",
            "index0",
            "rindex",
            "rindex0",
            "first",
            "last",
        ]

    def __repr__(self):  # pragma: no cover
        return f"ForLoop(name='{self.name}', length={self.length})"

    def __getitem__(self, key):
        if key in self.keys:
            return getattr(self, key)
        raise KeyError(key)

    def __len__(self):
        return len(self.keys)

    def __next__(self):
        self.step()
        return next(self.it)

    def __iter__(self):
        return self

    def __str__(self):
        return "ForLoop"

    def step(self):
        """Set the value for the current/next loop iteration and update forloop
        helper variables."""

        self.index += 1
        self.index0 += 1
        self.rindex -= 1
        self.rindex0 -= 1

        if self.index0 == 0:
            self.first = True
        else:
            self.first = False

        if self.rindex0 == 0:
            self.last = True
        else:
            self.last = False


class ForNode(ast.Node):
    """A parse tree node representing a for loop tag block."""

    __slots__ = ("tok", "expression", "block", "default")

    statement = False

    def __init__(
        self,
        tok: Token,
        expression: LoopExpression,
        block: ast.BlockNode = None,
        default: Optional[ast.BlockNode] = None,
    ):
        self.tok = tok
        self.expression = expression
        self.block = block
        self.default = default

    def __str__(self) -> str:
        tag_str = f"for ({self.expression}) {{ {self.block} }}"

        if self.default:
            tag_str += f" else {{ {self.default} }}"

        return tag_str

    def render_to_output(self, context: Context, buffer: TextIO):
        loop_iter, length = self.expression.evaluate(context)

        if length:
            name = self.expression.name

            forloop = ForLoop(
                name=name,
                it=loop_iter,
                length=length,
            )

            namespace = {
                "forloop": forloop,
                name: None,
            }

            # Extend the context. Essentially giving priority to `ForLoopDrop`, then
            # delegating `get` and `assign` to the outer context.
            with context.extend(namespace):

                for itm in forloop:
                    namespace[name] = itm

                    try:
                        self.block.render(context, buffer)
                    except ContinueLoop:
                        continue
                    except BreakLoop:
                        break

        elif self.default:
            self.default.render(context, buffer)


class BreakNode(ast.Node):
    __slots__ = ("tok",)

    def __init__(self, tok: Token):
        self.tok = tok

    def __str__(self) -> str:
        return "`break`"

    def render_to_output(self, context: Context, buffer: TextIO):
        raise BreakLoop("break")


class ContinueNode(ast.Node):
    __slots__ = ("tok",)

    def __init__(self, tok: Token):
        self.tok = tok

    def __str__(self) -> str:
        return "`continue`"

    def render_to_output(self, context: Context, buffer: TextIO):
        raise ContinueLoop("continue")


class ForTag(Tag):
    """Loop over items in an array, pairs of items in a hash, or integers in a range.

    For loop blocks share scope with their document. So assigning to a variable inside
    a for loop will add to the document's "local" namespace and persist after the loop
    has finished.

    To support nested loops and to remove "forloop" helpers, after each loop has finished,
    we push a "ForLoopDrop" to the context scope, then pop it after.
    """

    name = TAG_FOR
    end = TAG_ENDFOR

    def parse(self, stream: TokenStream) -> ast.Node:
        parser = get_parser(self.env)

        expect(stream, TOKEN_TAG_NAME, value=TAG_FOR)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_iter = tokenize_loop_expression(stream.current.value)
        expr = parse_loop_expression(TokenStream(expr_iter))

        tag = ForNode(tok, expression=expr)
        stream.next_token()

        tag.block = parser.parse_block(stream, ENDFORBLOCK)

        if stream.current.istag(TAG_ELSE):
            stream.next_token()
            tag.default = parser.parse_block(stream, ENDFORELSEBLOCK)

        expect(stream, TOKEN_TAG_NAME, value=TAG_ENDFOR)
        return tag


class BreakTag(Tag):

    name = TAG_BREAK
    block = False

    def parse(self, stream: TokenStream) -> BreakNode:
        expect(stream, TOKEN_TAG_NAME, value=TAG_BREAK)
        return BreakNode(stream.current)


class ContinueTag(Tag):

    name = TAG_CONTINUE
    block = False

    def parse(self, stream: TokenStream) -> ContinueNode:
        expect(stream, TOKEN_TAG_NAME, value=TAG_CONTINUE)
        return ContinueNode(stream.current)
