Static analysis
===============

Instances of :class:`liquid.Template` returned from :func:`liquid.parse`,
:meth:`liquid.Environment.parse` and :meth:`liquid.Environment.get_template` include
methods for inspecting template variable, tag and filter usage without rendering the
template.

Variables
---------

:meth:`liquid.Template.variables` and :meth:`liquid.Template.variables_async` return a
list of variables used in the template, without path segments. The list will include
variables that are local to the template (like those created with ``{% assign %}``) and
block scoped variables (like ``forloop``).

.. code-block:: python

    from liquid import parse

    source = """\
    Hello, {{ you }}!
    {% assign x = 'foo' | upcase %}

    {% for ch in x %}
        - {{ ch }}
    {% endfor %}

    Goodbye, {{ you.first_name | capitalize }} {{ you.last_name }}
    Goodbye, {{ you.first_name }} {{ you.last_name }}
    """

    template = parse(source)
    print(template.variables())
    # ['you', 'x', 'ch']

Paths
^^^^^

:meth:`liquid.Template.variable_paths` and :meth:`liquid.Template.variable_paths_async`
return a list of variables used in the template with their path segments.

.. code-block:: python

    # ... continued from above

    print(template.variable_paths())
    # ['you.last_name', 'you', 'ch', 'you.first_name', 'x']

Segments
^^^^^^^^

:meth:`liquid.Template.variable_segments` and :meth:`liquid.Template.variable_segments_async`
return a list of variables used in the template with their path segments as nested tuples.

.. code-block:: python

    # ... continued from above

    print(template.variable_segments())
    # [('you', 'last_name'), ('ch',), ('you', 'first_name'), ('x',), ('you',)]

Global variables
^^^^^^^^^^^^^^^^

:meth:`liquid.Template.global_variables`, :meth:`liquid.Template.global_variable_paths`,
and :meth:`liquid.Template.global_variable_segments` (and their async equivalents) are
similar to the methods described above, but exclude local and block scoped variables.

.. code-block:: python

    # ... continued from above

    print(template.global_variables())
    # ['you.last_name', 'you', 'ch', 'you.first_name', 'x']

    print(template.global_variable_paths())
    # ['you', 'you.first_name', 'you.last_name']

    print(template.global_variable_segments())
    # [('you',), ('you', 'last_name'), ('you', 'first_name')]

Filters and tags
----------------

:meth:`liquid.Template.filter_names` and :meth:`liquid.Template.tag_names` return the
names of filters and tags used in the template.

.. code-block:: python

    # ... continued from above

    print(template.filter_names())
    # ['upcase', 'capitalize']

    print(template.tag_names())
    # ['assign', 'for']

Comments and docs
-----------------

:meth:`liquid.Template.comments` and :meth:`liquid.Template.docs` return lists of comment
and ``DocTag`` nodes, respectively. All comment and doc nodes have ``token`` and ``text``
properties.

.. code-block:: python

    from liquid import parse

    source = """\
    {% doc %}
        some doc comment
    {% enddoc %}

    Hello!

    {% comment %}
        some comment
    {% endcomment %}

    {% if false %}
        {% # an inline comment %}
    {% endif %}
    """

    template = parse(source)

    print([node.text for node in template.comments()])
    # ['\n    some comment\n', ' an inline comment ']

    print([node.text for node in template.docs()])
    # ['\n    some doc comment\n']

Errors
------

:meth:`liquid.Template.errors` returns a list of ``ErrorNode`` and ``ErrorExpr`` instances.
Both have ``error`` properties containing a :class:`liquid.exceptions.LiquidSyntaxError`,
and a human readable string representation.

Note that ``errors`` will only be populated when using :ref:`lax-parsing`. Otherwise an
exception will have been raised before you get a ``Template`` instance.

.. code-block:: python

    from liquid import Environment, LaxLegacyParser

    env = Environment(parser=LaxLegacyParser)
    template = env.parse("{% if a b %}TRUE{% else %}FALSE{% endif %}")

    for err in template.errors():
        print(err)
