import cProfile
import json
import sys
import timeit
from pathlib import Path

from liquid import DictLoader
from liquid import Environment
from liquid.lex import get_lexer
from liquid.undefined import StrictUndefined

tokenize = get_lexer()


def fixture(path_to_templates: Path) -> dict[str, str]:
    # TODO: dataclass
    # TODO: inc data
    loader_dict: dict[str, str] = {}

    for input_file in path_to_templates.glob("*html"):
        loader_dict[input_file.name] = input_file.read_text()

    return loader_dict


def print_result(
    name: str, times: list[float], n_iterations: int, n_templates: int
) -> None:
    best = min(times)
    n_calls = n_iterations * n_templates
    per_sec = round(n_calls / best, 2)

    per_i = best / n_iterations
    i_per_s = 1 / per_i

    print(f"{name:>31}: {best:.2}s ({per_sec:.2f} ops/s, {i_per_s:.2f} i/s)")


def benchmark(search_path: str, number: int = 1000, repeat: int = 5) -> None:
    data = json.load((Path(search_path).parent / "data.json").open())
    templates = fixture(Path(search_path))
    env = Environment(
        loader=DictLoader(templates),
        globals=data,
        undefined=StrictUndefined,
    )
    source = templates["main.html"]
    # NOTE: included templates get parsed, main.html does not
    template = env.get_template("main.html")

    print(len(source))

    print((f"Best of {repeat} rounds with {number} iterations per round."))

    print_result(
        "scan template",
        timeit.repeat(
            "list(tokenize(template))",
            globals={
                "template": source,
                "tokenize": tokenize,
                "env": Environment(),
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
                "env": Environment(),
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


def profile_parse(search_path: str) -> None:
    # TODO: move to profile.py
    templates = fixture(Path(search_path))
    template = templates["main.html"]
    env = Environment()

    cProfile.runctx(
        "[env.from_string(template) for _ in range(1000)]",
        globals={
            "env": env,
            "template": template,
        },
        locals={},
        sort="cumtime",
    )


def main() -> None:
    # TODO: argparse
    search_path = "performance/fixtures/002/templates/"

    args = sys.argv
    n_args = len(args)

    if n_args == 1:
        benchmark(search_path)
    elif n_args == 2 and args[1] == "--profile":
        profile_parse(search_path)
    else:
        sys.stderr.write(f"usage: python {args[0]} [--profile]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
