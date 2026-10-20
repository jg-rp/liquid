from liquid import parse
from liquid._static_analysis import Locations, Segments, Vars

type Vars_ = dict[str, list[tuple[Segments, str]]]
type Locations_ = dict[str, list[str]]


def assert_vars(got: Vars, want: Vars_) -> None:
    for k, v in want.items():
        got_ = got.get(k, [])

        for i, (segments, value) in enumerate(v):
            assert got_[i]["value"] == value
            assert got_[i]["segments"] == segments

        assert len(got_) == len(v)

    assert len(got) == len(want)


def assert_locations(got: Locations, want: Locations_) -> None:
    for k, v in want.items():
        got_ = got.get(k, [])

        for i, w in enumerate(v):
            assert got_[i]["value"] == w

        assert len(got_) == len(v)

    assert len(got) == len(want)


def test_output() -> None:
    source = "{{ x | default: y, allow_false: z }}"
    analysis = parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "x": [(["x"], "x")],
        "y": [(["y"], "y")],
        "z": [(["z"], "z")],
    }

    variables: Vars_ = globals

    filters: Locations_ = {
        "default": ["default: y, allow_false: z"],
    }

    tags: Locations_ = {}

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


# TODO:
