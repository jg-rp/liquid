"""Utilities for working with strings of HTML."""

from html.parser import HTMLParser

from typing import List


class StripParser(HTMLParser):  # pylint: disable=abstract-method
    """An HTML parser that strips out tags."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.reset()
        self.dat: List[str] = []

    def handle_data(self, data: str) -> None:
        self.dat.append(data)

    def handle_entityref(self, name: str) -> None:
        self.dat.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.dat.append(f"&#{name};")

    def get_data(self) -> str:
        return "".join(self.dat)


def strip_tags(value: str) -> str:
    """Return the given value with all HTML tags removed."""
    if "<" in value and ">" in value:
        parser = StripParser()
        parser.feed(value)
        parser.close()
        return parser.get_data()
    return value
