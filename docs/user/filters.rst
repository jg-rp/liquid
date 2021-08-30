.. _filters:
.. _Shopify's documentation: https://shopify.github.io/liquid/

Template Filters
================

All built-in filters are registered automatically with every new
:class:`liquid.Environment`. :attr:`liquid.Environment.filters` is a normal python
dictionary mapping filter names (the string you would use in a template to apply a
filter) to filter functions (see `Custom Filters`_).

Please see `Shopify's documentation`_ for a filter function reference. Those built-in
filters are:

- abs
- at_most
- at_least
- ceil
- divided_by
- floor
- minus
- plus
- round
- times
- modulo
- capitalize
- append
- downcase
- escape
- escape_once
- lstrip
- newline_to_br
- prepend
- remove
- remove_first
- replace
- replace_first
- slice
- split
- upcase
- strip
- rstrip
- strip_html
- strip_newlines
- truncate
- truncatewords
- url_encode
- url_decode
- base64_encode
- base64_decode
- base64_url_safe_encode
- base64_url_safe_decode
- join
- first
- last
- concat
- map
- reverse
- sort
- sort_natural
- where
- uniq
- compact
- size
- default
- date

Non-Standard Filters
--------------------

Built-in filters that don't appear in the Liquid reference implementation.

Safe (Auto Escape)
******************

The non-standard ``safe`` filter is used to mark context variables as "safe". Meaning 
they don't need HTML escaping when :attr:`liquid.Environment.autoescape` is set to
``True``.

If the ``safe`` filter appears in a template rendered from and ``Environment`` without
HTML auto-escaping enabled, the filter has no effect.


Custom Filters
--------------

Add a custom template filter to an ``Environment`` by calling its ``add_filter`` method.
A filter can be any callable that accepts at least one argument (the result of the left 
hand side of a filtered expression), and returns a string or object with a ``__str__``
method.

Here's a simple example of adding ``str.endswith`` as a filter function.

.. code-block:: python

  from liquid import Environment, FileSystemLoader

  env = Environment(loader=FileSystemLoader("templates/"))
  env.add_filter("endswith", str.endswith)

And use it like this.

.. code-block:: text

    {% assign foo = "foobar" | endswith: "bar" %}
    {% if foo %}
        <!-- do something -->
    {% endif %}


Decorate filter functions with ``with_context`` or ``with_environment`` to have the 
active context or environment passed as a keyword arguments.

.. code-block:: python

  from liquid.filter import with_context
  from liquid.filter import string_filter

  @string_filter
  @with_context
  def link_to_tag(label, tag, *, context):
      handle = context.resolve("handle", default="")
      return (
          f'<a title="Show tag {tag}" href="/collections/{handle}/{tag}">{label}</a>'
      )

And register it wherever you create your environment.

.. code-block:: python

  from liquid import Environment, FileSystemLoader
  from myfilters import link_to_tag

  env = Environment(loader=FileSystemLoader("templates/"))
  env.add_filter("link_to_tag", link_to_tag)

In a template, you could then use the ``link_to_tag`` filter like this.

.. code-block::

    {% if tags %}
        <dl class="navbar">
        <dt>Tags</dt>
            {% for tag in collection.tags %}
            <dd>{{ tag | link_to_tag: tag }}</dd>
            {% endfor %}
        </dl>
    {% endif %}

All built-in filters are implemented in this way, so have a look in
``liquid/builtin/filters/`` for many more examples.

Note that old style, class-based filters are depreciated and will be removed in Liquid
0.9. You can still implement custom filters as callable classes, but Liquid will not
include any abstract base classes for filters or legacy filter "helpers".
