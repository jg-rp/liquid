"""Golden tests cases for testing liquid's `case` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="simple case/when",
        template=(
            r"{% case title %}"
            r"{% when 'foo' %}foo"
            r"{% when 'Hello' %}bar"
            r"{% endcase %}"
        ),
        expect="bar",
        globals={"title": "Hello"},
    ),
    Case(
        description="'when' expression using an identifier",
        template=(
            r"{% case title %}"
            r"{% when other %}foo"
            r"{% when 'goodbye' %}bar"
            r"{% endcase %}"
        ),
        expect="foo",
        globals={"title": "Hello", "other": "Hello"},
    ),
    Case(
        description="tags inside when block",
        template=(
            r"{% case title %}"
            r"{% when other %}"
            r"{% if true %}foo{% endif %}"
            r"{% when 'goodbye' %}bar"
            r"{% endcase %}"
        ),
        expect="foo",
        globals={"title": "Hello", "other": "Hello"},
    ),
    Case(
        description="'when' expression using an out of scope identifier",
        template=(
            r"{% case title %}"
            r"{% when nosuchthing %}foo"
            r"{% when 'Hello' %}bar"
            r"{% endcase %}"
        ),
        expect="bar",
        globals={"title": "Hello"},
    ),
    Case(
        description="name not in scope",
        template=(
            r"{% case nosuchthing %}"
            r"{% when 'foo' %}foo"
            r"{% when 'bar' %}bar"
            r"{% endcase %}"
        ),
        expect="",
    ),
    Case(
        description="no match and no default",
        template=(
            r"{% case title %}"
            r"{% when 'foo' %}foo"
            r"{% when 'bar' %}bar"
            r"{% endcase %}"
        ),
        expect="",
        globals={"title": "Hello"},
    ),
    Case(
        description="with default",
        template=r"{% case title %}{% when 'foo' %}foo{% else %}bar{% endcase %}",
        expect="bar",
        globals={"title": "Hello"},
    ),
    Case(
        description="no whens",
        template=r"{% case title %}{% else %}bar{% endcase %}",
        expect="bar",
        globals={"title": "Hello"},
    ),
    Case(
        description="no whens or default",
        template=r"{% case title %}{% endcase %}",
        expect="",
        globals={"title": "Hello"},
    ),
    Case(
        description="whitespace",
        template=(
            "{% case title %}  \n\t"
            "{% when 'foo' %}foo\n"
            "{% when 'Hello' %}bar"
            "{% endcase %}"
        ),
        expect="bar",
        globals={"title": "Hello"},
    ),
    Case(
        description="comma separated when expression",
        template=(
            r"{% case title %}"
            r"{% when 'foo' %}foo"
            r"{% when 'bar', 'Hello' %}bar"
            r"{% endcase %}"
        ),
        expect="bar",
        globals={"title": "Hello"},
    ),
    Case(
        description="evaluate multiple matching blocks",
        template=(
            r"{% case title %}"
            r"{% when 'Hello' %}foo"
            r"{% when a, 'Hello' %}bar"
            r"{% endcase %}"
        ),
        expect="foobarbar",
        globals={"title": "Hello", "a": "Hello"},
    ),
    Case(
        description="or separated when expression",
        template=(
            r"{% case title %}"
            r"{% when 'foo' %}foo"
            r"{% when 'bar' or 'Hello' %}bar"
            r"{% endcase %}"
        ),
        expect="bar",
        globals={"title": "Hello"},
    ),
    Case(
        description="mix or and comma separated when expression",
        template=(
            r"{% case title %}"
            r"{% when 'foo' %}foo"
            r"{% when 'bar' or 'Hello', 'Hello' %}bar"
            r"{% endcase %}"
        ),
        expect="barbar",
        globals={"title": "Hello"},
    ),
    Case(
        description="mix or and comma separated when expression",
        template=(
            r"{% case title %}"
            r"{% when 'foo' %}foo"
            r"{% when 'bar' or 'Hello', 'Hello' %}bar"
            r"{% endcase %}"
        ),
        expect="barbar",
        globals={"title": "Hello"},
    ),
    Case(
        description="unexpected when token",
        template=(
            r"{% case title %}"
            r"{% when 'foo' %}foo"
            r"{% when 'bar' and 'Hello', 'Hello' %}bar"
            r"{% endcase %}"
        ),
        expect="",
        globals={"title": "Hello"},
    ),
    Case(
        description="comma string literal",
        template=(
            r"{% case foo %}"
            r"{% when 'foo' %}bar"
            r"{% when ',' %}comma"
            r"{% endcase %}"
        ),
        expect="comma",
        globals={"foo": ","},
    ),
    Case(
        description="empty when tag",
        template=(r"{% case foo %}{% when %}bar{% endcase %}"),
        expect="",
        globals={"foo": "bar"},
        error=True,
    ),
]
