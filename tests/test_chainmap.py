from liquid.utils import ReadOnlyChainMap


def test_earlier_maps_take_priority() -> None:
    chain_map = ReadOnlyChainMap({"foo": 1}, {"foo": 2})
    assert chain_map.get("foo") == 1


def test_fall_back_to_later_maps() -> None:
    chain_map = ReadOnlyChainMap({"bar": 1}, {"foo": 2})
    assert chain_map.get("foo") == 2


def test_default_to_none() -> None:
    chain_map = ReadOnlyChainMap({"bar": 1}, {"bar": 2})
    assert chain_map.get("foo") is None


def test_iter() -> None:
    chain_map = ReadOnlyChainMap({"foo": 1}, {"bar": 2}, {"foo": 3})
    assert list(chain_map) == ["foo", "bar", "foo"]
