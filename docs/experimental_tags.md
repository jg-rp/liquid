The tags described on this page are considered experimental and might change without warning and not follow semantic versioning.

## snippet

**_New in version 2.2.0_**

```plain
{% snippet <identifier> %}
  <liquid markup>
{% endsnippet %}
```

A snippet is a reusable block of Liquid markup. Traditionally we'd save a snippet to a file and include it in a template with the `{% render %}` tag.

```liquid
{% render  "some_snippet" %}
```

With the `{% snippet %}` tag we can define blocks for reuse inside a single template, potentially reducing the number of snippet files we need.

```liquid
{% snippet div %}
  <div>
    {{ content }}
  </div>
{% endsnippet %}
```

Defining a snippet does not render it. We use `{% render snippet_name %}` to render a snippet, where `snippet_name` is the name of your snippet without quotes (file-based snippet names must be quoted).

```liquid
{% snippet div %}
  <div>
    {{ content }}
  </div>
{% endsnippet %}

{% render div, content: "Some content" %}
{% render div, content: "Other content" %}
```

```html title="output"
<div>Some content</div>

<div>Other content</div>
```

Inline snippets share the same namespace as variables defined with `{% assign %}` and `{% capture %}`, so be wary of accidentally overwriting snippets with non-snippet data.

```liquid
{% snippet foo %}Hello{% endsnippet %}
{% foo = 42 %}
{% render foo %} {% # error %}
```

Snippets can be nested and follow the same scoping rules as file-based snippets.

```liquid
{% snippet a %}
  b
  {% snippet c %}
    d
  {% endsnippet %}
  {% render c %}
{% endsnippet %}

{% render a %}
{% render c %} {% # error, c is out of scope %}
```

Snippet blocks are bound to their names late. You can conditionally define multiple snippets with the same name and pick one at render time.

```liquid
{% if x %}
  {% snippet a %}b{% endsnippet %}
{% else %}
  {% snippet a %}c{% endsnippet %}
{% endif %}
{% render a %}
```
