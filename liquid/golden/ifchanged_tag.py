"""Golden tests cases for testing liquid's `ifchanged` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="changed from initial state",
        template=r"{% ifchanged %}hello{% endifchanged %}",
        expect="hello",
    ),
    Case(
        description="not changed from initial state",
        template=r"{% ifchanged %}{% endifchanged %}",
        expect="",
    ),
    Case(
        description="no change from assign",
        template=(
            r"{% assign foo = 'hello' %}"
            r"{% ifchanged %}{{ foo }}{% endifchanged %}"
            r"{% ifchanged %}{{ foo }}{% endifchanged %}"
        ),
        expect="hello",
    ),
    Case(
        description="change from assign",
        template=(
            r"{% assign foo = 'hello' %}"
            r"{% ifchanged %}{{ foo }}{% endifchanged %}"
            r"{% ifchanged %}{{ foo }}{% endifchanged %}"
            r"{% assign foo = 'goodbye' %}"
            r"{% ifchanged %}{{ foo }}{% endifchanged %}"
        ),
        expect="hellogoodbye",
    ),
    Case(
        description="within for loop",
        template=(
            r'{% assign list = "1,3,2,1,3,1,2" | split: "," | sort %}'
            r"{% for item in list -%}"
            r"{%- ifchanged %} {{ item }}{% endifchanged -%}"
            r"{%- endfor %}"
        ),
        expect=" 1 2 3",
    ),
]
