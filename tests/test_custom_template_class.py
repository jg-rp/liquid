"""Test Template and Context subclassing."""

from __future__ import annotations

import io
from typing import TYPE_CHECKING
from typing import Any
from typing import Optional

from liquid import Environment
from liquid import RenderContext
from liquid.template import BoundTemplate

if TYPE_CHECKING:
    from liquid import Token


def test_bound_template_subclass() -> None:
    """Test that we can use a subclass of BoundTemplate with an Environment."""

    class CustomTemplate(BoundTemplate):
        """Mock template subclass."""

    env = Environment()
    env.template_class = CustomTemplate

    template = env.from_string("Hello, {{ you }}!")
    assert isinstance(template, CustomTemplate)


def test_context_subclass() -> None:
    """Test that we can use a subclass of Context with an Environment."""

    class CustomContext(RenderContext):
        """Mock context subclass."""

        def __init__(
            self,
            template: BoundTemplate,
            *,
            globals: Optional[dict[str, object]] = None,  # noqa: A002
            disabled_tags: Optional[list[str]] = None,
            copy_depth: int = 0,
        ):
            super().__init__(
                template,
                globals=globals,
                disabled_tags=disabled_tags,
                copy_depth=copy_depth,
            )
            self.assign_counter = 0

        def assign(self, key: str, val: Any) -> None:
            self.assign_counter += 1
            return super().assign(key, val)

    class CustomTemplate(BoundTemplate):
        """Mock template subclass."""

        context_class = CustomContext

    env = Environment()
    env.template_class = CustomTemplate

    template = env.from_string("{% assign you = 'Brian' %}Hello, {{ you }}!")
    assert isinstance(template, CustomTemplate)

    buf = io.StringIO()
    ctx = CustomContext(template)
    template.render_with_context(ctx, buf)

    assert buf.getvalue() == "Hello, Brian!"
    assert ctx.assign_counter == 1


def test_capture_variables_from_context_subclass() -> None:
    """Test that we can capture a template's variables from a Context subclass."""
    _missing = object()

    class CustomContext(RenderContext):
        """Mock context subclass."""

        def __init__(
            self,
            template: BoundTemplate,
            *,
            globals: Optional[dict[str, object]] = None,  # noqa: A002
            disabled_tags: Optional[list[str]] = None,
            copy_depth: int = 0,
        ):
            super().__init__(
                template,
                globals=globals,
                disabled_tags=disabled_tags,
                copy_depth=copy_depth,
            )
            self.references: list[str] = []

        def get(
            self, path: list[object], token: Optional[Token], default: object = ...
        ) -> object:
            self._count_reference(path)
            return super().get(path, token=token, default=default)

        async def get_async(
            self, path: list[object], token: Optional[Token], default: object = ...
        ) -> object:
            self._count_reference(path)
            return await super().get_async(path, token=token, default=default)

        def resolve(
            self,
            name: str,
            token: Optional[Token] = None,
            default: object = _missing,
        ) -> Any:
            self._count_reference([name])
            return super().resolve(name, token=token, default=default)

        def _count_reference(self, path: list[object]) -> None:
            self.references.append(".".join(str(p) for p in path))

    class CustomTemplate(BoundTemplate):
        """Mock template subclass."""

        context_class = CustomContext

    env = Environment()
    env.template_class = CustomTemplate

    template = env.from_string("{% assign you = 'Brian' %}Hello, {{ you }}!")
    assert isinstance(template, CustomTemplate)

    buf = io.StringIO()
    ctx = CustomContext(template)
    template.render_with_context(ctx, buf)

    assert buf.getvalue() == "Hello, Brian!"
    assert ctx.references == ["you"]

    ctx.resolve("you")
    assert ctx.references == ["you", "you"]
