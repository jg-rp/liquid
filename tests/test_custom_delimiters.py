import pytest

from liquid import Environment, ExtendedLexer, ExtendedParser


class MockTokenizer(ExtendedLexer):
    comment_start: str = "[#"
    comment_end: str = "#]"

    out_start: str = "[["
    out_end: str = "]]"

    tag_start: str = "[%"
    tag_end: str = "%]"


@pytest.mark.parametrize(
    "source,data,want",
    [
        ("Hello, [[ you ]]!", {"you": "World"}, "Hello, World!"),
        ("[% if false %]FALSE[% else %]TRUE[% endif %]", {}, "TRUE"),
        ("Hello, {{ hi }}\n[[- you ]]!", {"you": "World"}, "Hello, {{ hi }}World!"),
        ("Hello, [# comment #] [[ you ]]!", {"you": "World"}, "Hello,  World!"),
    ],
)
def test_custom_delimiters(source: str, data: dict[str, object], want: str) -> None:
    assert Environment(tokenizer=MockTokenizer).render(source, data) == want
    assert (
        Environment(
            parser=ExtendedParser,
            tokenizer=MockTokenizer,
        ).render(source, data)
        == want
    )


class AnotherMockTokenizer(ExtendedLexer):
    comment_start: str = "[(#"
    comment_end: str = "#)]"

    out_start: str = "[[("
    out_end: str = ")]]"

    tag_start: str = "[(%"
    tag_end: str = "%)]"


@pytest.mark.parametrize(
    "source,data,want",
    [
        ("Hello, [[( you )]]!", {"you": "World"}, "Hello, World!"),
        ("[(% if false %)]FALSE[(% else %)]TRUE[(% endif %)]", {}, "TRUE"),
        ("Hello, {{ hi }}\n[[(- you )]]!", {"you": "World"}, "Hello, {{ hi }}World!"),
        ("Hello, [(# comment #)] [[( you )]]!", {"you": "World"}, "Hello,  World!"),
    ],
)
def test_longer_custom_delimiters(
    source: str, data: dict[str, object], want: str
) -> None:
    assert Environment(tokenizer=AnotherMockTokenizer).render(source, data) == want
    assert (
        Environment(
            parser=ExtendedParser,
            tokenizer=AnotherMockTokenizer,
        ).render(source, data)
        == want
    )
