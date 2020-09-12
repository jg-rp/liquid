from enum import Enum
from typing import NamedTuple, MutableMapping, Optional


class SymbolScope(Enum):
    GLOBAL = "GLOBAL"
    LOCAL = "LOCAL"


class Symbol(NamedTuple):
    name: str
    scope: SymbolScope
    index: int


class SymbolTable:
    def __init__(self):
        self.store: MutableMapping[str, Symbol] = {}
        self.size: int = 0

    def define(self, name: str) -> Symbol:
        symbol = Symbol(name=name, scope=SymbolScope.LOCAL, index=self.size)
        self.store[name] = symbol
        self.size += 1
        return symbol

    def resolve(self, name: str) -> Optional[Symbol]:
        return self.store.get(name, None)
