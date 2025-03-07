"""Golden tests cases for testing liquid's `if` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="condition with literal consequence",
        template=r"{% if product.title == 'foo' %}bar{% endif %}",
        expect="bar",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="condition with literal consequence and literal alternative",
        template=r"{% if product.title == 'hello' %}bar{% else %}baz{% endif %}",
        expect="baz",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="condition with conditional alternative",
        template=(
            r"{% if product.title == 'hello' %}"
            r"foo"
            r"{% elsif product.title == 'foo' %}"
            r"bar"
            r"{% endif %}"
        ),
        expect="bar",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="condition with conditional alternative and final alternative",
        template=(
            r"{% if product.title == 'hello' %}"
            r"foo"
            r"{% elsif product.title == 'goodbye' %}"
            r"bar"
            r"{% else %}"
            r"baz"
            r"{% endif %}"
        ),
        expect="baz",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="non-empty hash is truthy",
        template=r"{% if product %}bar{% else %}foo{% endif %}",
        expect="bar",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="literal nil is falsy",
        template=r"{% if nil %}bar{% else %}foo{% endif %}",
        expect="foo",
    ),
    Case(
        description="undefined variables are falsy",
        template=r"{% if nosuchthing %}bar{% else %}foo{% endif %}",
        expect="foo",
    ),
    Case(
        description="nested condition in the consequence block",
        template=(
            r"{% if product %}"
            r"{% if title == 'Hello' %}"
            r"baz"
            r"{% endif %}"
            r"{% endif %}"
        ),
        expect="baz",
        globals={
            "product": {"title": "foo"},
            "title": "Hello",
        },
    ),
    Case(
        description="nested condition, alternative in the consequence block",
        template=(
            r"{% if product %}"
            r"{% if title == 'goodbye' %}"
            r"baz"
            r"{% else %}"
            r"hello"
            r"{% endif %}"
            r"{% endif %}"
        ),
        expect="hello",
        globals={"product": {"title": "foo"}, "title": "Hello"},
    ),
    Case(
        description="literal false condition",
        template=r"{% if false %}{% endif %}",
        expect="",
    ),
    Case(
        description="contains condition",
        template=r"{% if product.tags contains 'garden' %}baz{% endif %}",
        expect="baz",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="not equal condition",
        template=r"{% if product.title != 'foo' %}baz{% endif %}",
        expect="",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="alternate not equal condition",
        template=r"{% if product.title <> 'foo' %}baz{% endif %}",
        expect="",
        globals={"product": {"title": "foo"}},
    ),
    Case(
        description="blocks that contain only whitespace are not rendered",
        template=r"{% if true %}  {% elsif false %} {% else %} {% endif %}",
        expect="",
    ),
    Case(
        description=(
            "blocks that contain only whitespace and comments are not rendered"
        ),
        template=(
            r"{% if true %} "
            r"{% comment %} this is blank {% endcomment %} "
            r"{% endif %}"
        ),
        expect="",
    ),
    Case(
        description="compare empty string literal to blank",
        template=r"{% if '' == blank %}is blank{% endif %}",
        expect="is blank",
        standard=False,
    ),
    Case(
        description="conditional alternative with default",
        template=(
            r"{% if false %}foo"
            r"{% elsif false %}bar"
            r"{% else %}hello"
            r"{% endif %}"
        ),
        expect="hello",
    ),
    Case(
        description="range equals range",
        template=(
            r"{% assign foo = (1..3) %}"
            r"{% if foo == (1..3) %}true"
            r"{% else %}false"
            r"{% endif %}"
        ),
        expect="true",
    ),
    Case(
        description="logical operators are right associative",
        template=r"{% if true and false and false or true %}hello{% endif %}",
        expect="",
    ),
    Case(
        description="zero is not equal to false",
        template=r"{% if 0 == false %}Hello{% else %}Goodbye{% endif %}",
        expect="Goodbye",
    ),
    Case(
        description="zero is truthy",
        template=r"{% if 0 %}Hello{% else %}Goodbye{% endif %}",
        expect="Hello",
    ),
    Case(
        description="0.0 is truthy",
        template=(r"{% if 0.0 %}Hello{% else %}Goodbye{% endif %}"),
        expect="Hello",
    ),
    Case(
        description="one is not equal to true",
        template=(r"{% if 1 == true %}Hello{% else %}Goodbye{% endif %}"),
        expect="Goodbye",
    ),
    Case(
        description="array is equal to array",
        template=(
            "{% assign x = 'a,b,c' | split: ',' %}"
            "{% assign y = 'a,b,c' | split: ',' %}"
            "{% if x == y %}true{% else %}false{% endif %}"
        ),
        expect="true",
    ),
    Case(
        description="array is equal to array from context",
        template=(
            "{% assign y = 'a,b,c' | split: ',' %}"
            "{% if x == y %}true{% else %}false{% endif %}"
        ),
        globals={"x": ["a", "b", "c"]},
        expect="true",
    ),
    Case(
        description="string does not equal int",
        template="{% if '1' == 1 %}true{% else %}false{% endif %}",
        globals={},
        expect="false",
    ),
    Case(
        description="int does not equal string",
        template="{% if 1 == '1' %}true{% else %}false{% endif %}",
        globals={},
        expect="false",
    ),
    Case(
        description="int equals float",
        template="{% if 1 == 1.0 %}true{% else %}false{% endif %}",
        globals={},
        expect="true",
    ),
    Case(
        description="string greater than int",
        template="{% if '2' > 1 %}true{% else %}false{% endif %}",
        globals={},
        expect="false",
        error=True,
    ),
    Case(
        description="string is less than string",
        template="{% if 'abc' < 'acb' %}true{% else %}false{% endif %}",
        globals={},
        expect="true",
    ),
    Case(
        description="string is not less than string",
        template="{% if 'bbb' < 'aaa' %}true{% else %}false{% endif %}",
        globals={},
        expect="false",
    ),
    Case(
        description="string is less than or equal to string",
        template="{% if 'abc' <= 'acb' %}true{% else %}false{% endif %}",
        globals={},
        expect="true",
    ),
    Case(
        description="string is not less than or equal to string",
        template="{% if 'bbb' <= 'aaa' %}true{% else %}false{% endif %}",
        globals={},
        expect="false",
    ),
    Case(
        description="string is greater than string",
        template="{% if 'abc' > 'acb' %}true{% else %}false{% endif %}",
        globals={},
        expect="false",
    ),
    Case(
        description="string is not greater than string",
        template="{% if 'bbb' > 'aaa' %}true{% else %}false{% endif %}",
        globals={},
        expect="true",
    ),
    Case(
        description="string is greater than or equal to string",
        template="{% if 'abc' >= 'acb' %}true{% else %}false{% endif %}",
        globals={},
        expect="false",
    ),
    Case(
        description="string is not greater than or equal to string",
        template="{% if 'bbb' >= 'aaa' %}true{% else %}false{% endif %}",
        globals={},
        expect="true",
    ),
    Case(
        description="else tag expressions are ignored",
        template="{% if false %}1{% else nonsense %}2{% endif %}",
        globals={},
        expect="2",
        error=False,
        strict=True,
        future=True,
    ),
    Case(
        description="extra else blocks are ignored",
        template="{% if false %}1{% else %}2{% else %}3{% endif %}",
        globals={},
        expect="2",
        error=False,
        strict=True,
        future=True,
    ),
    Case(
        description="extra elsif blocks are ignored",
        template="{% if false %}1{% else %}2{% elsif true %}3{% endif %}",
        globals={},
        expect="2",
        error=False,
        strict=True,
        future=True,
    ),
    Case(
        description="empty array equals special empty",
        template="{% if x == empty %}TRUE{% else %}FALSE{% endif %}",
        expect="TRUE",
        globals={"x": []},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="empty array is truthy",
        template="{% if x %}TRUE{% else %}FALSE{% endif %}",
        expect="TRUE",
        globals={"x": []},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="empty object equals special empty",
        template="{% if x == empty %}TRUE{% else %}FALSE{% endif %}",
        expect="TRUE",
        globals={"x": {}},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="empty object is truthy",
        template="{% if x %}TRUE{% else %}FALSE{% endif %}",
        expect="TRUE",
        globals={"x": {}},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="empty string is truthy",
        template="{% if '' %}TRUE{% else %}FALSE{% endif %}",
        expect="TRUE",
        globals={},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="string contains string",
        template="{% if 'hello' contains 'llo' %}TRUE{% else %}FALSE{% endif %}",
        expect="TRUE",
        globals={},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="string contains int",
        template="{% if 'hel9lo' contains 9 %}TRUE{% else %}FALSE{% endif %}",
        expect="TRUE",
        globals={},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="string contains string from context",
        template="{% if 'hello' contains s %}TRUE{% else %}FALSE{% endif %}",
        expect="TRUE",
        globals={"s": "llo"},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="context string contains string from context",
        template="{% if t contains s %}TRUE{% else %}FALSE{% endif %}",
        expect="TRUE",
        globals={"s": "llo", "t": "hello"},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="undefined is equal to nil",
        template="{% if nosuchthing == nil %}TRUE{% else %}FALSE{% endif %}",
        expect="TRUE",
        globals={},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="undefined is equal to null",
        template="{% if nosuchthing == null %}TRUE{% else %}FALSE{% endif %}",
        expect="TRUE",
        globals={},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="string contains undefined",
        template="{% if s contains nosuchthing %}TRUE{% else %}FALSE{% endif %}",
        expect="FALSE",
        globals={"s": "hello"},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="array contains undefined",
        template="{% if a contains nosuchthing %}TRUE{% else %}FALSE{% endif %}",
        expect="FALSE",
        globals={"a": [1, 2, 3, None]},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="array contains false",
        template="{% if a contains false %}TRUE{% else %}FALSE{% endif %}",
        expect="FALSE",
        globals={"a": [1, 2, 3, False]},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="object contains undefined",
        template="{% if obj contains nosuchthing %}TRUE{% else %}FALSE{% endif %}",
        expect="FALSE",
        globals={"obj": {"foo": "bar"}},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="string contains nil",
        template="{% if s contains nil %}TRUE{% else %}FALSE{% endif %}",
        expect="FALSE",
        globals={"s": "hello"},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="array contains nil",
        template="{% if a contains nil %}TRUE{% else %}FALSE{% endif %}",
        expect="FALSE",
        globals={"a": [1, 2, None]},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="object contains nil",
        template="{% if obj contains nosuchthing %}TRUE{% else %}FALSE{% endif %}",
        expect="FALSE",
        globals={"obj": {"foo": "bar"}},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="undefined contains string",
        template="{% if undefined contains s %}TRUE{% else %}FALSE{% endif %}",
        expect="FALSE",
        globals={"s": "hello"},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="undefined contains array",
        template="{% if undefined contains a %}TRUE{% else %}FALSE{% endif %}",
        expect="FALSE",
        globals={"a": [1, 2, 3]},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="undefined contains object",
        template="{% if undefined contains obj %}TRUE{% else %}FALSE{% endif %}",
        expect="FALSE",
        globals={"obj": {"foo": "bar"}},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="undefined contains undefined",
        template="{% if undefined contains thing %}TRUE{% else %}FALSE{% endif %}",
        expect="FALSE",
        globals={},
        partials={},
        error=False,
        strict=False,
    ),
    Case(
        description="startswith is not a valid operator",
        template="{% if s startswith t %}TRUE{% else %}FALSE{% endif %}",
        expect="",
        globals={"s": "hello", "t": "hell"},
        partials={},
        error=True,
        strict=False,
    ),
    Case(
        description="endswith is not a valid operator",
        template="{% if s endswith t %}TRUE{% else %}FALSE{% endif %}",
        expect="",
        globals={"s": "hello", "t": "lo"},
        partials={},
        error=True,
        strict=False,
    ),
    Case(
        description="haskey is not a valid operator",
        template="{% if obj haskey x %}TRUE{% else %}FALSE{% endif %}",
        expect="",
        globals={"obj": {"foo": "bar"}, "x": "foo"},
        partials={},
        error=True,
        strict=False,
    ),
    Case(
        description="in is not a valid operator",
        template="{% if t in s %}TRUE{% else %}FALSE{% endif %}",
        expect="",
        globals={"s": "hello", "t": "lo"},
        partials={},
        error=True,
        strict=False,
    ),
]
