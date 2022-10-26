"""Golden tests cases for testing liquid's built-in `truncatewords` filter."""

from liquid.golden.case import Case

cases = [
    Case(
        description="default end",
        template=r'{{ "Ground control to Major Tom." | truncatewords: 3 }}',
        expect="Ground control to...",
    ),
    Case(
        description="custom end",
        template=r'{{ "Ground control to Major Tom." | truncatewords: 3, "--" }}',
        expect="Ground control to--",
    ),
    Case(
        description="no end",
        template=r'{{ "Ground control to Major Tom." | truncatewords: 3, "" }}',
        expect="Ground control to",
    ),
    Case(
        description="fewer words than word count",
        template=r'{{ "Ground control" | truncatewords: 3 }}',
        expect="Ground control",
    ),
    Case(
        description="not a string",
        template="{{ 5 | truncatewords: 10 }}",
        expect="5",
    ),
    Case(
        description="too many arguments",
        template='{{ "hello" | truncatewords: 5, "foo", "bar" }}',
        expect="",
        error=True,
    ),
    Case(
        description="reference implementation test 1",
        template=r'{{ "测试测试测试测试" | truncatewords: 5 }}',
        expect="测试测试测试测试",
    ),
    Case(
        description="reference implementation test 2",
        template=r'{{ "one two three" | truncatewords: 2, 1 }}',
        expect="one two1",
    ),
    Case(
        description="reference implementation test 3",
        template='{{ "one  two\tthree\nfour" | truncatewords: 3 }}',
        expect="one two three...",
    ),
    Case(
        description="reference implementation test 4",
        template=r'{{ "one two three four" | truncatewords: 2 }}',
        expect="one two...",
    ),
    Case(
        description="reference implementation test 5",
        template=r'{{ "one two three four" | truncatewords: 0 }}',
        expect="one...",
    ),
    Case(
        description="undefined left value",
        template=r"{{ nosuchthing | truncatewords: 5 }}",
        expect="",
    ),
    Case(
        description="undefined first argument",
        template=r'{{ "one two three four" | truncatewords: nosuchthing }}',
        expect="",
        error=True,
    ),
    Case(
        description="undefined second argument",
        template=r'{{ "one two three four" | truncatewords: 2, nosuchthing }}',
        expect="one two",
    ),
    # Case(
    #     description="very big argument",
    #     template=r'{{ "" | truncatewords: 100000000000000 }}',
    #     expect="",
    #     error=False,
    # ),
    Case(
        description="number of words defaults to 15",
        template=r'{{ "a b c d e f g h i j k l m n o p q" | truncatewords }}',
        expect="a b c d e f g h i j k l m n o...",
    ),
    Case(
        description="all whitespace is clobbered",
        template=r'{{ "    one    two three    four  " | truncatewords: 2 }}',
        expect="one two...",
    ),
]
