Liquid is a template language, where source text (the template) contains placeholders for variables, conditional expressions for including or excluding blocks of text, and loops for repeating blocks of text. Plus other syntax for manipulating variables and combining multiple templates into a single output.

Output text is the result of _rendering_ a template given some data model. It is that data model that provides the variables and objects referenced in a template's expressions.

Liquid is most commonly used with HTML or Markdown, but can be used with any text-based content. Consider this example template.

```liquid2
<main>
  <h2>{{ page_heading | default: "Welcome to Our Benchmark Test" }}</h2>
  <p>{{ intro_text | default: "This is a dynamically generated page." }}</p>

  {% # About us section }
  <section>
    <h3>About Us</h3>
    {% if site_description %}
      <p>{{ site_description }}</p>
    {% endif %}
  <section>

  <section>
    <h3>Items List</h3>
    {% assign items_size = items | size %}
    {% if items_size > 0 %}
      {% for item in items %}
        <div class="item">
          <h4>{{ item.title | capitalize }}</h4>
          <p>{{ item.description | escape }}</p>
          <p>Price: {{ item.price | ceil }} USD</p>

          {% if item.price > 50 %}
            <p>This is a premium item.</p>
            {% else %}
            <p>This is a budget-friendly item.</p>
          {% endif %}
        </div>
      {% endfor %}
    {% else %}
      <p>No items are available at the moment.</p>
    {% endif %}
  </section>
</main>
```

## Output

`{{ site_description }}` and `{{ item.title | capitalize }}` are examples of [output statements](tag_reference.md#output). Expressions surrounded by double curly braces, `{{` and `}}`, will be evaluated and the result inserted into the output text.

## Filters

`capitalize` in `{{ item.title | capitalize }}` and `ceil` in `{{ item.price | ceil }}` are examples of [filters](tag_reference.md#filters). Filters modify the expression to their left prior to output or assignment.

## Tags

`{% if site_description %}`, `{% endif %}` and `{% assign items_size = items | size %}` are examples of [tags](tag_reference.md). After the start tag delimiter (`{%`) there must be a tag name. Everything up to the closing tag delimiter (`%}`) is the tags's expression.

Not all tags accept an expression, but all tag must have a name.

Together `{% if site_description %}` and `{% endif %}` form a _block tag_. Block tags have an opening tag, some Liquid in between, and an end tag. In the case of the [`if tag`](tag_reference.md#if), the block is only rendered if the tag's expression evaluates to true.

`{% assign items_size = items | size %}` is an _inline tag_. It does not have an _end tag_ and it does not output anything, although some inline tags do produce an output.

## Comments

`{% # About us section %}` is an example of a [comment](tag_reference.md#comments). Text between `{% #` and `%}` will not be parsed or rendered.

## Content

`<main>` and `\n    <h3>About Us</h3>` are examples of template content. That's anything not inside `{%` and `%}` or `{{` and `}}`. With the exception of [whitespace control](whitespace_control.md), template content is output unchanged.
