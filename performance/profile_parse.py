import cProfile
import sys
from pathlib import Path

from performance.benchmark import Fixture


def profile_parse(path: Path) -> None:
    fixture = Fixture.load(Path(path))
    env = fixture.env()
    source = fixture.templates["index.liquid"]

    cProfile.runctx(
        "[env.from_string(template) for _ in range(1000)]",
        globals={
            "env": env,
            "template": source,
        },
        locals={},
        sort="cumtime",
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        print(f"usage: {Path(__file__).name} FIXTURE_NAME")
        sys.exit(1)
    fixture = Path("performance/fixtures/") / args[0]
    profile_parse(fixture)
