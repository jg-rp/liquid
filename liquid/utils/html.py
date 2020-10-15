"""Utilities for working with strings of HTML."""

from html.parser import HTMLParser


class StripParser(HTMLParser):
    """An HTML parser that strips out tags."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.reset()
        self.dat = []

    def handle_data(self, data):
        self.dat.append(data)

    def handle_entityref(self, name):
        self.dat.append(f"&{name};")

    def handle_charref(self, name):
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
