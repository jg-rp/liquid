"""The location of a variable, tag or filter in a template."""

from dataclasses import dataclass


@dataclass
class Span:
    """The location of a variable, tag or filter in a template."""

    template_name: str
    """The template name."""

    index: int
    """A start index into the template source text."""

    def line_col(self, source: str) -> tuple[int, int]:
        """Return a tuple of (line number, column number) for this span in _source_."""
        lines = source.splitlines(keepends=True)
        cumulative_length = 0
        target_line_index = -1

        for i, line in enumerate(lines):
            cumulative_length += len(line)
            if self.index < cumulative_length:
                target_line_index = i
                break

        if target_line_index == -1:
            raise ValueError("index is out of bounds for the given string")

        # Line number (1-based)
        line_number = target_line_index + 1
        # Column number within the line
        column_number = self.index - (cumulative_length - len(lines[target_line_index]))
        return line_number, column_number
