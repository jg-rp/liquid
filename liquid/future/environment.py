"""An environment that's configured for maximum compatibility with Shopify/Liquid.

This environment will be updated without concern for backwards incompatible changes to
template rendering behavior.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Type

from ..environment import Environment as DefaultEnvironment
from ..template import FutureBoundTemplate

if TYPE_CHECKING:
    from ..template import BoundTemplate


class Environment(DefaultEnvironment):
    """An environment that's configured for maximum compatibility with Shopify/Liquid.

    This environment addresses some compatibility issues between Python Liquid's default
    `Environment` and Shopify/Liquid. These issues are considered to be an unacceptable
    breaking changes for users that rely on existing behavior of the default
    environment.

    See https://jg-rp.github.io/liquid/known_issues
    """

    template_class: Type[BoundTemplate] = FutureBoundTemplate
