from collections.abc import Iterable, Iterator


class IterableDrop[T](Iterable[T]):
    def __init__(self, it: Iterable[T], length: int) -> None:
        self.it = it
        self.length = length

    def __iter__(self) -> Iterator[T]:
        return iter(self.it)

    def __len__(self) -> int:
        return self.length
