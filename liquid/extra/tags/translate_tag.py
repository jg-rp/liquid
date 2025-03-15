"""Tag and node definition for the "trans" or "translate" tag."""

from __future__ import annotations

import re
from gettext import NullTranslations
from typing import TYPE_CHECKING
from typing import Iterable
from typing import NamedTuple
from typing import Optional
from typing import TextIO
from typing import cast

from markupsafe import Markup

from liquid.ast import BlockNode
from liquid.ast import Node
from liquid.builtin.content import ContentNode
from liquid.builtin.expressions import FilteredExpression
from liquid.builtin.expressions import Identifier
from liquid.builtin.expressions import KeywordArgument
from liquid.builtin.expressions import Path
from liquid.builtin.expressions import StringLiteral
from liquid.builtin.output import OutputNode
from liquid.exceptions import TranslationSyntaxError
from liquid.limits import to_int
from liquid.messages import MESSAGES
from liquid.messages import MessageText
from liquid.messages import TranslatableTag
from liquid.messages import Translations
from liquid.messages import line_number
from liquid.parser import get_parser
from liquid.stringify import to_liquid_string
from liquid.tag import Tag
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TAG

if TYPE_CHECKING:
    from liquid import Expression
    from liquid import RenderContext
    from liquid import TokenStream
    from liquid.token import Token


class TranslateNode(Node, TranslatableTag):
    """The built-in _translate_ tag node."""

    __slots__ = (
        "args",
        "singular_block",
        "plural_block",
    )

    default_translations = NullTranslations()
    translations_var = "translations"
    message_count_var = "count"
    message_context_var = "context"
    re_vars = re.compile(r"(?<!%)%\((\w+)\)s")

    def __init__(
        self,
        token: Token,
        *,
        args: dict[str, KeywordArgument],
        singular_block: MessageBlock,
        plural_block: Optional[MessageBlock],
    ):
        super().__init__(token)
        self.args = args
        self.singular_block = singular_block
        self.plural_block = plural_block
        self.blank = False

    def __str__(self) -> str:
        args = (
            " " + ", ".join(str(arg) for arg in self.args.values()) if self.args else ""
        )
        plural = ""

        if self.plural_block:
            plural = f"{{% plural %}}{self.plural_block.block}"

        return (
            f"{{% translate{args} %}}"
            f"{self.singular_block.block}"
            f"{plural}"
            f"{{% endtranslate %}}"
        )

    def render_to_output(self, context: RenderContext, buffer: TextIO) -> int:
        """Render the node to the output buffer."""
        translations = self.resolve_translations(context)
        namespace = {k: expr.value.evaluate(context) for k, expr in self.args.items()}
        count = self.resolve_count(context, namespace)
        message_context = self.resolve_message_context(context, namespace)

        message_text = self.gettext(
            translations,
            count=count,
            message_context=message_context,
        )

        with context.extend(namespace):
            return buffer.write(self._format_message(context, message_text))

    async def render_to_output_async(
        self, context: RenderContext, buffer: TextIO
    ) -> int:
        """Render the node to the output buffer."""
        translations = self.resolve_translations(context)
        namespace = {
            k: await expr.value.evaluate_async(context) for k, expr in self.args.items()
        }
        count = self.resolve_count(context, namespace)
        message_context = self.resolve_message_context(context, namespace)

        message_text = self.gettext(
            translations,
            count=count,
            message_context=message_context,
        )

        with context.extend(namespace):
            return buffer.write(self._format_message(context, message_text))

    def resolve_translations(self, context: RenderContext) -> Translations:
        """Return a translations object from the current render context."""
        return cast(
            Translations,
            context.resolve(self.translations_var, default=self.default_translations),
        )

    def resolve_count(
        self,
        context: RenderContext,  # noqa: ARG002
        block_scope: dict[str, object],
    ) -> Optional[int]:
        """Return a message count.

        Uses the current render context and/or the translation's block scope.
        """
        try:
            return to_int(block_scope.get(self.message_count_var, 1))  # defaults to 1
        except ValueError:
            return 1

    def resolve_message_context(
        self,
        context: RenderContext,  # noqa: ARG002
        block_scope: dict[str, object],
    ) -> Optional[str]:
        """Return the message context string.

        Uses the current render context and/or the translation block scope.
        """
        message_context = block_scope.pop(self.message_context_var, None)
        if message_context:
            return (
                str(message_context)
                if not isinstance(message_context, str)
                else message_context
            )  # Just in case we get a Markupsafe object.
        return None

    def gettext(
        self,
        translations: Translations,
        count: Optional[int],
        message_context: Optional[str],
    ) -> str:
        """Get translated text from the given translations object."""
        if self.plural_block and count:
            if message_context:
                return translations.npgettext(
                    message_context,
                    self.singular_block.text,
                    self.plural_block.text,
                    count,
                )

            return translations.ngettext(
                self.singular_block.text,
                self.plural_block.text,
                count,
            )

        if message_context:
            return translations.pgettext(message_context, self.singular_block.text)
        return translations.gettext(self.singular_block.text)

    def children(
        self,
        static_context: RenderContext,  # noqa: ARG002
        *,
        include_partials: bool = True,  # noqa: ARG002
    ) -> Iterable[Node]:
        """Return this node's children."""
        yield self.singular_block.block

        if self.plural_block:
            yield self.plural_block.block

    def block_scope(self) -> Iterable[Identifier]:
        """Return variables this node adds to the node's block scope."""
        yield from (Identifier(p.name, token=p.token) for p in self.args.values())

    def expressions(self) -> Iterable[Expression]:
        """Return this node's expressions."""
        yield from (arg.value for arg in self.args.values())

    def messages(self) -> Iterable[MessageText]:  # noqa: D102
        if not self.singular_block.block.nodes:
            return ()

        message_context = self.args.get(self.message_context_var)

        if self.plural_block:
            if message_context and isinstance(message_context.value, StringLiteral):
                funcname = "npgettext"
                message: MESSAGES = (
                    (message_context.value.value, "c"),
                    self.singular_block.text,
                    self.plural_block.text,
                )
            else:
                funcname = "ngettext"
                message = (
                    self.singular_block.text,
                    self.plural_block.text,
                )
        elif message_context and isinstance(message_context.value, StringLiteral):
            funcname = "pgettext"
            message = (
                (message_context.value.value, "c"),
                self.singular_block.text,
            )
        else:
            funcname = "gettext"
            message = (self.singular_block.text,)

        return (
            MessageText(
                lineno=line_number(self.token),
                funcname=funcname,
                message=message,
            ),
        )

    def _format_message(
        self,
        context: RenderContext,
        message_text: str,
    ) -> str:
        """Return the message string formatted with the given message variables."""
        autoescape = context.env.autoescape
        if autoescape:
            message_text = Markup(message_text)

        _vars = {
            k: to_liquid_string(context.resolve(k), autoescape=autoescape)
            for k in self.re_vars.findall(message_text)
        }

        return message_text % _vars


