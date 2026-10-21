from liquid import (
    AbstractTag,
    Block,
    Environment,
    Markup,
    Parser,
    RenderContext,
    StringBuffer,
    Token,
    render_block,
    render_block_async,
)


class MockTag(AbstractTag):
    tag = "mock"
    blank = False

    def __init__(self, token: Token, expr: str, block: Block) -> None:
        self.token = token
        self.expr = expr
        self.block = block

    @classmethod
    def parse(cls, token: Token, parser: Parser) -> Markup:
        expr = parser.raw_expression()
        block = parser.parse_block(end=("endmock",))
        parser.eat_empty_tag("endmock")
        return MockTag(token, expr, block)

    def render(self, context: RenderContext, buffer: StringBuffer) -> None:
        buffer.write(repr(self.expr))
        render_block(self.block, context, buffer)

    async def render_async(self, context: RenderContext, buffer: StringBuffer) -> None:
        buffer.write(repr(self.expr))
        await render_block_async(self.block, context, buffer)


def test_raw_expression() -> None:
    env = Environment()
    env.tags["mock"] = MockTag

    source = "Hello, {% mock 1+2 %} {{ you }}{% endmock %}!"
    assert env.render(source, {"you": "World"}) == "Hello, '1+2' World!"


def test_raw_expression_whitespace_control() -> None:
    env = Environment()
    env.tags["mock"] = MockTag

    source = "Hello, {% mock 1+2 -%} {{ you }}{% endmock %}!"
    assert env.render(source, {"you": "World"}) == "Hello, '1+2'World!"
