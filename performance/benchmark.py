from __future__ import annotations

import json
import timeit
from pathlib import Path

from liquid import DictLoader
from liquid import Environment
from liquid import StrictUndefined
from liquid.lex import get_lexer

tokenize = get_lexer()

FIXTURE = "performance/fixtures/002"
NUMBER = 10000
REPEAT = 3

fixture = Path(FIXTURE)
templates = {f.name: f.read_text() for f in (fixture / "templates").glob("*liquid")}

with (fixture / "data.json").open() as fd:
    data = json.load(fd)

env = Environment(
    loader=DictLoader(templates),
    undefined=StrictUndefined,
)

source = templates["index.liquid"]
template = env.get_template("index.liquid")

benchmarks: dict[str, tuple[str, str]] = {
    "tokenize": (
        "",
        "list(tokenize(source))",
    ),
    "parse": (
        "",
        "env.parse(source)",
    ),
    "render": (
        "",
        "template.render(**data)",
    ),
    "parse and render": (
        "",
        "env.render(source, **data)",
    ),
}


title = f"Benchmark {fixture.parts[-1]} ({NUMBER:,} times)"
print(f"{title:<35} | {'Min (s)':<10} | {'Mean (s)':<10}")
print("-" * 62)

for bench_name, (setup, stmt) in benchmarks.items():
    times = timeit.repeat(
        stmt=stmt,
        setup=setup,
        globals={
            "source": source,
            "template": template,
            "env": env,
            "data": data,
            "tokenize": tokenize,
        },
        repeat=REPEAT,
        number=NUMBER,
    )

    min_time = min(times)
    mean_time = sum(times) / len(times)

    print(f"{bench_name:<35} | {min_time:<10.4f} | {mean_time:<10.4f}")
