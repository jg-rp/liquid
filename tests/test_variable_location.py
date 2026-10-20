from liquid import parse
from liquid.expressions import Variable
from liquid.tags import OutputStatement


def test_just_variable() -> None:
    template = parse("{{ some }}")
    node = template.nodes[0]
    assert isinstance(node, OutputStatement)
    expressions = node.expressions()
    assert len(expressions) == 1
    expr = expressions[0]
    assert isinstance(expr, Variable)
    assert expr.location() == ["some"]


def test_shorthand_name_selector() -> None:
    template = parse("{{ some.thing }}")
    node = template.nodes[0]
    assert isinstance(node, OutputStatement)
    expressions = node.expressions()
    assert len(expressions) == 1
    expr = expressions[0]
    assert isinstance(expr, Variable)
    assert expr.location() == ["some", "thing"]


def test_name_selector() -> None:
    template = parse("{{ some['other.thing'] }}")
    node = template.nodes[0]
    assert isinstance(node, OutputStatement)
    expressions = node.expressions()
    assert len(expressions) == 1
    expr = expressions[0]
    assert isinstance(expr, Variable)
    assert expr.location() == ["some", "other.thing"]


def test_variable_selector() -> None:
    template = parse("{{ some[other.thing] }}")
    node = template.nodes[0]
    assert isinstance(node, OutputStatement)
    expressions = node.expressions()
    assert len(expressions) == 1
    expr = expressions[0]
    assert isinstance(expr, Variable)
    assert expr.location() == ["some", ["other", "thing"]]


def test_nested_variable_selector() -> None:
    template = parse("{{ some[foo.bar[a.b]]['other.thing'] }}")
    node = template.nodes[0]
    assert isinstance(node, OutputStatement)
    expressions = node.expressions()
    assert len(expressions) == 1
    expr = expressions[0]
    assert isinstance(expr, Variable)
    assert expr.location() == ["some", ["foo", "bar", ["a", "b"]], "other.thing"]
