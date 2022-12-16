# Static Template Analysis

**_New in version 1.2.0_**

Use the [`analyze()`](../api/bound-template.md#analyze) or [`analyze_async()`](../api/bound-template.md#analyze_async) methods of a Liquid [`Template`](../api/bound-template.md) to traverse its abstract syntax tree and report template variable usage.

## All Template Variables

The object returned from `analyze()` is an instance of [`TemplateAnalysis`](../api/template-analysis.md). Its `variables` property is a dictionary mapping template variable names to a list of two-tuples. Each tuple is the template name and line number where the variable was found.

```python
from liquid import Template

template = Template("""\
{% assign people = "Sally, John, Brian, Sue" | split: ", " %}
{{ people }}
{% for name in people %}
    {{ forloop.index }} - {{ greeting }}, {{ name }}!
{% endfor %}
""")

analysis = template.analyze()
print(list(analysis.variables))

for name, location in analysis.variables.items():
    for template_name, line_number in location:
        print(f"'{name}' found in '{template_name}' on line {line_number}")
```

```plain title="output"
['people', 'forloop.index', 'greeting', 'name']
'people' found in '<string>' on line 2
'people' found in '<string>' on line 3
'forloop.index' found in '<string>' on line 4
'greeting' found in '<string>' on line 4
'name' found in '<string>' on line 4
```

**_New in version 1.6.0_**

Variable names - the keys of `TemplateAnalysis.variables`, and others - are a `str` subclass that includes a `parts` property, being a tuple representation of a variable's parts.

```python
from liquid import Template

template = Template("{{ data.some[thing['foo.bar']] }}")

for var, location in template.analyze().variables.items():
    for template_name, line_number in location:
        print(f"{var.parts} found in '{template_name}' on line {line_number}")
```

```plain title="output"
('data', 'some', ('thing', 'foo.bar')) found in '<string>' on line 1
('thing', 'foo.bar') found in '<string>' on line 1
```

## Global Template Variables

The `global_variables` property of [`TemplateAnalysis`](../api/template-analysis.md) is similar to `variables`, but only includes those variables that are not in scope from previous `assign` or `capture` tags, or added to a block's scope by a block tag.

```python
from liquid import Template

template = Template("""\
{% assign people = "Sally, John, Brian, Sue" | split: ", " %}
{{ people }}
{% for name in people %}
    {{ forloop.index }} - {{ greeting }}, {{ name }}!
{% endfor %}
""")

analysis = template.analyze()
print("all variables: ", list(analysis.variables))
print("global variables: ", list(analysis.global_variables))
```

```plain title="output"
all variables:  ['people', 'forloop.index', 'greeting', 'name']
global variables:  ['greeting']
```

While `greeting` is assumed to be global (that is, provided by application developers rather than a template author), Python Liquid knows that `forloop` is in scope for the duration of the `for` block. If `people` were referenced before being assigned, we'd see an entry in the `people` list for each location where it is out of scope.

```python
from liquid import Template

template = Template("""\
{{ people }}
{% assign people = "Sally, John, Brian, Sue" | split: ", " %}
{{ people }}
""")

analysis = template.analyze()

for name, location in analysis.global_variables.items():
    for template_name, line_number in location:
        print(f"'{name}' is out of scope in '{template_name}' on line {line_number}")
```

```plain title="output"
'people' is out of scope in '<string>' on line 1
```

## Local Template Variables

The `local_variables` property of [`TemplateAnalysis`](../api/template-analysis.md) is, again, a dictionary mapping template variable names to their locations. Each entry is the location of an `assign`, `capture`, `increment`, or `decrement` tag (or any custom tag that introduces names into the template local namespace) that initializes or updates the variable.

```python
from liquid import Template

template = Template("""\
{% assign people = "Sally, John, Brian, Sue" | split: ", " %}
{% assign people = "Bob, Frank" | split: ", " %}
""")

analysis = template.analyze()

for name, location in analysis.local_variables.items():
    for template_name, line_number in location:
        print(f"'{name}' assigned in '{template_name}' on line {line_number}")
```

```plain title="output"
'people' assigned in '<string>' on line 1
'people' assigned in '<string>' on line 2
```

## Analyzing Partial Templates

When the `follow_partials` argument to [`BoundTemplate.analyze()`](../api/bound-template.md#analyze) is `True` (the default), Python Liquid will attempt to load and analyze templates from `include` and `render` tags. In the case of `include`, this is only possible when the template name is a string literal.

```python
from pprint import pprint
from liquid import Environment, DictLoader

templates = {
    "layout": """\
        {% include 'nav', title: page_name %}
        {% render 'foot' with website as site_name %}
    """,
    "nav": "{{ title }} nav bar",
    "foot": "a footer for {{ site_name }}",
}

env = Environment(loader=DictLoader(templates))
layout = env.get_template("layout")

analysis = layout.analyze(follow_partials=True)
pprint(analysis.variables)
```

```plain title="output"
{'page_name': [('layout', 1)],
 'site_name': [('foot', 1)],
 'title': [('nav', 1)],
 'website': [('layout', 2)]}
```

When the `raise_for_failures` argument is `True` (the default), we should expect a [`TemplateTraversalError`](../api/exceptions.md#templatetraversalerror) to be raised if a partial template can not be loaded. If `raise_for_failures` is `False`, a dictionary of unloadable `include`/`render` tags is available as `TemplateAnalysis.unloadable_partials`.

```python
from liquid import Environment, DictLoader

templates = {
    "layout": """\
        {% include 'nav', title: page_name %}
        {% render 'foot' with website as site_name %}
    """,
}

env = Environment(loader=DictLoader(templates))
layout = env.get_template("layout")

analysis = layout.analyze(follow_partials=True, raise_for_failures=False)
print(analysis.unloadable_partials)
```

```plain title=output
{'foot': [('layout', 2)], 'nav': [('layout', 1)]}
```

## Analyzing Custom Tags

All built-in tags (the tag's `Node` and `Expression` classes) implement a `children()` method. When analyzing a custom tag that does not implement `children()`, and with the `raise_for_failures` argument set to `True` (the default), Python Liquid will raise a [`TemplateTraversalError`](../api/exceptions.md#templatetraversalerror). When `raise_for_failures` is `False`, a dictionary of unvisitable AST nodes and expressions is available as `TemplateAnalysis.failed_visits`.

```python
from liquid import Environment, DictLoader
from liquid.ast import Node
from liquid.tag import Tag

class ExampleNode(Node):
    def __init__(self, token: Token) -> None:
        self.tok = token

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        buffer.write("example node")

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        buffer.write("example node")


class ExampleTag(Tag):
    block = False
    name = "example"

    def parse(self, stream: TokenStream) -> Node:
        return ExampleNode(stream.current)


templates = {
    "layout": "{% example %}"
}

env = Environment(loader=DictLoader(templates))
env.add_tag(ExampleTag)
layout = env.get_template("layout")

analysis = layout.analyze(follow_partials=True, raise_for_failures=False)
print(analysis.failed_visits)
```

```plain title=output
{'ExampleNode': [('layout', 1)]}
```

`liquid.ast.Node.children()` should return a list of `liquid.ast.ChildNode` objects. Each `ChildNode` includes a child `Expression` and/or `Node`, plus any names the tag adds to the template local scope or subsequent block scope. Please see [liquid/builtin/tags](https://github.com/jg-rp/liquid/tree/main/liquid/builtin/tags) for examples.

`liquid.expression.Expression.children()` is expected to return a list of child `Expressions`. For example, `liquid.expression.RangeLiteral` returns a list containing expressions for its `start` and `stop` properties. Please see [liquid/expression.py](https://github.com/jg-rp/liquid/blob/main/liquid/expression.py) for examples.
