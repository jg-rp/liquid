from liquid.builtin.expressions import Path
from liquid.token import TOKEN_WORD
from liquid.token import Token


def test_simple_variable() -> None:
    """Test that we can represent a simple variable as a tuple."""
    mock_token = Token(TOKEN_WORD, "", 0, "")
    path = Path(mock_token, ["some"])
    assert path.location() == ("some",)


def test_dotted_variable() -> None:
    """Test that we can represent a dotted variable as a tuple."""
    mock_token = Token(TOKEN_WORD, "", 0, "")
    path = Path(mock_token, ["some", "thing"])
    assert path.location() == ("some", "thing")


def test_bracketed_variable() -> None:
    """Test that we can represent a bracketed variable as a tuple."""
    mock_token = Token(TOKEN_WORD, "", 0, "")
    path = Path(mock_token, ["some", "other.thing"])
    assert path.location() == ("some", "other.thing")


def test_nested_variable() -> None:
    """Test that we can represent nested variables as a tuple."""
    mock_token = Token(TOKEN_WORD, "", 0, "")
    path = Path(
        mock_token,
        [
            "some",
            Path(mock_token, ["foo", "bar", Path(mock_token, ["a", "b"])]),
            "other.thing",
        ],
    )
    assert path.location() == ("some", ("foo", "bar", ("a", "b")), "other.thing")
