from liquid.builtin.filters.string import squish


def test_leading_trailing_and_inner_space() -> None:
    assert squish(" Hello    World!   ") == "Hello World!"


def test_leading_trailing_space() -> None:
    assert squish(" HelloWorld!   ") == "HelloWorld!"


def test_just_leading_space() -> None:
    assert squish("  HelloWorld!") == "HelloWorld!"


def test_just_trailing_space() -> None:
    assert squish("HelloWorld!   ") == "HelloWorld!"


def test_just_inner_space() -> None:
    assert squish("Hello   World!") == "Hello World!"


def test_leading_trailing_and_inner_whitespace() -> None:
    assert (
        squish(" \n\t\r\nHello  \n\t\r\n \n\t\r\n World!  \n\t\r\n") == "Hello World!"
    )


def test_null_input() -> None:
    assert squish(None) == ""


def test_empty_string() -> None:
    assert squish("") == ""


def test_just_whitespace() -> None:
    assert squish("  ") == ""
