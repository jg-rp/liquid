"""Parse tree node and tag definition for the built in "if" tag."""

import sys
from typing import Optional, List, TextIO

from liquid.token import (
    Token,
    TOKEN_EOF,
    TOKEN_TAG_NAME,
    TOKEN_EXPRESSION,
)
from liquid.parse import expect, parse_boolean_expression, get_parser, eat_block
from liquid import ast
from liquid.tag import Tag
from liquid.context import Context
from liquid.lex import TokenStream
from liquid.expression import Expression
from liquid.exceptions import LiquidSyntaxError
from liquid.builtin.illegal import IllegalNode
from liquid.code import Opcode
from liquid.compiler import Compiler

TAG_IF = sys.intern("if")
TAG_ENDIF = sys.intern("endif")
TAG_ELSIF = sys.intern("elsif")
TAG_ELSE = sys.intern("else")

ENDIFBLOCK = (TAG_ENDIF, TAG_ELSIF, TAG_ELSE, TOKEN_EOF)
ENDELSIFBLOCK = (TAG_ENDIF, TAG_ELSIF, TAG_ELSE)
ENDIFELSEBLOCK = (TAG_ENDIF,)


class IfNode(ast.Node):
    """Parse tree node for "if" block tags."""

    __slots__ = (
        "tok",
        "condition",
        "consequence",
        "conditional_alternatives",
        "alternative",
    )

    def __init__(
        self,
        tok: Token,
        condition: Expression,
        consequence: Optional[ast.BlockNode] = None,
        conditional_alternatives: List[ast.ConditionalBlockNode] = None,
        alternative: Optional[ast.BlockNode] = None,
    ):
        self.tok = tok
        self.condition = condition
        self.consequence = consequence
        self.conditional_alternatives = conditional_alternatives or []
        self.alternative = alternative

    def __str__(self) -> str:
        buf = [
            f"if {self.condition} {{ {self.consequence} }}",
        ]

        for alt in self.conditional_alternatives:
            buf.append(f"elsif {alt}")

        if self.alternative:
            buf.append(f"else {{ {self.alternative} }}")
        return " ".join(buf)

    def __repr__(self):  # pragma: no cover
        return f"IfNode(tok={self.tok}, condition='{self.condition}')"

    def render_to_output(self, context: Context, buffer: TextIO):
        if self.condition.evaluate(context):
            self.consequence.render(context, buffer)
        else:
            rendered = False
            for alt in self.conditional_alternatives:
                if alt.render(context, buffer):
                    rendered = True
                    break

            if not rendered and self.alternative:
                self.alternative.render(context, buffer)

    def compile_node(self, compiler: Compiler):
        # A list of jump instruction positions at the end of each conditional block.
        # Each one of them needs to be updated with the position of just after the
        # final alternative block, which we can do until we've compiled all conditions
        # and blocks.
        jump_positions = []

        self.condition.compile(compiler)
        jump_if_not_position = compiler.emit(Opcode.JIN, 9999)
        self.consequence.compile(compiler)

        if compiler.last_instruction_is(Opcode.POP):
            compiler.remove_last_pop()

        jump_positions.append(compiler.emit(Opcode.JMP, 9999))

        after_consequence_pos = len(compiler.current_instructions())
        compiler.change_operand(jump_if_not_position, after_consequence_pos)

        # Repeat what we've just done for the condition and consequence, but for
        # each alternative condition and block.
        for alt in self.conditional_alternatives:
            alt.condition.compile(compiler)
            jump_if_not_position = compiler.emit(Opcode.JIN, 9999)
            alt.block.compile(compiler)

            if compiler.last_instruction_is(Opcode.POP):
                compiler.remove_last_pop()

            jump_positions.append(compiler.emit(Opcode.JMP, 9999))

            after_conditional_alternative_pos = len(compiler.current_instructions())
            compiler.change_operand(
                jump_if_not_position, after_conditional_alternative_pos
            )

        # Emit a dummy alternative if one was not given.
        if not self.alternative:
            compiler.emit(Opcode.NOP)
        else:
            self.alternative.compile(compiler)

            if compiler.last_instruction_is(Opcode.POP):
                compiler.remove_last_pop()

        # Update all jump instruction operands with this position.
        after_alternative_pos = len(compiler.current_instructions())
        for pos in jump_positions:
            compiler.change_operand(pos, after_alternative_pos)


class IfTag(Tag):
    """"""

    name = TAG_IF
    end = TAG_ENDIF

    def parse(self, stream: TokenStream) -> ast.Node:
        parser = get_parser(self.env)

        expect(stream, TOKEN_TAG_NAME, value=TAG_IF)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_iter = self.expr_lexer.tokenize(stream.current.value)

        # If the expression can't be parsed, eat the whole "if" tag, including
        # any alternatives. See `Tag.get_node`.
        expr = parse_boolean_expression(expr_iter)

        node = IfNode(tok, expr)
        stream.next_token()

        node.consequence = parser.parse_block(stream, ENDIFBLOCK)

        while stream.current.istag(TAG_ELSIF):
            stream.next_token()
            expect(stream, TOKEN_EXPRESSION)

            expr_iter = self.expr_lexer.tokenize(stream.current.value)

            # If the expression can't be parsed, eat the "elsif" block and
            # continue to parse more "elsif" expression, if any.
            try:
                expr = parse_boolean_expression(expr_iter)
            except LiquidSyntaxError as err:
                self.env.error(err)
                eat_block(stream, ENDELSIFBLOCK)
                return IllegalNode(node.tok)

            alt = ast.ConditionalBlockNode(
                stream.current,
                condition=expr,
            )
            stream.next_token()
            alt.block = parser.parse_block(stream, ENDELSIFBLOCK)
            node.conditional_alternatives.append(alt)

        if stream.current.istag(TAG_ELSE):
            stream.next_token()
            node.alternative = parser.parse_block(stream, ENDIFELSEBLOCK)

        expect(stream, TOKEN_TAG_NAME, value=TAG_ENDIF)
        return node
