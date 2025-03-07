import os

import pytest
from mock import patch

from liquid import Mode
from liquid import Template
from liquid.exceptions import LiquidValueError
from liquid.limits import MAX_STR_INT
from liquid.limits import _init_int_max_str_digits


def test_parse_long_integer_literal() -> None:
    """Test that we honour the maximum str to int length on integer literals."""
    Template("".join(["{{", "1" * MAX_STR_INT, " }}"]))

    with pytest.raises(LiquidValueError):
        Template("".join(["{{", "1" * (MAX_STR_INT + 1), " }}"]))


def test_math_filter_long_string_literal() -> None:
    """Test that we honour the maximum str to int length on string literals."""
    template = Template("".join(["{{ '", "1" * MAX_STR_INT, "' | abs }}"]))
    assert template.render() == "1" * MAX_STR_INT

    template = Template(
        "".join(["{{ '", "1" * (MAX_STR_INT + 1), "' | abs }}"]),
        tolerance=Mode.STRICT,
    )

    with pytest.raises(LiquidValueError):
        assert template.render() == "1" * (MAX_STR_INT + 1)


@patch.dict(os.environ, {"LIQUIDINTMAXSTRDIGITS": "hello"})
def test_liquid_max_not_digit() -> None:
    """Test that we handle liquid environment variables that not digits."""
    with pytest.raises(TypeError):
        _init_int_max_str_digits()


@patch.dict(os.environ, {"LIQUIDINTMAXSTRDIGITS": "5"})
def test_max_digits_too_small() -> None:
    """Test that we handle environment variables that are too small."""
    with pytest.raises(ValueError, match="invalid limit"):
        _init_int_max_str_digits()


@patch.dict(os.environ, {"LIQUIDINTMAXSTRDIGITS": "1000"})
def test_set_liquid_max() -> None:
    """Test that we can set LIQUIDINTMAXSTRDIGITS."""
    assert _init_int_max_str_digits() == 1000


@patch.dict(os.environ, {"LIQUIDINTMAXSTRDIGITS": "0"})
def test_zero_is_ok() -> None:
    """Test that zero is OK."""
    assert _init_int_max_str_digits() == 0
