.. _filters:

Templates Filters
=================

TODO:

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


If you want to add more complex filters, probably including some type checking and/or
casting, or the filter needs access to the active context or environment, you'll want to
inherit from ``Filter`` and implement its ``__call__`` method.

.. code-block:: python

  from liquid.filter import Filter
  from liquid.filter import string_required

  class LinkToTag(Filter):

    name = "link_to_tag"
    with_context = True

    @string_required
    def __call__(self, label, tag, *, context):
        handle = context.resolve("handle", default="")
        return (
            f'<a title="Show tag {tag}" href="/collections/{handle}/{tag}">{label}</a>'
        )

And register it wherever you create your environment.

.. code-block:: python

  from liquid import Environment, FileSystemLoader
  from myfilters import LinkToTag

  env = Environment(loader=FileSystemLoader("templates/"))
  env.add_filter(LinkToTag.name, LinkToTag(env))

In a template, you could then use the ``LinkToTag`` filter like this.

.. code-block::

    {% if tags %}
        <dl class="navbar">
        <dt>Tags</dt>
            {% for tag in collection.tags %}
            <dd>{{ tag | link_to_tag: tag }}</dd>
            {% endfor %}
        </dl>
    {% endif %}

Note that the ``Filter`` constructor takes a single argument, a reference to the
environment, which is available to ``Filter`` methods as ``self.env``. The class
variable ``name`` is used by the ``string_required`` decorator (and all other helpers/
decorators found in ``liquid.filter``) to give informative error messages.

All built-in filters are implemented in this way, so have a look in ``liquid/builtin/\
filters/`` for many more examples.