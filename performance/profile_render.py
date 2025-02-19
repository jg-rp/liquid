from __future__ import annotations

import cProfile
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from performance.benchmark import Fixture

if TYPE_CHECKING:
    from liquid import BoundTemplate


def render_many(template: BoundTemplate, n: int = 10000) -> None:
    for _ in range(n):
        template.render()


def profile_render(path: Path) -> None:
    fixture = Fixture.load(path)
    env = fixture.env()
    template = env.get_template("index.liquid")

    cProfile.runctx(
        "render_many(template)",
        globals={"template": template, "render_many": render_many},
        locals={},
        sort="cumtime",
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    assert len(args) == 1, f"usage: {__file__} FIXTURE_NAME"
    fixture = Path("performance/fixtures/") / args[0]
    profile_render(fixture)
