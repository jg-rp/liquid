from .tokens import Token, token_value


class LiquidError(Exception):
    pass


class DetailedLiquidError(LiquidError):
    """A Liquid exception with contextual information."""

    def __init__(self, msg: str, *, token: Token, source: str, name: str) -> None:
        super().__init__(msg)
        self.token = token
        self.source = source
        self.name = name

    def __str__(self) -> str:
        return self.detailed_message()

    def detailed_message(self) -> str:
        """Return an error message formatted with extra context info."""
        span = token_value(self.token, self.source)
        line, col, current_line = self._error_context(self.source, self.token[1])

        pad = " " * len(str(line))
        length = len(span)
        pointer = (" " * col) + ("^" * max(length, 1))

        return (
            f"{self.message}\n"
            f"{pad} -> {self.name!r} {line}:{col}\n"
            f"{pad} |\n"
            f"{line} | {current_line}\n"
            f"{pad} | {pointer} {self.message}\n"
        )

    @property
    def message(self) -> object:
        """The exception's error message if one was given."""
        if self.args:
            return self.args[0]
        return None

    def _error_context(self, source: str, index: int) -> tuple[int, int, str]:
        lines = source.splitlines(keepends=True)
        cumulative_length = 0
        target_line_index = -1

        for i, line in enumerate(lines):
            cumulative_length += len(line)
            if index < cumulative_length:
                target_line_index = i
                break

        if target_line_index == -1:
            # Point to end of input
            return len(lines), len(lines[-1]), lines[-1].rstrip()

        # Line number (1-based)
        line_number = target_line_index + 1
        # Column number within the line
        column_number = index - (cumulative_length - len(lines[target_line_index]))

        current_line = lines[target_line_index].rstrip()
        return line_number, column_number, current_line


class LiquidSyntaxError(DetailedLiquidError):
    pass


class LiquidNameError(DetailedLiquidError):
    pass
