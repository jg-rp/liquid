"""Malformed template test cases."""
# pylint: disable=missing-class-docstring missing-function-docstring

from unittest import TestCase

from typing import Iterable
from typing import Dict
from typing import List
from typing import Union
from typing import NamedTuple
from typing import Type
from typing import Tuple

from liquid import Template
from liquid.environment import Environment
from liquid.mode import Mode

from liquid.exceptions import LiquidSyntaxError
from liquid.exceptions import FilterArgumentError
from liquid.exceptions import LiquidTypeError
from liquid.exceptions import lookup_warning
from liquid.exceptions import Error
from liquid.exceptions import TemplateNotFound
from liquid.exceptions import DisabledTagError
from liquid.exceptions import ContextDepthError

from liquid.extra import add_inline_expression_tags
from liquid.extra import add_extended_inline_expression_tags
from liquid.extra import IfNotTag

from liquid.loaders import DictLoader


class Case(NamedTuple):
    description: str
    template: str
    expect_exception: Union[Type[Error], Tuple[Type[Error], ...]]
    expect_msg: Union[str, List[str]]
    expect_render: str = ""

    @property
    def exceptions(self):
        if isinstance(self.expect_exception, tuple):
            return self.expect_exception
        return (self.expect_exception,)

    @property
    def warnings(self):
        return tuple(lookup_warning(e) for e in self.exceptions)


