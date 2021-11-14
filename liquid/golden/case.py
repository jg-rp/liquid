from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Mapping


@dataclass
class Case:
    """Test case dataclass to help with table driven tests."""

    description: str
    template: str
    expect: str
    globals: Mapping[str, Any] = field(default_factory=dict)
    partials: Mapping[str, Any] = field(default_factory=dict)
    standard: bool = True


TEMPLATE_DROP_ATTRS = (
    r"{{ template }} "
    r"{{ template.directory }} "
    r"{{ template.name }} "
    r"{{ template.suffix }}"
)
