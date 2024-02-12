"""An environment that's configured for maximum compatibility with Shopify/Liquid.

This environment will be updated without concern for backwards incompatible changes to
template rendering behavior.
"""
from ..environment import Environment as DefaultEnvironment
from ..template import FutureBoundTemplate
from .filters import split
from .tags import LaxIfTag
from .tags import LaxUnlessTag


class Environment(DefaultEnvironment):
    """An environment that's configured for maximum compatibility with Shopify/Liquid.

    This environment addresses some compatibility issues between Python Liquid's default
    `Environment` and Shopify/Liquid. These issues are considered to be an unacceptable
    breaking changes for users that rely on existing behavior of the default
    environment.

    See https://jg-rp.github.io/liquid/known_issues
    """

    template_class = FutureBoundTemplate

    def setup_tags_and_filters(self) -> None:
        """Add future tags and filters to this environment."""
        super().setup_tags_and_filters()
        self.add_filter("split", split)
        self.add_tag(LaxIfTag)
        self.add_tag(LaxUnlessTag)
