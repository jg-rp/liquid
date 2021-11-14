"""Golden tests cases for testing liquid's `cycle` tag."""

from liquid.golden.case import Case

cases = [
    Case(
        description="no identifier",
        template=(
            r"{% cycle 'some', 'other' %}"
            r"{% cycle 'some', 'other' %}"
            r"{% cycle 'some', 'other' %}"
        ),
        expect="someothersome",
    ),
    Case(
        description="with identifier",
        template=(
            r"{% cycle 'foo': 'some', 'other' %}"
            r"{% cycle 'some', 'other' %}"
            r"{% cycle 'foo': 'some', 'other' %}"
        ),
        expect="somesomeother",
    ),
    Case(
        description="different items",
        template=(
            r"{% cycle '1', '2', '3' %}"
            r"{% cycle '1', '2' %}"
            r"{% cycle '1', '2', '3' %}"
        ),
        expect="112",
    ),
    Case(
        description="integers",
        template=r"{% cycle 1, 2, 3 %}{% cycle 1, 2, 3 %}{% cycle 1, 2, 3 %}",
        expect="123",
    ),
]
