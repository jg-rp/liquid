"""Golden tests cases for testing liquid's built-in `default` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="nil",
        template=r"{{ nil | default: 'foo' }}",
        expect="foo",
    ),
    Case(
        description="false",
        template=r"{{ False | default: 'foo' }}",
        expect="foo",
    ),
    Case(
        description="empty string",
        template=r'{{ "" | default: "foo" }}',
        expect="foo",
    ),
    Case(
        description="empty array",
        template=r"{{ a | default: 'foo' }}",
        expect="foo",
        globals={"a": []},
    ),
    Case(
        description="empty object",
        template=r"{{ a | default: 'foo' }}",
        expect="foo",
        globals={"a": {}},
    ),
    Case(
        description="not empty string",
        template=r'{{ "hello" | default: "foo" }}',
        expect="hello",
    ),
    Case(
        description="not empty list",
        template=r'{{ a | default: "foo" | join: "#" }}',
        expect="hello#world",
        globals={"a": ["hello", "world"]},
    ),
    Case(
        description="not empty object",
        template=(
            r"{% assign b = a | default: foo %}"
            r"{% for item in b %}"
            r"({{ item[0] }},{{ item[1] }})"
            r"{% endfor %}"
        ),
        expect="(greeting,hello)",
        globals={"a": {"greeting": "hello"}, "foo": {"greeting": "goodbye"}},
    ),
    Case(
        description="too many arguments",
        template=r"{{ None | default: 'foo', 'bar', 'baz' }}",
        expect="",
        error=True,
    ),
    Case(
        description="missing argument",
        template=r"{{ false | default }}",
        expect="",
    ),
    Case(
        description="empty",
        template=r"{{ empty | default: bar }}",
        expect="",
    ),
    Case(
        description="allow false",
        template=r"{{ false | default: 'bar', allow_false:true }}",
        expect="false",
    ),
    Case(
        description="allow false from context",
        template=r"{{ false | default: 'bar', allow_false:foo }}",
        expect="false",
        globals={"foo": True},
    ),
    Case(
        description="undefined left value",
        template=r'{{ nosuchthing | default: "bar" }}',
        expect="bar",
    ),
    Case(
        description="true keyword argument before positional",
        template=r'{{ false | default: allow_false: true, "bar" }}',
        expect="false",
    ),
    Case(
        description="false keyword argument before positional",
        template=r'{{ false | default: allow_false: false, "bar" }}',
        expect="bar",
    ),
    Case(
        description="zero is not falsy",
        template=r'{{ 0 | default: "bar" }}',
        expect="0",
    ),
    Case(
        description="zero is not falsy with allow_false",
        template=r'{{ 0 | default: "bar", allow_false: true }}',
        expect="0",
    ),
    Case(
        description="0.0 is not falsy",
        template=r'{{ 0.0 | default: "bar" }}',
        expect="0.0",
    ),
]
