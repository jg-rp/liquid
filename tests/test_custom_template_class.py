"""Test Template and Context subclassing."""
import io
import unittest

from typing import Any
from typing import Optional
from typing import List

from liquid import Context
from liquid import Environment

from liquid.context import ContextPath
from liquid.context import Namespace

from liquid.template import BoundTemplate


class CustomTemplateClassTestCase(unittest.TestCase):
    """Test that we can customize the template class."""

    def test_bound_template_subclass(self):
        """Test that we can use a subclass of BoundTemplate with an Environment."""

        class CustomTemplate(BoundTemplate):
            """Mock template subclass"""

        env = Environment()
        env.template_class = CustomTemplate

        template = env.from_string("Hello, {{ you }}!")
        self.assertIsInstance(template, CustomTemplate)

    def test_context_subclass(self):
        """Test that we can use a subclass of Context with an Environment."""

        # pylint: disable=redefined-builtin
        class CustomContext(Context):
            """Mock context subclass"""

            def __init__(
                self,
                env: Environment,
                globals: Optional[Namespace] = None,
                disabled_tags: Optional[List[str]] = None,
                copy_depth: int = 0,
            ):
                super().__init__(env, globals, disabled_tags, copy_depth)
                self.assign_counter = 0

            def assign(self, key: str, val: Any) -> None:
                self.assign_counter += 1
                return super().assign(key, val)

        class CustomTemplate(BoundTemplate):
            """Mock template subclass"""

            context_class = CustomContext

        env = Environment()
        env.template_class = CustomTemplate

        template = env.from_string("{% assign you = 'Brian' %}Hello, {{ you }}!")
        self.assertIsInstance(template, CustomTemplate)

        buf = io.StringIO()
        ctx = CustomContext(env)
        template.render_with_context(ctx, buf)

        self.assertEqual(buf.getvalue(), "Hello, Brian!")
        self.assertEqual(ctx.assign_counter, 1)

    def test_capture_variables_from_context_subclass(self):
        """Test that we can capture a template's used variables from a Context subclass."""

        _missing = object()

        # pylint: disable=redefined-builtin
        class CustomContext(Context):
            """Mock context subclass"""

            def __init__(
                self,
                env: Environment,
                globals: Optional[Namespace] = None,
                disabled_tags: Optional[List[str]] = None,
                copy_depth: int = 0,
            ):
                super().__init__(env, globals, disabled_tags, copy_depth)
                self.references: List[str] = []

            def get(self, path: ContextPath, default: object = ...) -> object:
                self._count_reference(path)
                return super().get(path, default)

            async def get_async(
                self, path: ContextPath, default: object = ...
            ) -> object:
                self._count_reference(path)
                return await super().get_async(path, default)

            def resolve(self, name: str, default: object = _missing) -> Any:
                self._count_reference(name)
                return super().resolve(name, default)

            def _count_reference(self, path: ContextPath) -> None:
                if isinstance(path, str):
                    self.references.append(path)
                else:
                    self.references.append(".".join(str(p) for p in path))

        class CustomTemplate(BoundTemplate):
            """Mock template subclass"""

            context_class = CustomContext

        env = Environment()
        env.template_class = CustomTemplate

        template = env.from_string("{% assign you = 'Brian' %}Hello, {{ you }}!")
        self.assertIsInstance(template, CustomTemplate)

        buf = io.StringIO()
        ctx = CustomContext(env)
        template.render_with_context(ctx, buf)

        self.assertEqual(buf.getvalue(), "Hello, Brian!")
        self.assertEqual(ctx.references, ["you"])

        ctx.resolve("you")
        self.assertEqual(ctx.references, ["you", "you"])
