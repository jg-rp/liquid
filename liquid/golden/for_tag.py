"""Golden tests cases for testing liquid's `for` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="simple range loop",
        template=r"{% for i in (0..3) %}{{ i }} {% endfor %}",
        expect="0 1 2 3 ",
    ),
    Case(
        description="range loop using identifier",
        template=(
            r"{% for i in (0..product.end_range) %}"
            r"{{ i }} - {{ product.tags[i] }} "
            r"{% endfor %}"
        ),
        expect="0 - sports 1 - garden ",
        globals={"product": {"tags": ["sports", "garden"], "end_range": 1}},
    ),
    Case(
        description="simple array loop",
        template=r"{% for tag in product.tags %}{{ tag }} {% endfor %}",
        expect="sports garden ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="loop over an array in reverse",
        template=r"{% for tag in product.tags reversed %}{{ tag }} {% endfor %}",
        expect="garden sports ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="simple hash loop",
        template=r"{% for c in collection %}{{ c[0] }} {{ c[1] }} {% endfor %}",
        expect="title foo description bar ",
        globals={"collection": {"title": "foo", "description": "bar"}},
    ),
    Case(
        description="empty array with default",
        template=(
            r"{% for img in emptythings.array %}"
            r"{{ img.url }} "
            r"{% else %}"
            r"no images"
            r"{% endfor %}"
        ),
        expect="no images",
        globals={"emptythings": {"array": [], "map": {}, "string": ""}},
    ),
    Case(
        description="break",
        template=(
            r"{% for tag in product.tags %}"
            r"{% if tag == 'sports' %}"
            r"{% break %}"
            r"{% else %}"
            r"{{ tag }} "
            r"{% endif %}"
            r"{% else %}"
            r"no images"
            r"{% endfor %}"
        ),
        expect="",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="continue",
        template=(
            r"{% for tag in product.tags %}"
            r"{% if tag == 'sports' %}"
            r"{% continue %}"
            r"{% else %}"
            r"{{ tag }} "
            r"{% endif %}"
            r"{% else %}"
            r"no images"
            r"{% endfor %}"
        ),
        expect="garden ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="limit",
        template=r"{% for tag in product.tags limit:1 %}{{ tag }} {% endfor %}",
        expect="sports ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="offset",
        template=r"{% for tag in product.tags offset:1 %}{{ tag }} {% endfor %}",
        expect="garden ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="forloop length",
        template=r"{% for tag in product.tags %}{{ forloop.length }} {% endfor %}",
        expect="2 2 ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="forloop length with limit",
        template=r"{% for tag in tags limit:3 %}{{ forloop.length }} {% endfor %}",
        expect="3 3 3 ",
        globals={
            "tags": [
                "sports",
                "garden",
                "home",
                "diy",
                "motoring",
                "fashion",
            ]
        },
    ),
    Case(
        description="forloop length with offset",
        template=r"{% for tag in tags offset:3 %}{{ forloop.length }} {% endfor %}",
        expect="3 3 3 ",
        globals={
            "tags": [
                "sports",
                "garden",
                "home",
                "diy",
                "motoring",
                "fashion",
            ]
        },
    ),
    Case(
        description="forloop goes out of scope",
        template=(
            r"{% for tag in product.tags %}"
            r"{{ forloop.length }} "
            r"{% endfor %}"
            r"{{ forloop.length }}"
        ),
        expect="2 2 ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="forloop.first",
        template=r"{% for tag in product.tags %}{{ forloop.first }} {% endfor %}",
        expect="true false ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="forloop.last",
        template=r"{% for tag in product.tags %}{{ forloop.last }} {% endfor %}",
        expect="false true ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="forloop.index",
        template=r"{% for tag in product.tags %}{{ forloop.index }} {% endfor %}",
        expect="1 2 ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="forloop.index0",
        template=r"{% for tag in product.tags %}{{ forloop.index0 }} {% endfor %}",
        expect="0 1 ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="forloop.rindex",
        template=r"{% for tag in product.tags %}{{ forloop.rindex }} {% endfor %}",
        expect="2 1 ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="forloop.rindex0",
        template=r"{% for tag in product.tags %}{{ forloop.rindex0 }} {% endfor %}",
        expect="1 0 ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="forloop name",
        template=r"{% for tag in product.tags limit:1 %}{{ forloop.name }}{% endfor %}",
        expect="tag-product.tags",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="forloop name of a range",
        template=r"{% for i in (1..3) limit:1 %}{{ forloop.name }}{% endfor %}",
        expect="i-(1..3)",
        globals={},
    ),
    Case(
        description="forloop no such attribute",
        template=r"{% for tag in product.tags %}{{ forloop.nosuchthing }}{% endfor %}",
        expect="",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="iterate an empty array",
        template=r"{% for item in emptythings.array %}{{ item }}{% endfor %}",
        expect="",
        globals={"emptythings": {"array": [], "map": {}, "string": ""}},
    ),
    Case(
        description="iterate an empty array with default",
        template=(
            r"{% for item in emptythings.array %}"
            r"{{ item }}{% else %}foo"
            r"{% endfor %}"
        ),
        expect="foo",
        globals={"emptythings": {"array": [], "map": {}, "string": ""}},
    ),
    Case(
        description="lookup a filter from an outer context",
        template=r"{% for tag in product.tags %}{{ tag | upcase }} {% endfor %}",
        expect="SPORTS GARDEN ",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="assign inside loop",
        template=(
            r"{% for tag in product.tags %}"
            r"{% assign x = tag %}"
            r"{% endfor %}"
            r"{{ x }}"
        ),
        expect="garden",
        globals={"product": {"tags": ["sports", "garden"]}},
    ),
    Case(
        description="blank empty loops",
        template=r"{% for i in (0..10) %}  {% endfor %}",
        expect="",
    ),
    Case(
        description=(
            "loop over nested and chained object from context "
            "with trailing identifier"
        ),
        template=(
            r"{% for link in linklists[section.settings.menu].links %}"
            r"{{ link }} "
            r"{% endfor %}"
        ),
        expect="1 2 ",
        globals={
            "linklists": {"main": {"links": ["1", "2"]}},
            "section": {"settings": {"menu": "main"}},
        },
    ),
    Case(
        description="loop over undefined",
        template=r"{% for tag in nosuchthing %}{{ tag }}{% endfor %}",
        expect="",
        globals={},
    ),
    Case(
        description="continue a loop",
        template=(
            r"{% for item in array limit: 3 %}"
            r"a{{ item }} "
            r"{% endfor %}"
            r"{% for item in array offset: continue %}"
            r"b{{ item }} "
            r"{% endfor %}"
        ),
        expect="a1 a2 a3 b4 b5 b6 ",
        globals={"array": [1, 2, 3, 4, 5, 6]},
    ),
    Case(
        description="continue a loop over an assigned range",
        template=(
            r"{% assign nums = (1..5) %}"
            r"{% for item in nums limit: 3 %}"
            r"a{{ item }} "
            r"{% endfor %}"
            r"{% for item in nums offset: continue %}"
            r"b{{ item }} "
            r"{% endfor %}"
        ),
        expect="a1 a2 a3 b4 b5 ",
    ),
    Case(
        description="continue a loop over a changing array",
        template=(
            r"{% assign foo = '1,2,3,4,5,6' | split: ',' %}"
            r"{% for item in foo limit: 3 %}"
            r"{{ item }} "
            r"{% endfor %}"
            r"{% assign foo = 'u,v,w,x,y,z' | split: ',' %}"
            r"{% for item in foo offset: continue %}"
            r"{{ item }} "
            r"{% endfor %}"
        ),
        expect="1 2 3 x y z ",
        globals={},
    ),
    Case(
        description="continue with changing loop var",
        template=(
            r"{% for foo in array limit: 3 %}"
            r"{{ foo }} "
            r"{% endfor %}"
            r"{% for bar in array offset: continue %}"
            r"{{ bar }} "
            r"{% endfor %}"
        ),
        expect="1 2 3 1 2 3 4 5 6 ",
        globals={"array": [1, 2, 3, 4, 5, 6]},
    ),
    Case(
        description="nothing to continue from",
        template=(
            r"{% for item in array %}"
            r"a{{ item }} "
            r"{% endfor %}"
            r"{% for item in array offset: continue %}"
            r"b{{ item }} "
            r"{% endfor %}"
        ),
        expect="a1 a2 a3 a4 a5 a6 ",
        globals={"array": [1, 2, 3, 4, 5, 6]},
    ),
    Case(
        description="offset continue without preceding loop",
        template=r"{% for item in array offset: continue %}{{ item }} {% endfor %}",
        expect="1 2 3 4 5 6 ",
        globals={"array": [1, 2, 3, 4, 5, 6]},
    ),
    Case(
        description="continue from a limit that is greater than length",
        template=(
            r"{% for item in array limit: 99 %}"
            r"a{{ item }} "
            r"{% endfor %}"
            r"{% for item in array offset: continue %}"
            r"b{{ item }} "
            r"{% endfor %}"
        ),
        expect="a1 a2 a3 a4 a5 a6 ",
        globals={"array": [1, 2, 3, 4, 5, 6]},
    ),
    Case(
        description="continue from a range expression",
        template=(
            r"{% for item in (1..6) limit: 3 %}"
            r"a{{ item }} "
            r"{% endfor %}"
            r"{% for item in (1..6) offset: continue %}"
            r"b{{ item }} "
            r"{% endfor %}"
        ),
        expect="a1 a2 a3 b4 b5 b6 ",
        globals={"array": [1, 2, 3, 4, 5, 6]},
    ),
    Case(
        description="offset continue twice with limit",
        template=(
            r"{% for item in (1..6) limit: 2 %}"
            r"a{{ item }} "
            r"{% endfor %}"
            r"{% for item in (1..6) limit: 2 offset: continue %}"
            r"b{{ item }} "
            r"{% endfor %}"
            r"{% for item in (1..6) offset: continue %}"
            r"c{{ item }} "
            r"{% endfor %}"
        ),
        expect="a1 a2 b3 b4 c5 c6 ",
    ),
    Case(
        description="offset continue twice with changing limit",
        template=(
            r"{% for item in (1..6) limit: 2 %}"
            r"a{{ item }} "
            r"{% endfor %}"
            r"{% for item in (1..6) limit: 3 offset: continue %}"
            r"b{{ item }} "
            r"{% endfor %}"
            r"{% for item in (1..6) offset: continue %}"
            r"c{{ item }} "
            r"{% endfor %}"
        ),
        expect="a1 a2 b3 b4 b5 c6 ",
    ),
    Case(
        description="offset continue twice with no second limit",
        template=(
            r"{% for item in (1..6) limit: 2 %}"
            r"a{{ item }} "
            r"{% endfor %}"
            r"{% for item in (1..6) offset: continue %}"
            r"b{{ item }} "
            r"{% endfor %}"
            r"{% for item in (1..6) offset: continue %}"
            r"c{{ item }} "
            r"{% endfor %}"
        ),
        expect="a1 a2 b3 b4 b5 b6 ",
    ),
    Case(
        description="offset continue from a broken loop",
        template=(
            r"{% for item in (1..6) limit: 4 %}"
            r"{% if item == 3 %}{% break %}{% endif %}"
            r"a{{ item }} "
            r"{% endfor %}"
            r"{% for item in (1..6) offset: continue %}"
            r"b{{ item }} "
            r"{% endfor %}"
        ),
        expect="a1 a2 b5 b6 ",
    ),
    Case(
        description="offset continue from a broken loop with preceding limit",
        template=(
            r"{% for item in (1..6) limit: 3 %}"
            r"a{{ item }} "
            r"{% endfor %}"
            r"{% for item in (1..6) %}"
            r"{% if item == 3 %}{% break %}{% endif %}"
            r"b{{ item }} "
            r"{% endfor %}"
            r"{% for item in (1..6) offset: continue %}"
            r"c{{ item }} "
            r"{% endfor %}"
        ),
        expect="a1 a2 a3 b1 b2 ",
    ),
    Case(
        description="offset continue forloop length",
        template=(
            r"{% for item in (1..6) limit: 2 %}"
            r"a{{ item }} - {{ forloop.length }}, "
            r"{% endfor %}"
            r"{% for item in (1..6) offset: continue %}"
            r"b{{ item }} - {{ forloop.length }}, "
            r"{% endfor %}"
        ),
        expect="a1 - 2, a2 - 2, b3 - 4, b4 - 4, b5 - 4, b6 - 4, ",
    ),
    Case(
        description="parentloop is normally undefined",
        template=(r"{% for i in (1..2)%}{{ forloop.parentloop.index }}{% endfor %}"),
        expect="",
        globals={},
    ),
    Case(
        description="access parentloop",
        template=(
            r"{% for i in (1..2)%}"
            r"{% for j in (1..2) %}"
            r"{{ i }} {{j}} {{ forloop.parentloop.index }} {{ forloop.index }} "
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect="1 1 1 1 1 2 1 2 2 1 2 1 2 2 2 2 ",
        globals={},
    ),
    Case(
        description="parentloop goes out of scope",
        template=(
            r"{% for i in (1..2)%}"
            r"{% for j in (1..2) %}"
            r"{{ i }} {{ j }} "
            r"{% endfor %}"
            r"{{ forloop.parentloop.index }}"
            r"{% endfor %}"
        ),
        expect="1 1 1 2 2 1 2 2 ",
        globals={},
    ),
    Case(
        description="parent's parentloop",
        template=(
            r"{% for i in (1..2) %}"
            r"{% for j in (1..2) %}"
            r"{% for k in (1..2) %}"
            r"i={{ forloop.parentloop.parentloop.index }} "
            r"j={{ forloop.parentloop.index }} "
            r"k={{ forloop.index }} "
            r"{% endfor %}"
            r"{% endfor %}"
            r"{% endfor %}"
        ),
        expect=(
            "i=1 j=1 k=1 i=1 j=1 k=2 "
            "i=1 j=2 k=1 i=1 j=2 k=2 "
            "i=2 j=1 k=1 i=2 j=1 k=2 "
            "i=2 j=2 k=1 i=2 j=2 k=2 "
        ),
        globals={},
    ),
    Case(
        description="loop over an existing range object",
        template=(
            r"{% assign foo = (1..3) %}"
            r"{{ foo | join: '#' }}"
            r"{% for i in foo %}"
            r"{{ i }}"
            r"{% endfor %}"
            r"{% for i in foo %}"
            r"{{ i }}"
            r"{% endfor %}"
        ),
        expect="1#2#3123123",
        globals={},
    ),
    Case(
        description="loop over range with float start",
        template=r"{% assign x = (2.4..5) %}{% for i in x %}{{ i }}{% endfor %}",
        expect="2345",
        globals={},
    ),
    Case(
        description="share outer scope",
        template=(
            r"{% assign foo = 'hello' %}"
            r"{% for x in (1..3) %}"
            r"{% assign foo = x %}"
            r"{% endfor %}"
            r"{{ foo }}"
        ),
        expect="3",
        globals={},
    ),
    Case(
        description="offset and limit",
        template=r"{% for tag in tags limit: 3 offset: 1 %}{{ tag }} {% endfor %}",
        expect="garden home diy ",
        globals={"tags": ["sports", "garden", "home", "diy", "motoring", "fashion"]},
    ),
    Case(
        description="first and last with an offset and limit",
        template=(
            r"{% for tag in tags limit: 2 offset: 1 %}"
            r"{{ tag }} {{ forloop.first }} {{ forloop.last }} "
            r"{% endfor %}"
        ),
        expect="garden true false home false true ",
        globals={"tags": ["sports", "garden", "home", "diy", "motoring", "fashion"]},
    ),
    Case(
        description="first and last with offset continue",
        template=(
            r"{% for tag in product.tags limit: 1 %}"
            r"{% endfor %}"
            r"{% for tag in product.tags offset: continue %}"
            r"{{ forloop.first }} {{ forloop.last }} "
            r"{% endfor %}"
        ),
        expect="true false false false false false false false false true ",
        globals={
            "product": {
                "tags": ["sports", "garden", "home", "diy", "motoring", "fashion"]
            }
        },
    ),
    Case(
        description="range start and stop are the same",
        template=r"{% for i in (1..1) %}{{ i }} {% endfor %}",
        expect="1 ",
    ),
    Case(
        description="range start and stop are zero",
        template=r"{% for i in (0..0) %}{{ i }} {% endfor %}",
        expect="0 ",
    ),
    # Case(
    #     description="limit is a float",
    #     template=r"{% for i in (1..4) limit: 2.6 %}{{ i }} {% endfor %}",
    #     expect="",
    #     error=True,
    # ),
    # Case(
    #     description="offset is a float",
    #     template=r"{% for i in (1..4) offset: 2.6 %}{{ i }} {% endfor %}",
    #     expect="",
    #     error=True,
    # ),
    Case(
        description="limit is a string",
        template=r"{% for i in (1..4) limit: '2' %}{{ i }} {% endfor %}",
        expect="1 2 ",
    ),
    Case(
        description="offset is a string",
        template=r"{% for i in (1..4) offset: '2' %}{{ i }} {% endfor %}",
        expect="3 4 ",
    ),
    Case(
        description="limit is a non-number string",
        template=r"{% for i in (1..4) limit: 'foo' %}{{ i }} {% endfor %}",
        expect="",
        error=True,
    ),
    Case(
        description="offset is a non-number string",
        template=r"{% for i in (1..4) offset: 'foo' %}{{ i }} {% endfor %}",
        expect="",
        error=True,
    ),
    Case(
        description="limit is not a string or number",
        template=r"{% for i in (1..4) limit: foo %}{{ i }} {% endfor %}",
        expect="",
        globals={"foo": [1, 2, 3]},
        error=True,
    ),
    Case(
        description="offset is not a string or number",
        template=r"{% for i in (1..4) offset: foo %}{{ i }} {% endfor %}",
        expect="",
        globals={"foo": [1, 2, 3]},
        error=True,
    ),
    Case(
        description="comma separated arguments",
        template=r"{% for i in (1..6), limit: 4, offset: 2 %}{{ i }} {% endfor %}",
        expect="3 4 5 6 ",
        globals={},
    ),
    Case(
        description="some comma separated arguments",
        template=r"{% for i in (1..6) limit: 4, offset: 2, %}{{ i }} {% endfor %}",
        expect="3 4 5 6 ",
        globals={},
    ),
    Case(
        description="loop over a string literal",
        template=r"{% for i in 'hello' %}{{ i }} {% endfor %}",
        expect="hello ",
        globals={},
        future=True,
    ),
    Case(
        description="loop over a string variable",
        template=r"{% for i in foo %}{{ i }} {% endfor %}",
        expect="hello ",
        globals={"foo": "hello"},
        future=True,
    ),
]
