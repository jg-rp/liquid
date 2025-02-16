"""Golden test case definition."""

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass
class Case:
    """Test case dataclass to help with table driven tests."""

    description: str
    template: str
    expect: str
    globals: dict[str, Any] = field(default_factory=dict)  # noqa: A003
    partials: dict[str, Any] = field(default_factory=dict)
    standard: bool = True
    error: bool = False
    strict: bool = False
    future: bool = False


TEMPLATE_DROP_ATTRS = (
    r"{{ template }} "
    r"{{ template.directory }} "
    r"{{ template.name }} "
    r"{{ template.suffix }}"
)
