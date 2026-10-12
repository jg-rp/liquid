class StringBuffer:
    def __init__(self):
        self._parts: list[str] = []
        self._length = 0

    def write(self, s: str) -> None:
        self._parts.append(s)
        self._length += len(s)

    def __len__(self) -> int:
        return self._length

    def getvalue(self) -> str:
        return "".join(self._parts)
