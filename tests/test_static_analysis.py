import pytest

from liquid import DictLoader, Environment, parse
from liquid._static_analysis import Locations, Segments, Vars
from liquid.exceptions import TemplateNotFoundError

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
        "x": [(("x",), "x")],
        "y": [(("y",), "y")],
        "z": [(("z",), "z")],
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


def test_bracket_notation() -> None:
    source = "{{ x['y'].title }}"
    analysis = parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "x": [(("x", "y", "title"), "x['y'].title")],
    }

    variables: Vars_ = globals
    filters: Locations_ = {}
    tags: Locations_ = {}

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_quoted_name_notation() -> None:
    source = "{{ some['foo.bar'] }}"
    analysis = parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "some": [(("some", "foo.bar"), "some['foo.bar']")],
    }

    variables: Vars_ = globals
    filters: Locations_ = {}
    tags: Locations_ = {}

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_quoted_nested_vaariables() -> None:
    source = "{{ x[y.z].title }}"
    analysis = parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "x": [(("x", ("y", "z"), "title"), "x[y.z].title")],
        "y": [(("y", "z"), "y.z")],
    }

    variables: Vars_ = globals
    filters: Locations_ = {}
    tags: Locations_ = {}

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_dynamic_root_query() -> None:
    source = "{{ [a.b] }}"
    analysis = parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "a.b": [((("a", "b"),), "[a.b]")],
        "a": [(("a", "b"), "a.b")],
    }

    variables: Vars_ = globals
    filters: Locations_ = {}
    tags: Locations_ = {}

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_variable_segments() -> None:
    source = "{{ a['b.c'] }}{{ d[e.f][4] }}"
    analysis = parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "a": [(("a", "b.c"), "a['b.c']")],
        "d": [(("d", ("e", "f"), 4), "d[e.f][4]")],
        "e": [(("e", "f"), "e.f")],
    }

    variables: Vars_ = globals
    filters: Locations_ = {}
    tags: Locations_ = {}

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_assign() -> None:
    source = "{% assign x = y | append: z %}"
    analysis = parse(source).analyze()

    locals: Vars_ = {
        "x": [(("x",), "x")],
    }

    globals: Vars_ = {
        "y": [(("y",), "y")],
        "z": [(("z",), "z")],
    }

    variables: Vars_ = globals
    filters: Locations_ = {"append": ["append: z"]}
    tags: Locations_ = {"assign": ["assign"]}

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_capture() -> None:
    source = "{% capture x %}{% if y %}z{% endif %}{% endcapture %}"
    analysis = parse(source).analyze()

    locals: Vars_ = {
        "x": [(("x",), "x")],
    }

    globals: Vars_ = {
        "y": [(("y",), "y")],
    }

    variables: Vars_ = globals
    filters: Locations_ = {}
    tags: Locations_ = {
        "capture": ["capture"],
        "if": ["if"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_case() -> None:
    source = "".join(  # noqa: FLY002
        [
            "{% case x %}",
            "{% when y %}",
            "  {{ a }}",
            "{% when z %}",
            "  {{ b }}",
            "{% else %}",
            "  {{ c }}",
            "{% endcase %}",
        ]
    )
    analysis = parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "x": [(("x",), "x")],
        "y": [(("y",), "y")],
        "a": [(("a",), "a")],
        "z": [(("z",), "z")],
        "b": [(("b",), "b")],
        "c": [(("c",), "c")],
    }

    variables: Vars_ = globals
    filters: Locations_ = {}
    tags: Locations_ = {
        "case": ["case"],
        "when": ["when", "when"],
        "else": ["else"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_cycle() -> None:
    source = "{% cycle x: a, b %}"
    analysis = parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "a": [(("a",), "a")],
        "b": [(("b",), "b")],
        "x": [(("x",), "x")],
    }

    variables: Vars_ = globals
    filters: Locations_ = {}
    tags: Locations_ = {
        "cycle": ["cycle"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_decrement() -> None:
    source = "{% decrement x %}"
    analysis = parse(source).analyze()

    locals: Vars_ = {
        "x": [(("x",), "x")],
    }

    globals: Vars_ = {}

    variables: Vars_ = globals
    filters: Locations_ = {}
    tags: Locations_ = {
        "decrement": ["decrement"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_echo() -> None:
    source = "{% echo x | default: y, allow_false: z %}"
    analysis = parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "x": [(("x",), "x")],
        "y": [(("y",), "y")],
        "z": [(("z",), "z")],
    }
    variables: Vars_ = globals

    filters: Locations_ = {
        "default": ["default: y, allow_false: z"],
    }
    tags: Locations_ = {
        "echo": ["echo"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_for() -> None:
    source = "".join(  # noqa: FLY002
        [
            "{% for x in (1..y) %}",
            "  {{ x }}",
            "{% break %}",
            "{% else %}",
            "  {{ z }}",
            "{% continue %}",
            "{% endfor %}",
        ]
    )
    analysis = parse(source).analyze()

    locals: Vars_ = {}
    globals: Vars_ = {
        "y": [(("y",), "y")],
        "z": [(("z",), "z")],
    }

    variables: Vars_ = {
        "y": [(("y",), "y")],
        "x": [(("x",), "x")],
        "z": [(("z",), "z")],
    }

    filters: Locations_ = {}
    tags: Locations_ = {
        "for": ["for"],
        "break": ["break"],
        "continue": ["continue"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_if() -> None:
    source = "".join(  # noqa: FLY002
        [
            "{% if x %}",
            "  {{ a }}",
            "{% elsif y %}",
            "  {{ b }}",
            "{% else %}",
            "  {{ c }}",
            "{% endif %}",
        ]
    )
    analysis = parse(source).analyze()

    locals: Vars_ = {}
    globals: Vars_ = {
        "x": [(("x",), "x")],
        "a": [(("a",), "a")],
        "y": [(("y",), "y")],
        "b": [(("b",), "b")],
        "c": [(("c",), "c")],
    }

    variables: Vars_ = globals

    filters: Locations_ = {}
    tags: Locations_ = {
        "if": ["if"],
        "elsif": ["elsif"],
        "else": ["else"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_increment() -> None:
    source = "{% increment x %}"
    analysis = parse(source).analyze()

    locals: Vars_ = {
        "x": [(("x",), "x")],
    }

    globals: Vars_ = {}
    variables: Vars_ = globals

    filters: Locations_ = {}
    tags: Locations_ = {
        "increment": ["increment"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_liquid() -> None:
    source = """\
{% liquid
if product.title
    echo foo | upcase
else
    echo 'product-1' | upcase
endif

for i in (0..5)
    echo i
endfor %}"""

    analysis = parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "product": [(("product", "title"), "product.title")],
        "foo": [(("foo",), "foo")],
    }

    variables: Vars_ = {
        "product": [(("product", "title"), "product.title")],
        "foo": [(("foo",), "foo")],
        "i": [(("i",), "i")],
    }

    filters: Locations_ = {
        "upcase": ["upcase", "upcase"],
    }

    tags: Locations_ = {
        "liquid": ["liquid"],
        "echo": ["echo", "echo", "echo"],
        "for": ["for"],
        "if": ["if"],
        "else": ["else"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_unless() -> None:
    source = """\
{% unless x %}
  {{ a }}
{% elsif y %}
  {{ b }}
{% else %}
  {{ c }}
{% endunless %}"""

    analysis = parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "x": [(("x",), "x")],
        "a": [(("a",), "a")],
        "y": [(("y",), "y")],
        "b": [(("b",), "b")],
        "c": [(("c",), "c")],
    }

    variables: Vars_ = globals

    filters: Locations_ = {}

    tags: Locations_ = {
        "unless": ["unless"],
        "elsif": ["elsif"],
        "else": ["else"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_include() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x }}"}))
    source = "{% include 'a' %}"
    analysis = env.parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "x": [(("x",), "x")],
    }

    variables: Vars_ = globals

    filters: Locations_ = {}

    tags: Locations_ = {
        "include": ["include"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_include_assign() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x }}{% assign y = 42 %}"}))
    source = "{% include 'a' %}{{ y }}"
    analysis = env.parse(source).analyze()

    locals: Vars_ = {
        "y": [(("y",), "y")],
    }

    globals: Vars_ = {
        "x": [(("x",), "x")],
    }

    variables: Vars_ = {
        "x": [(("x",), "x")],
        "y": [(("y",), "y")],
    }

    filters: Locations_ = {}

    tags: Locations_ = {
        "include": ["include"],
        "assign": ["assign"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_include_twice() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x }}"}))
    source = "{% include 'a' %}{% include 'a' %}"
    analysis = env.parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "x": [(("x",), "x")],
    }

    variables: Vars_ = globals
    filters: Locations_ = {}

    tags: Locations_ = {
        "include": ["include", "include"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_include_recirsive() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x }}{% include 'a' %}"}))
    source = "{% include 'a' %}"
    analysis = env.parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "x": [(("x",), "x")],
    }

    variables: Vars_ = globals
    filters: Locations_ = {}

    tags: Locations_ = {
        "include": ["include", "include"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_include_with_bound_variable() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x | append: y }}{{ a }}"}))
    source = "{% include 'a' with z %}"
    analysis = env.parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "z": [(("z",), "z")],
        "x": [(("x",), "x")],
        "y": [(("y",), "y")],
    }

    variables: Vars_ = {
        "z": [(("z",), "z")],
        "x": [(("x",), "x")],
        "y": [(("y",), "y")],
        "a": [(("a",), "a")],
    }

    filters: Locations_ = {
        "append": ["append: y"],
    }

    tags: Locations_ = {
        "include": ["include"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_include_with_bound_alias() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x | append: y }}"}))
    source = "{% include 'a' with z as y %}"
    analysis = env.parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "z": [(("z",), "z")],
        "x": [(("x",), "x")],
    }

    variables: Vars_ = {
        "z": [(("z",), "z")],
        "x": [(("x",), "x")],
        "y": [(("y",), "y")],
    }

    filters: Locations_ = {
        "append": ["append: y"],
    }

    tags: Locations_ = {
        "include": ["include"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_include_with_arguments() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x | append: y }}"}))
    source = "{% include 'a', x:y, z:42 %}{{ x }}"
    analysis = env.parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "y": [
            (("y",), "y"),
            (("y",), "y"),
        ],
        "x": [(("x",), "x")],
    }

    variables: Vars_ = {
        "y": [
            (("y",), "y"),
            (("y",), "y"),
        ],
        "x": [
            (("x",), "x"),
            (("x",), "x"),
        ],
    }

    filters: Locations_ = {
        "append": ["append: y"],
    }

    tags: Locations_ = {
        "include": ["include"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_include_with_dynamic_name() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x | append: y }}"}))
    source = "{% include b %}{{ x }}"

    with pytest.raises(TemplateNotFoundError):
        env.parse(source).analyze()


def test_include_template_not_found() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x | append: y }}"}))
    source = "{% include 'nosuchthing' %}{{ x }}"

    with pytest.raises(TemplateNotFoundError):
        env.parse(source).analyze()


def test_render_assign() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x }}{% assign y = 42 %}"}))
    source = "{% render 'a' %}{{ y }}"
    analysis = env.parse(source).analyze()

    locals: Vars_ = {
        "y": [(("y",), "y")],
    }

    globals: Vars_ = {
        "x": [(("x",), "x")],
        "y": [(("y",), "y")],
    }

    variables: Vars_ = {
        "x": [(("x",), "x")],
        "y": [(("y",), "y")],
    }

    filters: Locations_ = {}

    tags: Locations_ = {
        "render": ["render"],
        "assign": ["assign"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_render_twice() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x }}"}))
    source = "{% render 'a' %}{% render 'a' %}"
    analysis = env.parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "x": [(("x",), "x")],
    }

    variables: Vars_ = globals
    filters: Locations_ = {}

    tags: Locations_ = {
        "render": ["render", "render"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_render_recirsive() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x }}{% render 'a' %}"}))
    source = "{% render 'a' %}"
    analysis = env.parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "x": [(("x",), "x")],
    }

    variables: Vars_ = globals
    filters: Locations_ = {}

    tags: Locations_ = {
        "render": ["render", "render"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_render_with_bound_variable() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x | append: y }}{{ a }}"}))
    source = "{% render 'a' with z %}"
    analysis = env.parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "z": [(("z",), "z")],
        "x": [(("x",), "x")],
        "y": [(("y",), "y")],
    }

    variables: Vars_ = {
        "z": [(("z",), "z")],
        "x": [(("x",), "x")],
        "y": [(("y",), "y")],
        "a": [(("a",), "a")],
    }

    filters: Locations_ = {
        "append": ["append: y"],
    }

    tags: Locations_ = {
        "render": ["render"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_render_with_bound_alias() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x | append: y }}"}))
    source = "{% render 'a' with z as y %}"
    analysis = env.parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "z": [(("z",), "z")],
        "x": [(("x",), "x")],
    }

    variables: Vars_ = {
        "z": [(("z",), "z")],
        "x": [(("x",), "x")],
        "y": [(("y",), "y")],
    }

    filters: Locations_ = {
        "append": ["append: y"],
    }

    tags: Locations_ = {
        "render": ["render"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_render_with_arguments() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x | append: y }}"}))
    source = "{% render 'a', x:y, z:42 %}{{ x }}"
    analysis = env.parse(source).analyze()

    locals: Vars_ = {}

    globals: Vars_ = {
        "y": [
            (("y",), "y"),
            (("y",), "y"),
        ],
        "x": [(("x",), "x")],
    }

    variables: Vars_ = {
        "y": [
            (("y",), "y"),
            (("y",), "y"),
        ],
        "x": [
            (("x",), "x"),
            (("x",), "x"),
        ],
    }

    filters: Locations_ = {
        "append": ["append: y"],
    }

    tags: Locations_ = {
        "render": ["render"],
    }

    assert_vars(analysis.locals, locals)
    assert_vars(analysis.globals, globals)
    assert_vars(analysis.variables, variables)
    assert_locations(analysis.filters, filters)
    assert_locations(analysis.tags, tags)


def test_render_template_not_found() -> None:
    env = Environment(loader=DictLoader({"a": "{{ x | append: y }}"}))
    source = "{% render 'nosuchthing' %}{{ x }}"

    with pytest.raises(TemplateNotFoundError):
        env.parse(source).analyze()
