# Whitespace Suppression

Block tags that, when rendered, contain only whitespace are suppressed by default.

```python
from liquid import Template

template = Template("Hello{% if true %}\n\n{% endif %}World!")
print(template.render())
```

```plain title="output"
HelloWorld!
```

That is unless the block contains an output statement (`{{ .. }}`) or `{% echo %}` tag, even if the result of that output is whitespace only.

```python
from liquid import Template

template = Template("Hello{% if true %}{{ '\n\n' }}{% endif %}World!")
print(template.render())
```

```plain title="output"
Hello

World!
```

## Disabling Whitespace Suppression

**_New in version 1.10.0_**

Automatic suppression of whitespace only blocks can be disabled by subclassing [`liquid.Environment`](../api/environment.md) and setting the class attribute `render_whitespace_only_blocks` to `True`. Templates rendered from such an environment will output blocks that contain whitespace only.

```python
from liquid import Environment

class MyEnvironment(Environment):
    render_whitespace_only_blocks = True

env = MyEnvironment()
template = env.from_string("Hello{% if true %}\n\n{% endif %}World!")
print(template.render())
```

```plain title="output"
Hello

World!
```

## Selective Whitespace Suppression

**_New in version 1.10.0_**

`render_whitespace_only_blocks` affects all block tags. You can disable automatic whitespace suppression for one or more tags by registering custom versions of those tags with the `force_output` class attribute set to `True`.

This example disables whitespace suppression for `{% unless %}` tags, but keeps it active for `{% for %}`, `{% if %}` and `{% case %}` tags.

```python
from liquid import Environment
from liquid.builtin.tags.unless_tag import UnlessNode
from liquid.builtin.tags.unless_tag import UnlessTag

class MyUnlessNode(UnlessNode):
    force_output = True


class MyUnlessTag(UnlessTag):
    node_class = MyUnlessNode


env = Environment()
env.add_tag(MyUnlessTag)

template = env.from_string(
    "{% for x in (1..3) %}"
    "{{ x }}"
    "{% unless forloop.last %}\n{% endunless %}"
    "{% endfor %}"
)

result = template.render() # "1\n2\n3"
```
