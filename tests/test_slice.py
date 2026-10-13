from collections.abc import Sequence

import pytest

from liquid._slice import slice_range, slice_sequence


@pytest.mark.parametrize(
    "it,offset,limit,want",
    [
        (range(0, 10), 0, None, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        (range(0, 10), 2, 5, [2, 3, 4, 5, 6]),
        (range(0, 10), 5, 2, [5, 6]),
        (range(0, 10), -2, 3, [0]),
        (range(0, 10), 1, -2, []),
        (range(0, 10), -2, -1, []),
        (range(0, 10), -5, -2, []),
        (range(-5, -1), 0, None, [-5, -4, -3, -2, -1]),
        (range(-5, 3), 0, None, [-5, -4, -3, -2, -1, 0, 1, 2, 3]),
        (range(-5, 3), 2, 2, [-3, -2]),
        (range(-5, 3), 2, -1, []),
        (range(1, 6), 2, 4, [3, 4, 5, 6]),
    ],
)
def test_dodgy_slice(
    it: range, offset: int, limit: int | None, want: list[int]
) -> None:
    assert list(slice_range(it, offset, limit)) == want


@pytest.mark.parametrize(
    "it,offset,limit,want",
    [
        (list(range(0, 11)), 0, None, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        (list(range(0, 12)), 2, 5, [2, 3, 4, 5, 6]),
        (list(range(0, 13)), 5, 2, [5, 6]),
        (list(range(0, 14)), -2, 3, [0]),
        (list(range(0, 15)), 1, -2, []),
        (list(range(0, 16)), -2, -1, []),
        (list(range(0, 17)), -5, -2, []),
        (list(range(-5, 0)), 0, None, [-5, -4, -3, -2, -1]),
        (list(range(-5, 4)), 0, None, [-5, -4, -3, -2, -1, 0, 1, 2, 3]),
        (list(range(-5, 4)), 2, 2, [-3, -2]),
        (list(range(-5, 4)), 2, -1, []),
        (list(range(1, 7)), 2, 4, [3, 4, 5, 6]),
        (["a", "b", "c", "d", "e", "f", "g", "h"], 2, 5, ["c", "d", "e", "f", "g"]),
    ],
)
def test_dodgy_slice_sequence(
    it: Sequence[object], offset: int, limit: int | None, want: list[int]
) -> None:
    it_, length = slice_sequence(it, offset, limit)
    assert list(it_) == want
    assert length == len(want)
