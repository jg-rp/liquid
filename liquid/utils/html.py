"""Utilities for working with strings of HTML."""

from html.parser import HTMLParser

from typing import List
from typing import Tuple
from typing import Optional


class StripParser(HTMLParser):  # pylint: disable=abstract-method
    """An HTML parser that strips out tags."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.reset()
        self.script_depth = 0
        self.style_depth = 0
        self.dat: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag == "script":
            self.script_depth += 1
        elif tag == "style":
            self.style_depth += 1
        return super().handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.script_depth -= 1
        elif tag == "style":
            self.style_depth -= 1
        return super().handle_endtag(tag)

    def handle_data(self, data: str) -> None:
        if not self.script_depth and not self.style_depth:
            self.dat.append(data)

    def handle_entityref(self, name: str) -> None:
        if not self.script_depth and not self.style_depth:
            self.dat.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self.script_depth and not self.style_depth:
            self.dat.append(f"&#{name};")

    def get_data(self) -> str:
        """Return accumulated data."""
        return "".join(self.dat)


def strip_tags(value: str) -> str:
    """Return the given value with all HTML tags removed."""
    if "<" in value and ">" in value:
        parser = StripParser()
        parser.feed(value)
        parser.close()
        return parser.get_data()
    return value
