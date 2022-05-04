"""Test cases for shorthand comment syntax."""
# pylint: disable=missing-class-docstring

from dataclasses import dataclass
from unittest import TestCase

from typing import List
from typing import Type
from typing import Union

from liquid import Environment
from liquid import Template
from liquid import Mode


@dataclass
class Case:
    description: str
    template: str
    expect: Union[str, Type[Exception]]


class ShorthandCommentTestCase(TestCase):
    def _test(
        self,
        test_cases: List[Case],
        template_comments=False,
        comment_start_string="{#",
        comment_end_string="#}",
    ) -> None:
        """Table driven test runner."""
        for case in test_cases:
            with self.subTest(msg=case.description, env=True):
                env = Environment(
                    tolerance=Mode.STRICT,
                    template_comments=template_comments,
                    comment_start_string=comment_start_string,
                    comment_end_string=comment_end_string,
                )

                template = env.from_string(case.template)
                result = template.render()
                self.assertEqual(result, case.expect)

            # Test using the Template API too.
            with self.subTest(msg=case.description, Template=True):
                template = Template(
                    case.template,
                    tolerance=Mode.STRICT,
                    template_comments=template_comments,
                    comment_start_string=comment_start_string,
                    comment_end_string=comment_end_string,
                )
                result = template.render()
                self.assertEqual(result, case.expect)

    def test_no_shorthand_comment_syntax(self):
        """Test that a default environment does not support shorthand comment syntax."""
        test_cases = [
            Case(
                description="shorthand comments are disbled",
                template=r"Hello, {# this is a comment #} World!",
                expect="Hello, {# this is a comment #} World!",
            ),
        ]

        self._test(test_cases)

    def test_shorthand_comment_syntax(self):
        """Test that shorthand comments are ignored."""
        test_cases = [
            Case(
                description="shorthand comments are ignored",
                template=r"Hello, {# this is a comment #} World!",
                expect="Hello,  World!",
            ),
            Case(
                description="shorthand comments must have a trailing hash.",
                template=r"Hello, {# this is not a comment } World!",
                expect="Hello, {# this is not a comment } World!",
            ),
            Case(
                description="shorthand comments can contain tags and statements",
                template=r"Hello, {# this is {% if %} a {{ comment }} #} World!",
                expect="Hello,  World!",
            ),
            Case(
                description="liquid expression line comments are ignored",
                template="\n".join(
                    (
                        r"{% liquid ",
                        r"if true",
                        r"echo 'foo'",
                        r"endif",
                        r"# this is a comment",
                        r"%}",
                    )
                ),
                expect="foo",
            ),
        ]

        self._test(test_cases, template_comments=True)

    def test_shorthand_comment_whitespace_control(self):
        """Test that shorthand comments can use whitespace control."""
        test_cases = [
            Case(
                description="shorthand comments can remove trailing whitespace",
                template=r"Hello, {# this is a comment -#} World!",
                expect="Hello, World!",
            ),
            Case(
                description="shorthand comments can remove leading whitespace",
                template=r"Hello, {#- this is a comment #} World!",
                expect="Hello, World!",
            ),
        ]

        self._test(test_cases, template_comments=True)

    def test_different_start_and_end_sequence(self):
        """Test that we can change the comment start and end sequence."""
        test_cases = [
            Case(
                description="shorthand comments are ignored",
                template="Hello, {// this is a comment //} World!",
                expect="Hello,  World!",
            ),
            Case(
                description="shorthand comments must have a valid end sequence.",
                template=r"Hello, {// this is not a comment } World!",
                expect="Hello, {// this is not a comment } World!",
            ),
            Case(
                description="shorthand comments can contain tags and statements",
                template=r"Hello, {// this is {% if %} a {{ comment }} //} World!",
                expect="Hello,  World!",
            ),
            Case(
                description="liquid expression line comments are ignored",
                template="\n".join(
                    (
                        r"{% liquid ",
                        r"if true",
                        r"echo 'foo'",
                        r"endif",
                        r"// this is a comment",
                        r"%}",
                    )
                ),
                expect="foo",
            ),
        ]

        self._test(
            test_cases,
            template_comments=True,
            comment_start_string="{//",
            comment_end_string="//}",
        )
