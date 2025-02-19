from __future__ import annotations

import json
import timeit
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from liquid import DictLoader
from liquid import Environment
from liquid.lex import get_lexer
from liquid.undefined import StrictUndefined

tokenize = get_lexer()


@dataclass
class Fixture:
    """Benchmark fixture data and templates."""

    name: str
    data: dict[str, object]
    templates: dict[str, str] = field(default_factory=dict)

    @staticmethod
    def load(path: Path) -> Fixture:
        """Load a benchmark fixture from _path_."""
        templates: dict[str, str] = {}

        for input_file in (path / "templates").glob("*liquid"):
            templates[input_file.name] = input_file.read_text()

        with (path / "data.json").open() as fd:
            data = json.load(fd)

        return Fixture(name=path.parts[-1], data=data, templates=templates)

    def env(self) -> Environment:
        """Return a new Liquid environment for this fixture."""
        return Environment(
            loader=DictLoader(self.templates),
            undefined=StrictUndefined,
            globals=self.data,
        )


def print_result(
    name: str, times: list[float], n_iterations: int, n_templates: int
) -> None:
    best = min(times)
    n_calls = n_iterations * n_templates
    per_sec = round(n_calls / best, 2)

    per_i = best / n_iterations
    i_per_s = 1 / per_i

    print(f"{name:>31}: {best:.2}s ({per_sec:.2f} ops/s, {i_per_s:.2f} i/s)")


def benchmark(path: str, number: int = 1000, repeat: int = 5) -> None:
    fixture = Fixture.load(Path(path))
    env = fixture.env()

    source = fixture.templates["index.liquid"]
    template = env.get_template("index.liquid")

    print(
        f"({fixture.name}) Best of {repeat} rounds with {number} iterations per round."
    )

    print_result(
        "scan template",
        timeit.repeat(
            "list(tokenize(template))",
            globals={
                "template": source,
                "tokenize": tokenize,
            },
            number=number,
            repeat=repeat,
        ),
        number,
        1,
    )

    print_result(
        "parse template",
        timeit.repeat(
            "env.from_string(template)",
            globals={
                "template": source,
                "env": env,
            },
            number=number,
            repeat=repeat,
        ),
        number,
        1,
    )

    print_result(
        "render templates",
        timeit.repeat(
            "template.render()",
            globals={
                "template": template,
            },
            number=number,
            repeat=repeat,
        ),
        number,
        1,
    )


def main() -> None:
    fixtures = [
        "performance/fixtures/001",
        "performance/fixtures/002",
    ]

    for fixture in fixtures:
        benchmark(fixture)
        print()


if __name__ == "__main__":
    main()
