import asyncio
from collections.abc import AsyncGenerator

from liquid import AsyncIterableDrop, IterableDrop, parse


def test_async_loop_over_async_iterable() -> None:
    class MockIterable:
        def __liquid_iter__(
            self, offset: int, limit: int | None, reversed_: bool
        ) -> IterableDrop[object]:
            return IterableDrop(iter([1, 2, 3]), 3)

        async def __liquid_iter_async__(
            self, offset: int, limit: int | None, reversed_: bool
        ) -> AsyncIterableDrop[object]:
            async def f() -> AsyncGenerator[int]:
                yield 4
                yield 5
                yield 6

            return AsyncIterableDrop(f(), 3)

    data = {"y": MockIterable()}
    template = parse("{% for x in y %}{{ x }},{% endfor %}")

    async def coro() -> str:
        return await template.render_async(data)

    assert template.render(data) == "1,2,3,"
    assert asyncio.run(coro()) == "4,5,6,"


def test_async_loop_over_iterable() -> None:
    class MockIterable:
        def __liquid_iter__(
            self, offset: int, limit: int | None, reversed_: bool
        ) -> IterableDrop[object]:
            return IterableDrop(iter([1, 2, 3]), 3)

        async def __liquid_iter_async__(
            self, offset: int, limit: int | None, reversed_: bool
        ) -> IterableDrop[object]:
            return IterableDrop(iter(["a", "b", "c"]), 3)

    data = {"y": MockIterable()}
    template = parse("{% for x in y %}{{ x }},{% endfor %}")

    async def coro() -> str:
        return await template.render_async(data)

    assert template.render(data) == "1,2,3,"
    assert asyncio.run(coro()) == "a,b,c,"
