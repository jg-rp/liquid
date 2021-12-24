# Comments

Using the standard [comment](/language/tags#comment) tag you can mark a block of template text as a comment. Python Liquid does not parse or render anything between `{% comment %}` and `{% endcomment %}`.

```liquid title="template"
{% comment %} Determine if the current product is on sale. {% endcomment %}
{% liquid
  if product.was_price
    assign on_sale = true
  else
    comment was_price is undefined
    endcomment
    assign on_sale = false
  endif
%}
```

:::caution
Python Liquid will raise a `LiquidSyntaxError` if it finds the string `{% endcomment %}` inside a
comment block. Ruby Liquid, on the other hand, will successfully parse fully-formed nested comment
blocks, but will fail to parse a comment block containing either an `{% comment %}` or
`{% endcomment %}` on its own.
:::

## Alternative Comment Syntax

**_New in version 1.1.0_**

Python Liquid offers an alternative, non-standard template comment syntax. When enabled, anything
between `{#` and `#}` will be treated as a comment. It is disabled by default. Enable it using the
[template_comments](/api/Environment#template_comments) argument to [liquid.Evironment](/api/Environment)
or [liquid.Template](/api/Template).

:::caution
This alternative comment syntax is non-standard. If you choose to use it in your templates, those
templates are unlikely to render correctly with other implementations of Liquid.
:::

```python
from liquid import Environment
env = Environment(template_comments=True)
```

Because this comment syntax is not implemented as a tag, there are no issues commenting out
arbitrary chunks of Liquid.

```plain title="template"
{# note: comment this out for now
  {% for x in (1..5) %}
    {{ x }}
  {% endfor %}
#}
```

Inside [liquid](/language/tags#liquid) tags any line starting with a hash is considered a comment.

```plain title="template"
{% liquid
  # greetings
  echo 'Hello, World!'
  # Multi line
  # comment
%}
```
