import collections.abc
from pathlib import Path
from typing import Optional


class TemplateDrop(collections.abc.Mapping):
    def __init__(self, name: str, path: Optional[Path]):
        self.name = name
        self.path = path or Path(name)

        self.stem = self.path.stem
        if "." in self.stem:
            self.suffix = self.stem.split(".")[-1]
        else:
            self.suffix = None

        self._items = {
            "directory": self.path.parent.name,
            "name": self.path.name.split(".")[0],
            "suffix": self.suffix,
        }

    def __str__(self):
        return self.stem

    def __repr__(self):
        return f"TemplateDrop(directory='{self['directory']}', name='{self['name']}', suffix='{self['suffix']}')"

    def __contains__(self, item):
        return item in self._items

    def __getitem__(self, key):
        return self._items[key]

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)
