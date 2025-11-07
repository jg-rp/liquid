import operator
import sys
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from typing import Any
from typing import Hashable
from typing import Optional

import pytest
import yaml

from liquid import DictLoader
from liquid import Environment
from liquid.exceptions import LiquidError


class LiquidSpecLoader(yaml.SafeLoader):
    """A YAML loader that handles and flags `!ruby` tags."""

    def __init__(self, stream: Any):
        super().__init__(stream)
        self.depth_ = -1
        self.current_root_item_: dict[Hashable, Any] = {}


def yaml_ruby_tag_handler(
    loader: LiquidSpecLoader, tag_suffix: str, node: yaml.Node
) -> dict[str, Any]:
    """Handle `!ruby` tag.s."""
    if isinstance(node, yaml.MappingNode):
        _data = loader.construct_mapping(node)
    elif isinstance(node, yaml.SequenceNode):
        _data = loader.construct_sequence(node)
    else:
        assert isinstance(node, yaml.ScalarNode)
        _data = loader.construct_scalar(node)

    loader.current_root_item_["skip"] = True

    return {
        "__ruby_tag__": tag_suffix,
        "__ruby_skip__": True,
        "value": _data,
    }


def yaml_mapping_constructor(
    loader: LiquidSpecLoader,
    node: yaml.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    """Handle test cases with unhashable keys."""
    m: dict[Hashable, Any] = {}

    if loader.depth_ == 0:
        loader.current_root_item_ = m

    loader.depth_ += 1

    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)  # type: ignore

        try:
            value = loader.construct_object(value_node, deep=deep)  # type: ignore
        except yaml.constructor.ConstructorError:
            loader.current_root_item_["skip"] = True
            loader.depth_ -= 1
            return {}

        try:
            m[key] = value
        except TypeError:
            loader.current_root_item_["skip"] = True
            loader.depth_ -= 1
            return {}

    loader.depth_ -= 1
    return m


def yaml_sequence_constructor(
    loader: LiquidSpecLoader, node: yaml.SequenceNode, deep: bool = False
) -> list[Any]:
    """Track top-level sequence items for skipping."""
    loader.depth_ += 1
    seq = loader.construct_sequence(node, deep=deep)
    loader.depth_ -= 1
    return seq


LiquidSpecLoader.add_multi_constructor("!ruby/", yaml_ruby_tag_handler)  # type: ignore
LiquidSpecLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, yaml_mapping_constructor
)
LiquidSpecLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG, yaml_sequence_constructor
)


@dataclass()
class Unit:
    name: str
    expected: str
    template: str
    template_name: Optional[str] = None
    environment: dict[str, Any] = field(default_factory=dict[str, Any])
    filesystem: dict[str, str] = field(default_factory=dict[str, str])
    error_mode: str = ""
    skip: bool = False


def spec_cases() -> list[Unit]:
    try:
        with open(
            "tests/liquid-spec/specs/liquid_ruby/specs.yml", encoding="utf8"
        ) as fd:
            data = yaml.load(fd, Loader=LiquidSpecLoader)  # noqa: S506
    except FileNotFoundError:
        sys.stderr.write(
            "Did you forget to initialize submodules? `git submodule update --init`"
        )
        raise

    keys = [f.name for f in fields(Unit)]
    return [Unit(**{k: case[k] for k in keys if k in case}) for case in data]


def manual_cases() -> list[Unit]:
    try:
        with open(
            "tests/liquid-spec/specs/liquid_ruby/manual.yml", encoding="utf8"
        ) as fd:
            data = yaml.load(fd, Loader=LiquidSpecLoader)  # noqa: S506
    except FileNotFoundError:
        sys.stderr.write(
            "Did you forget to initialize submodules? `git submodule update --init`"
        )
        raise

    keys = [f.name for f in fields(Unit)]
    return [Unit(**{k: case[k] for k in keys if k in case}) for case in data]


@pytest.mark.parametrize("case", spec_cases(), ids=operator.attrgetter("name"))
def test_spec(case: Unit) -> None:
    if case.skip:
        pytest.skip(reason="unloadable")

    env = Environment(loader=DictLoader(case.filesystem))

    if "Liquid error " in case.expected:
        with pytest.raises(LiquidError):
            env.from_string(case.template).render(**case.filesystem)
    else:
        assert (
            env.from_string(case.template).render(**case.environment) == case.expected
        )


@pytest.mark.parametrize("case", manual_cases(), ids=operator.attrgetter("name"))
def test_spec_manual(case: Unit) -> None:
    if case.skip:
        pytest.skip(reason="unloadable")

    env = Environment(loader=DictLoader(case.filesystem))

    if "Liquid error " in case.expected:
        with pytest.raises(LiquidError):
            env.from_string(case.template).render(**case.filesystem)
    else:
        assert (
            env.from_string(case.template).render(**case.environment) == case.expected
        )
