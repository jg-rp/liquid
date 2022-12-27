# Tag Analysis

**_New in version 1.7.0_**

Use [`Environment.analyze_tags()`](../api/environment.md#analyze_tags), [`Environment.analyze_tags_async()`](../api/environment.md#analyze_tags_async) or [`Environment.analyze_tags_from_string()`](../api/environment.md#analyze_tags_from_string) to analyze template source text and report tag usage and issues.

Unlike [static template analysis](./static-template-analysis.md), which also includes tag usage, _tag analysis_ operates on tokens generated from template source text, before creating an abstract syntax tree. This give us the opportunity to find unknown, unexpected and unbalanced tags that might cause the parser to raise an exception or skip template blocks.

:::info
Because this form of tag analysis happens before a template is fully parsed, it will never attempt to load and analyze partial templates from `{% include %}` or `{% render %}` tags. Nor is it able to count template variables and filters, like [`BoundTemplate.analyze()`](./static-template-analysis.md) does.
:::

## Tags

The object returned from `analyze_tags()` is an instance of [`TagAnalysis`](../api/tag-analysis.md). Its `tags` property is a dictionary mapping tag names to a list of `(template_name, line_number)` tuples, one tuple for each occurrence of the tag. `TagAnalysis.tags` includes unknown tags, but excludes "end" and _inner_ tags (`else` and `break` in this example).

```python
from liquid import Environment

env = Environment()

tag_analysis = env.analyze_tags_from_string(
    """\
{% for foo in bar %}
    {% if foo %}
        {{ foo | upcase }}
    {% else %}
        {% break %}
    {% endif %}
{% endfor %}
"""
)

print(tag_analysis.tags)
# {'for': [('<string>', 1)], 'if': [('<string>', 2)]}
```

## All Tags

The `all_tags` property of `TagAnalysis` is a mapping of tag names to their locations, including "end" tags and inner tags.

```python
from pprint import pprint
from liquid import Environment

env = Environment()

tag_analysis = env.analyze_tags_from_string(
    """\
{% for foo in bar %}
    {% if foo %}
        {{ foo | upcase }}
    {% endif %}
{% endfor %}
"""
)

pprint(tag_analysis.all_tags)
# {'endfor': [('<string>', 5)],
#  'endif': [('<string>', 4)],
#  'for': [('<string>', 1)],
#  'if': [('<string>', 2)]}
```

## Unclosed Tags

The `unclosed_tags` property of `TagAnalysis` includes the names and locations of block tags that do not have a matching "end" tag.

```python
from liquid import Environment

env = Environment()

tag_analysis = env.analyze_tags_from_string(
    """\
{% for foo in bar %}
    {% if foo %}
        {{ foo | upcase }}
    {% endif %}
"""
)

print(tag_analysis.unclosed_tags)
# {'for': [('<string>', 1)]}
```

## Unexpected Tags

The `unexpected_tags` property of `TagAnalysis` includes the names and locations of _inner_ tags that do not have an appropriate enclosing block tag. Like an `{% else %}` appearing outside an `{% if %}` or `{% unless %}` block, for example.

:::caution
`unexpected_tags` does not handle the possibility of an "inner" tag appearing in a partial template (using `{% include %}`), where an appropriate enclosing block is in a parent template.
:::

```python
from liquid import Environment

env = Environment()

tag_analysis = env.analyze_tags_from_string(
    """\
{% for foo in bar %}
  {{ foo }}
{% endfor %}
{% break %}
"""
)

print(tag_analysis.unexpected_tags)
# {'break': [('<string>', 4)]}
```

## Unknown Tags

`TagAnalysis.unknown_tags` contains the names and locations of tags that are not registered with the environment. If there's an unregistered block tag, only the tag starting the block will be reported. In the case of an "end" tag typo, the "end" tag will be reported as "unknown" and the start tag will be in [`unclosed_tags`](#unclosed_tags).

```python
from liquid import Environment

env = Environment()

tag_analysis = env.analyze_tags_from_string(
    """\
{% form article %}
  <h2>Leave a comment</h2>
  <input type="submit" value="Post comment" id="comment-submit" />
{% endform %}
"""
)

print(tag_analysis.unknown_tags)
# {'form': [('<string>', 1)]}
```
