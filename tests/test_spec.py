import operator
import sys
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import Hashable
from typing import Iterable
from typing import Optional
from typing import cast

import pytest
import yaml

from liquid import DictLoader
from liquid import Environment
from liquid.exceptions import LiquidError


class LiquidSpecLoader(yaml.SafeLoader):
    """A YAML loader that handles and flags `!binary` tags."""

    def __init__(self, stream: Any):
        super().__init__(stream)
        self.depth_ = -1
        self.current_root_item_: dict[Hashable, Any] = {}


def yaml_binary_tag_handler(
    loader: LiquidSpecLoader, node: yaml.Node
) -> dict[str, Any]:
    """Handle `!binary` tags."""
    if isinstance(node, yaml.MappingNode):
        _data = loader.construct_mapping(node)
    elif isinstance(node, yaml.SequenceNode):
        _data = loader.construct_sequence(node)
    else:
        assert isinstance(node, yaml.ScalarNode)  # noqa: S101
        _data = loader.construct_scalar(node)

    loader.current_root_item_["__skip__"] = True
    loader.current_root_item_["__skip_reason__"] = "binary data"

    return {
        "__skip__": True,
        "value": _data,
    }


def yaml_mapping_constructor(
    loader: LiquidSpecLoader,
    node: yaml.MappingNode,
    deep: bool = False,  # noqa: FBT001, FBT002
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
        except yaml.constructor.ConstructorError as err:
            loader.current_root_item_["__skip__"] = True
            loader.current_root_item_["__skip_reason__"] = str(err)
            loader.depth_ -= 1
            return {}

        try:
            m[key] = value
        except TypeError as err:
            loader.current_root_item_["__skip__"] = True
            loader.current_root_item_["__skip_reason__"] = str(err)
            loader.depth_ -= 1
            return {}

    loader.depth_ -= 1
    return m


def yaml_sequence_constructor(
    loader: LiquidSpecLoader,
    node: yaml.SequenceNode,
    deep: bool = False,  # noqa: FBT001, FBT002
) -> list[Any]:
    """Track top-level sequence items for skipping."""
    loader.depth_ += 1
    seq = loader.construct_sequence(node, deep=deep)
    loader.depth_ -= 1
    return seq


def configure_yaml_loader() -> None:
    """Configure out Liquid spec YAML loader."""
    LiquidSpecLoader.add_constructor(  # type: ignore
        "!binary",
        yaml_binary_tag_handler,
    )

    LiquidSpecLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        yaml_mapping_constructor,
    )

    LiquidSpecLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG,
        yaml_sequence_constructor,
    )

    # Remove the implicit resolver for date, time and datetime.
    for ch, resolvers in list(LiquidSpecLoader.yaml_implicit_resolvers.items()):
        LiquidSpecLoader.yaml_implicit_resolvers[ch] = [
            (tag, regexp)
            for tag, regexp in resolvers
            if tag != "tag:yaml.org,2002:timestamp"
        ]


configure_yaml_loader()


@dataclass
class Case:
    """A single test case."""

    name: str
    template: str
    data: dict[str, object] = field(default_factory=dict)  # type: ignore
    templates: dict[str, Any] = field(default_factory=list)  # type: ignore
    result: Optional[str] = field(default=None)
    invalid: bool = field(default=False)
    skip: bool = field(default=False)
    skip_reason: Optional[str] = field(default=None)


def load_test_suite(path: Path) -> Iterable[Case]:
    """Load test cases from YAML files in `path`."""
    test_suite_files = [p for p in path.glob("**/*.yml") if p.name != "suite.yml"]

    try:
        with (path / "suite.yml").open() as fd:
            suite = yaml.safe_load(fd)
    except FileNotFoundError:
        sys.stderr.write(
            "Did you forget to initialize submodules? `git submodule update --init`"
        )
        raise

    test_suite_prefix = "_".join(suite["name"].lower().split())

    for test_file in sorted(test_suite_files):
        yield from load_test_suite_file(test_file, test_suite_prefix)


def load_test_suite_file(test_file: Path, suite_prefix: str) -> Iterable[Case]:
    """Load test cases from a single file in a test suite."""
    prefix = f"{suite_prefix}__{test_file.stem.replace('-', '_')}"

    with test_file.open() as fd:
        _test_cases = yaml.load(fd, Loader=LiquidSpecLoader)  # noqa: S506

    if isinstance(_test_cases, dict):
        test_cases = cast("list[dict[str, Any]]", _test_cases["specs"])
    else:
        # Some YAML files don't have a top-level mapping.
        test_cases = cast("list[dict[str, Any]]", _test_cases)

    for test_case in sorted(test_cases, key=operator.itemgetter("name")):
        test_case_name = f"{prefix}__{test_case['name']}"

        if "expected_pattern" in test_case:
            yield Case(
                name=test_case_name,
                template=test_case["template"],
                skip=True,
                skip_reason="expected patter",
            )

        elif "runtime_drops" in test_case.get("required_features", {}):
            yield Case(
                name=test_case_name,
                template=test_case["template"],
                skip=True,
                skip_reason="runtime drops",
            )

        if "__skip__" in test_case:
            yield Case(
                name=test_case_name,
                template=test_case["template"],
                skip=True,
                skip_reason=test_case["__skip_reason__"],
            )

        else:
            yield Case(
                name=test_case_name,
                template=test_case["template"],
                data=test_case.get("environment", {}),
                result=test_case.get("expected", None),
                templates=test_case.get("filesystem", {}),
                invalid=bool(test_case.get("errors", False)),
            )


def spec_cases() -> list[Case]:
    path = Path("tests/liquid-spec/specs/")

    test_suite_paths = [
        path / "basics/",
        path / "liquid_ruby/",
    ]

    test_suites: list[Case] = []

    for suite_path in test_suite_paths:
        test_suites.extend(load_test_suite(suite_path))

    return test_suites


@pytest.mark.parametrize("case", spec_cases(), ids=operator.attrgetter("name"))
def test_spec(case: Case) -> None:
    if case.skip:
        pytest.skip(reason=case.skip_reason or "unknown error")

    env = Environment(loader=DictLoader(case.templates or {}))

    if case.invalid:
        with pytest.raises(LiquidError):
            env.from_string(case.template).render(**case.data)
    else:
        assert env.from_string(case.template).render(**case.data) == case.result