class TranslateTag(Tag):
    """The built-in "translate" tag."""

    name = "translate"
    node_class = TranslateNode

    end = "endtranslate"
    plural_name = "plural"

    re_whitespace = re.compile(r"\s*\n\s*")

    # Override this to disable argument-less filters in translation expression
    # arguments.
    simple_filters = True

    # Override this to disable message whitespace normalization.
    trim_messages = True

    def parse(self, stream: TokenStream) -> TranslateNode:
        """Parse tokens from _stream_ into an AST node."""
        token = stream.eat(TOKEN_TAG)

        if stream.current.kind == TOKEN_EXPRESSION:
            args = {
                arg.name: arg
                for arg in KeywordArgument.parse(self.env, stream.into_inner(tag=token))
            }
        else:
            args = {}

        parse_block = get_parser(self.env).parse_block

        message_block = self.validate_message_block(
            parse_block(stream, end=(self.end, self.plural_name))
        )
        assert message_block

        if (
            stream.current.kind == TOKEN_TAG
            and stream.current.value == self.plural_name
        ):
            next(stream)
            plural_block = self.validate_message_block(
                parse_block(stream, end=(self.end,))
            )
        else:
            plural_block = None

        stream.expect(TOKEN_TAG, self.end)

        return self.node_class(
            token,
            args=args,
            singular_block=message_block,
            plural_block=plural_block,
        )

    def validate_message_block(
        self, block: Optional[BlockNode]
    ) -> Optional[MessageBlock]:
        """Check that a translation message block does not contain disallowed markup."""
        if not block:
            return None

        message_text: list[str] = []
        message_vars: list[str] = []

        for node in block.nodes:
            if isinstance(node, ContentNode):
                message_text.append(node.text.replace("%", "%%"))
            elif isinstance(node, OutputNode) and isinstance(
                node.expression, FilteredExpression
            ):
                expr = node.expression.left

                if not isinstance(expr, Path):
                    raise TranslationSyntaxError(
                        f"expected a translation variable, found '{expr}'",
                        token=node.token,
                    )

                if len(expr.path) > 1:
                    raise TranslationSyntaxError(
                        f"unexpected property access on translation variable '{expr}'",
                        token=node.token,
                    )

                var = expr.head()

                if node.expression.filters:
                    raise TranslationSyntaxError(
                        f"unexpected filter on translation variable '{expr}'",
                        token=node.token,
                    )

                if not isinstance(var, str):
                    raise TranslationSyntaxError(
                        f"expected a translation variable, found '{expr}'",
                        token=node.token,
                    )

                message_text.append(f"%({var})s")
                message_vars.append(var)
            else:
                raise TranslationSyntaxError(
                    "unexpected tag in translation text",
                    token=node.token,
                )

        msg = "".join(message_text)
        if self.trim_messages:
            msg = self.re_whitespace.sub(" ", msg.strip())

        return MessageBlock(block, msg, message_vars)


class MessageBlock(NamedTuple):
    """The AST block, text and placeholder variables representing a message block."""

    block: BlockNode
    text: str
    vars: list[str]  # noqa: A003
