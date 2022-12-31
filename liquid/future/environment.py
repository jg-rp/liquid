"""An environment that is configured for maximum compatibility with Ruby Liquid, without
concern for backwards incompatible changes to template rendering behavior."""
from ..environment import Environment as DefaultEnvironment
from ..template import FutureBoundTemplate


class Environment(DefaultEnvironment):
    """An environment that is configured for maximum compatibility with Ruby Liquid.

    This environment addresses some compatibility issues between Python Liquid's default
    :class:`Environment` and Ruby Liquid. These issues are considered to be an
    unacceptable breaking changes for users that rely on existing behavior of the
    default environment.

    See https://jg-rp.github.io/liquid/known_issues
    """

    template_class = FutureBoundTemplate