class MalformedTemplateTestCase(TestCase):
    """Malformed template test case."""

    def setUp(self):
        self.global_context = {
            "product": {
                "some-tags": ["hello", "there"],
                "tags": ["hello", "there"],
            },
            "tag": "goodbye",
        }

    def _test(self, test_cases: Iterable[Case], mode: Mode = Mode.STRICT):
        """Helper method for running lists of `Case`s in each render mode."""
        self._test_with_env(Environment(tolerance=mode), test_cases)

        # Test with non-standard conditional and boolean expressions
        env = Environment(tolerance=mode)
        env.add_tag(IfNotTag)
        add_inline_expression_tags(env)
        # Skip test cases that are not considered malformed with non-standard
        # expressions.
        self._test_with_env(
            env, [case for case in test_cases if "||" not in case.template]
        )

        # Same again for conditional expressions that support `not` and parens.
        add_extended_inline_expression_tags(env)
        self._test_with_env(
            env, [case for case in test_cases if "||" not in case.template]
        )

    def _test_with_env(self, env: Environment, test_cases: Iterable[Case]):
        for case in test_cases:
            with self.subTest(msg=case.description, mode=env.mode):
                if env.mode == Mode.STRICT:
                    with self.assertRaises(case.exceptions) as raised:
                        template = env.from_string(
                            case.template, globals=self.global_context
                        )
                        template.render()

                    if isinstance(case.expect_msg, list):
                        self.assertIn(str(raised.exception), case.expect_msg)
                    else:
                        self.assertEqual(str(raised.exception), case.expect_msg)

                elif env.mode == Mode.WARN:
                    with self.assertWarns(case.warnings):
                        template = env.from_string(
                            case.template, globals=self.global_context
                        )
                        template.render()
                elif env.mode == Mode.LAX:
                    template = env.from_string(
                        case.template, globals=self.global_context
                    )
                    result = template.render()
                    self.assertEqual(result, case.expect_render)

    def _test_partial(self, test_cases: Iterable[Case], templates: Dict[str, str]):
        """Helper method for testing lists of 'include' or 'render' cases."""
        env = Environment(loader=DictLoader(templates))
        for case in test_cases:
            with self.subTest(msg=case.description):
                with self.assertRaises(case.exceptions) as raised:
                    template = env.from_string(
                        case.template, globals=self.global_context
                    )
                    template.render()

                if isinstance(case.expect_msg, list):
                    self.assertIn(str(raised.exception), case.expect_msg)
                else:
                    self.assertEqual(str(raised.exception), case.expect_msg)

        env = Environment(loader=DictLoader(templates), tolerance=Mode.WARN)
        for case in test_cases:
            with self.subTest(msg=case.description):
                with self.assertWarns(case.warnings):
                    template = env.from_string(
                        case.template, globals=self.global_context
                    )
                    template.render()

        env = Environment(loader=DictLoader(templates), tolerance=Mode.LAX)
        for case in test_cases:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template, globals=self.global_context)
                result = template.render()
                self.assertEqual(result, case.expect_render)

    def test_liquid_syntax(self):
        """Test that we fail early and loud when parsing a malformed template."""

        test_cases = [
            Case(
                description="no expression",
                template="{% if %}foo{% endif %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="expected 'expression', found 'literal', on line 1",
            ),
            Case(
                description="end tag mismatch",
                template="{% if true %}foo{% endunless %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected tag 'endunless', on line 1",
            ),
            Case(
                description="unexpected outer tag name",
                template="{% foo true %}foo{% endfoo %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected tag 'foo', on line 1",
            ),
            Case(
                description="unexpected tag name inside block with line numbers",
                template=("Hello\n\n{% if true %}\n{% foo %}{% endfoo %}\n{% endif %}"),
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected tag 'foo', on line 4",
                expect_render="Hello\n\n",
            ),
            Case(
                description="missing tag name",
                template="{% %}foo{% end %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected tag '', on line 1",
            ),
            Case(
                description="missing end tag at EOF",
                template="{% if true %}foo{% assign bar = 'baz' %}",
                expect_exception=LiquidSyntaxError,
                expect_msg=(
                    "expected tag with value 'endif', found eof with value '', "
                    "on line 1"
                ),
            ),
            Case(
                description="orphaned break",
                template="{% break %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected 'break', on line 1",
            ),
            Case(
                description="orphaned continue",
                template="{% continue %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected 'continue', on line 1",
            ),
            Case(
                description="orphaned else",
                template="{% else %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected tag 'else', on line 1",
            ),
            Case(
                description="orphaned when",
                template="{% when %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected tag 'when', on line 1",
            ),
            Case(
                description="missing 'in' in forloop",
                template="{% for x (0..3) %}{{ x }}{% endfor %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="expected 'in', found '(', on line 1",
            ),
            Case(
                description="missing range or identifier in forloop",
                template="{% for x in %}{{ x }}foo{% endfor %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="invalid loop expression, on line 1",
            ),
            Case(
                description="float with trailing dot in range literal",
                template="{% for x in (2...4) %}{{ x }}{% endfor %}",
                expect_exception=LiquidSyntaxError,
                expect_msg=[
                    "invalid range expression, expected an integer, "
                    "found a dot, on line 1",
                    "unexpected '.' in range expression, on line 1",
                ],
            ),
            Case(
                description="chained identifier for loop variable",
                template="{% for x.y in (2...4) %}{{ x }}{% endfor %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="expected 'in', found '.', on line 1",
            ),
            Case(
                description="missing equal in assignment tag",
                template="{% assign x 5 %}",
                expect_exception=LiquidSyntaxError,
                expect_msg='invalid assignment expression "x 5", on line 1',
            ),
            Case(
                description="invalid subscript identifier",
                template="{{ foo[1.2] }}",
                expect_exception=LiquidSyntaxError,
                expect_msg=[
                    "invalid identifier, found float, on line 1",
                    "expected an identifier, found '1.2', on line 1",
                ],
            ),
            Case(
                description="nil subscript identifier",
                template="{{ foo[nil] }}",
                expect_exception=LiquidSyntaxError,
                expect_msg=[
                    "invalid identifier, found nil, on line 1",
                    "expected 'identifier', found 'nil', on line 1",
                    "expected ']', found 'nil', on line 1",
                ],
            ),
            Case(
                description="minus string",
                template="{{ -'foo' }}",
                expect_exception=(LiquidTypeError, LiquidSyntaxError),
                expect_msg=[
                    "unknown operator -'foo', on line 1",
                    "unexpected '-', on line 1",
                ],
            ),
            Case(
                description="unknown prefix operator",
                template="{{ +5 }}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected '+', on line 1",
            ),
            Case(
                description="float literal without a leading zero",
                template="{{ .1 }}",
                expect_exception=LiquidSyntaxError,
                expect_msg=[
                    "unknown prefix operator '.', on line 1",
                    "unexpected '.', on line 1",
                ],
            ),
            Case(
                description="unknown infix operator",
                template="{% if 1 =! 2 %}ok{% endif %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unknown operator '=!', on line 1",
            ),
            Case(
                description="bad 'unless' expression",
                template="{% unless 1 ~ 2 %}ok{% endunless %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected '~', on line 1",
            ),
            Case(
                description="bad conditional expression in unless block",
                template="{% unless true %}ok{% elsif £$! %}{% endunless %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected '£', on line 1",
            ),
            Case(
                description="unknown infix operator",
                template="{% if 1 ~ 2 %}ok{% endif %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected '~', on line 1",
            ),
            Case(
                description="bad alternative condition expression",
                template="{% if false %}ok{% elsif 1~=2 %}not ok{% endif %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected '~', on line 1",
            ),
            Case(
                description="junk in `liquid` tag",
                template="\n".join(
                    [
                        r"{{ 'hello' }}",
                        r"{% liquid",
                        r"echo 'foo'",
                        r"aiu34bseu",
                        r"%}",
                    ]
                ),
                expect_exception=LiquidSyntaxError,
                expect_render="hello\n",
                expect_msg="unexpected tag 'aiu34bseu', on line 4",
            ),
            Case(
                description="bad token in loop expression",
                template="{% for i$ in (1..3) %}{% endfor %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected '$', on line 1",
            ),
            Case(
                description="invalid loop argument",
                template=(
                    "{% for product in collections[0]['tags'] limit:| %}{% endfor %}"
                ),
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected '|', on line 1",
            ),
            Case(
                description="double pipe characters in filtered expression",
                template=r'{{ "failure" || upcase }}',
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected pipe or missing filter name, on line 1",
            ),
            Case(
                description="unexpected token between left value and filter",
                template=r'{{ "hello" boo || upcase }}',
                expect_exception=LiquidSyntaxError,
                expect_msg=(
                    "expected a filter or end of expression, found 'boo', on line 1"
                ),
            ),
            Case(
                description="unexpected token after left value and no filters",
                template=r'{{ "hello" offset:2 }}',
                expect_exception=LiquidSyntaxError,
                expect_msg=(
                    "expected a filter or end of expression, found 'offset', on line 1"
                ),
            ),
        ]

        self._test(test_cases, mode=Mode.STRICT)
        self._test(test_cases, mode=Mode.WARN)
        self._test(test_cases, mode=Mode.LAX)

    def test_liquid_syntax_from_template_api(self):
        """Test that syntax errors are raised by default when using the `Template`
        API."""
        with self.assertRaises(LiquidSyntaxError):
            # Missing colon before filter argument
            Template(r"{{ a | sort foo }}")

    def test_unrecoverable_syntax_errors(self):
        """Test that we fail early and loud when parsing a malformed template."""

        test_cases = [
            Case(
                description="single bracket close",
                template=r"text {{method} oh nos!",
                expect_exception=LiquidSyntaxError,
                expect_msg="expected '}}', found 'eof', on line 1",
            ),
            Case(
                description="single bracket close from tag sequence",
                template=r"text {%method} oh nos!",
                expect_exception=LiquidSyntaxError,
                expect_msg="expected '%}', found 'eof', on line 1",
            ),
        ]

        self._test(test_cases, mode=Mode.STRICT)

    def test_bad_include(self):
        """Test that we gracefully handle include errors."""

        test_cases = [
            Case(
                description="chained alias identifier",
                template=(
                    "{% include 'product.alt' with product['some-tags'] as foo.bar %}"
                ),
                expect_exception=LiquidSyntaxError,
                expect_msg="invalid identifier 'foo.bar', on line 1",
            ),
            Case(
                description="chained keyword identifier",
                template="{% include 'product.alt', foo.bar: 'hello' %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="invalid identifier 'foo.bar', on line 1",
            ),
            Case(
                description="template not found",
                template="{% include 'no/such/thing' %}",
                expect_exception=TemplateNotFound,
                expect_msg="template not found no/such/thing, on line 1",
            ),
            Case(
                description="template not found carry on",
                template="hello {% include 'no/such/thing' %}there",
                expect_exception=TemplateNotFound,
                expect_msg="template not found no/such/thing, on line 1",
                expect_render="hello there",
            ),
            Case(
                description="template name not a string or identifier",
                template="{% include 5 %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="expected identifier or string, found integer, on line 1",
            ),
            Case(
                description="missing keyword argument separator",
                template="{% include 'product.alt', foo: 5 bar: 6 %}",
                expect_exception=LiquidSyntaxError,
                expect_msg=(
                    "expected a comma separated list of arguments, "
                    "found identifier, on line 1"
                ),
            ),
            Case(
                description="bound expression is not an identifier",
                template="{% include 'product.alt' with 'foo' %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="expected 'identifier', found 'string', on line 1",
            ),
            Case(
                description="recursive include",
                template="{% include 'recursive.liquid' %}",
                expect_exception=ContextDepthError,
                expect_msg=(
                    "maximum context depth reached, "
                    "possible recursive include, on line 1"
                ),
            ),
        ]

        templates = {
            "product.alt": "{{ product }}",
            "recursive.liquid": "{% include 'inner.liquid' %}",
            "inner.liquid": "{% include 'recursive.liquid' %}",
        }

        self._test_partial(test_cases, templates)

    def test_bad_render(self):
        """Test that we gracefully handle render errors."""

        test_cases = [
            Case(
                description="break from render",
                template="".join(
                    [
                        r"{% assign greeting = 'good morning' %}",
                        r"{% for i in (1..3) %}",
                        r"{{ i }}",
                        r"{% render 'break' %}",
                        r"{{ i }}",
                        r"{% endfor %}",
                    ]
                ),
                expect_exception=LiquidSyntaxError,
                expect_msg="unexpected 'break', on line 1",
                expect_render="112233",
            ),
            Case(
                description="template name from identifier",
                template="{% render foo.bar %}",
                expect_exception=LiquidSyntaxError,
                expect_msg="expected 'string', found 'identifier', on line 1",
            ),
            Case(
                description="include will not render inside render",
                template="{% render 'include' %}",
                expect_exception=DisabledTagError,
                expect_msg="include usage is not allowed in this context, on line 1",
            ),
            Case(
                description="recursive render",
                template="{% render 'recursive.liquid' %}",
                expect_exception=ContextDepthError,
                expect_msg=(
                    "maximum context depth reached, "
                    "possible recursive render, on line 1"
                ),
            ),
            Case(
                description="arguments are not comma separated",
                template="{% render 'index', foo: 'foo' bar: 'bar' %}",
                expect_exception=LiquidSyntaxError,
                expect_msg=(
                    "expected a comma separated list of arguments, "
                    "found identifier, on line 1"
                ),
            ),
        ]

        templates = {
            "index": "hello",
            "break": "{% break %}",
            "include": "{% include 'foo' %}",
            "recursive.liquid": "{% render 'inner.liquid' %}",
            "inner.liquid": "{% render 'recursive.liquid' %}",
        }

        self._test_partial(test_cases, templates)

    def test_resume_block(self):
        """Test that we continue to execute a block after a single statement error."""
        source = (
            r"{% if true %}"
            r"before error "
            r"{% comment  %}"
            r"The following filter expression should throw a FilterArgumentError."
            r"{% endcomment %}"
            r"{{ 'foo' | upcase: bad }}"
            r"after error"
            r"{% endif %}"
        )

        env = Environment()

        # Confirm the exception is raised when in strict mode.
        env.mode = Mode.STRICT

        template = env.from_string(source)
        with self.assertRaises(FilterArgumentError):
            template.render()

        # Expect the template literal at the end of the block to render
        # after the filter argument error.
        env.mode = Mode.LAX
        result = template.render()
        self.assertEqual(result, "before error after error")

        # Same, but warn too.
        env.mode = Mode.WARN
        with self.assertWarns(lookup_warning(FilterArgumentError)):
            result = template.render()

        self.assertEqual(result, "before error after error")

    def test_invalid_identifiers(self):
        """Test that we gracefully handle invalid identifiers."""
        test_cases = [
            Case(
                description="unexpected character",
                template=r"{% assign foo+bar = 'hello there'%}{{ foo+bar }}",
                expect_exception=LiquidSyntaxError,
                expect_msg=(
                    "invalid assignment expression \"foo+bar = 'hello there'\", "
                    "on line 1"
                ),
            ),
            Case(
                description="unexpected chained assignment identifier",
                template=r"{% assign foo.bar = 'hello there' %}{{ foo.bar }}",
                expect_exception=LiquidSyntaxError,
                expect_msg=(
                    "invalid assignment expression \"foo.bar = 'hello there'\", "
                    "on line 1"
                ),
            ),
            Case(
                description="unexpected chained capture identifier",
                template=r"{% capture foo.bar %}{% endcapture %}",
                expect_exception=LiquidSyntaxError,
                expect_msg='invalid capture identifier "foo.bar", on line 1',
            ),
        ]

        self._test(test_cases, mode=Mode.STRICT)
        # self._test(test_cases, mode=Mode.WARN)
        # self._test(test_cases, mode=Mode.LAX)
