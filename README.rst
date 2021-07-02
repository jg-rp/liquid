
.. _reference documentation: https://shopify.github.io/liquid/
.. _reference implementation: https://github.com/Shopify/liquid
.. _dateutil: https://dateutil.readthedocs.io/en/stable/
.. _asyncpg: https://github.com/MagicStack/asyncpg


Python Liquid
=============

A Python implementation of `Liquid <https://shopify.github.io/liquid/>`_.
A non evaling templating language suitable for end users.

.. image:: https://img.shields.io/pypi/v/python-liquid.svg
    :target: https://pypi.org/project/python-liquid/
    :alt: Version

.. image:: https://github.com/jg-rp/liquid/actions/workflows/tests.yaml/badge.svg
    :target: https://github.com/jg-rp/liquid/tree/main/tests
    :alt: Tests

.. image:: https://img.shields.io/pypi/l/python-liquid.svg
    :target: https://pypi.org/project/python-liquid/
    :alt: Licence

.. image:: https://img.shields.io/pypi/pyversions/python-liquid.svg
    :target: https://pypi.org/project/python-liquid/
    :alt: Python versions

.. image:: https://img.shields.io/badge/pypy-3.7-blue
    :target: https://pypi.org/project/python-liquid/
    :alt: PyPy versions

    
- `Installing`_
- `Quick Start`_
- `API Reference <https://liquid.readthedocs.io/en/latest/api.html>`_
- `Related Projects`_
- `Compatibility`_
- `Benchmark`_
- `Async Support`_
- `Custom Filters`_
- `Custom Tags`_
- `Custom Loaders`_
- `Contributing`_


Installing
----------

Install and update using `pip <https://pip.pypa.io/en/stable/quickstart/>`_:

.. code-block:: text

    $ python -m pip install -U python-liquid


Quick Start
-----------

Please see `Shopify's documentation <https://shopify.github.io/liquid/>`_ for template
syntax and a reference of available tags and filters.

Render a template string by creating a ``Template`` and calling its ``render`` method.

.. code-block:: python

    from liquid import Template

    template = Template("Hello, {{ you }}!")
    print(template.render(you="World"))  # "Hello, World!"

Keyword arguments passed to ``render`` are added to the `render context`_, and are
available as variables for templates to use in Liquid expressions.


Loading Templates
*****************

If you want to use the built-in ``include`` or ``render`` tags, you'll need to create an 
``Environment``, with a template ``Loader``, then load and render templates from that
environment.

This example assumes a folder called ``templates`` exists in the current working
directory, and that the template file ``index.html`` exists within it.

.. code-block:: python

    from liquid import Environment
    from liquid import FileSystemLoader

    env = Environment(loader=FileSystemLoader("templates/"))

    template = env.get_template("index.html")
    print(template.render(some="variable", other="thing"))

You can create templates from strings using an ``Environment`` too. This is often more
efficient than using ``Template`` directly.

.. code-block:: python

    from liquid import Environment
    env = Environment()

    template = env.from_string("""
        <html>
        {% for i in (1..3) %}
          <p>hello {{ some }} {{ i }}</p>
        {% endfor %}
        </html>
    """)

    print(template.render(some="thing"))


Render Context
**************

Among other things, a render context includes namespaces for `global` variables passed
down from the ``Environment`` and `local` variables assigned with the built-in
``{% assign %}`` or ``{% capture %}`` tags.

The ``Environment`` constructor accepts ``globals``, a dictionary of variables made
available to all templates rendered from that environment. 

.. code-block:: python

    from liquid import Environment

    env = Environment(globals={"site_name": "Google"})

    template = env.from_string("""
        <html>
        <h1>{{ site_name }}</h1>
        {% for i in (1..3) %}
          <p>hello {{ some }} {{ i }}</p>
        {% endfor %}
        </html>
    """)

    print(template.render(some="thing"))

As does ``Template``, ``Environment.get_template`` and ``Environment.from_string``,
where the dictionary of variables is added to the resulting render context each time you
call ``render``.

.. code-block:: python

    from liquid import Environment

    env = Environment()

    template = env.get_template("index.html", globals={"page": "home"})
    print(template.render(some="thing"))


Strictness
**********

Templates are parsed and rendered in `strict` mode by default. Where syntax and
render-time type errors raise an exception as soon as possible. You can change the error
tolerance mode with the ``tolerance`` argument to the ``Environment`` or ``Template``
constructor.

Available modes are ``Mode.STRICT``, ``Mode.WARN`` and ``Mode.LAX``.

.. code-block:: python

    from liquid import Environment, FileSystemLoader, Mode

    env = Environment(
        loader=FileSystemLoader("templates/"),
        tolerance=Mode.LAX,
    )

By default, references to undefined variables are silently ignored. In
`strict variables` mode, any operation on an undefined variable will raise an
``UndefinedError``.

.. code-block:: python

    from liquid import Environment, StrictUndefined

    env = Environment(
        loader=FileSystemLoader("templates/"),
        undefined=StrictUndefined,
    )

HTML Auto Escape
****************

As of version 0.7.4, Python Liquid offers HTML auto-escaping. Where context variables
are automatically escaped on output. Install optional dependencies for auto-escaping
using the ``autoescape`` extra.

.. code-block:: text

    $ python -m pip install -U python-liquid[autoescape]

Auto-escaping is disabled by default. Enable it by setting the ``Environment`` or 
``Template`` ``autoescape`` argument to ``True``.

.. code-block:: python

    >>> from liquid import Environment
    >>> env = Environment(autoescape=True)
    >>> template = env.from_string("<p>Hello, {{ you }}</p>")
    >>> template.render(you='</p><script>alert("XSS!");</script>')
    '<p>Hello, &lt;/p&gt;&lt;script&gt;alert(&#34;XSS!&#34;);&lt;/script&gt;</p>'

Mark a string as "safe" by making it ``Markup``.

.. code-block:: python

    >>> from liquid import Environment, Markup
    >>> env = Environment(autoescape=True)
    >>> template = env.from_string("<p>Hello, {{ you }}</p>")
    >>> template.render(you=Markup("<em>World!</em>"))
    '<p>Hello, <em>World!</em></p>'

Alternatively use the non-standard ``safe`` filter.

.. code-block:: python

    >>> from liquid import Environment
    >>> env = Environment(autoescape=True)
    >>> template = env.from_string("<p>Hello, {{ you | safe }}</p>")
    >>> template.render(you="<em>World!</em>")
    '<p>Hello, <em>World!</em></p>'

Async Support
*************

Python Liquid supports loading and rendering templates asynchronously. When
``Template.render_async`` is awaited, ``render`` and ``include`` tags will load
templates asynchronously.

.. code-block:: python

    import asyncio
    from liquid import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader("templates/"))

    async def coro():
        template = await env.get_template_async("index.html")
        return await template.render_async(you="World")

    result = asyncio.run(coro())

Custom template loaders should implement ``get_source_async``. For example,
``AsyncDatabaseLoader`` will load templates from a PostgreSQL database using `asyncpg`_.

.. code-block:: python

  import datetime
  import functools

  import asyncpg

  from liquid import Environment
  from liquid.exceptions import TemplateNotFound
  from liquid.loaders import BaseLoader
  from liquid.loaders import TemplateSource


  class AsyncDatabaseLoader(BaseLoader):
      def __init__(self, pool: asyncpg.Pool) -> None:
          self.pool = pool

      def get_source(self, env: Environment, template_name: str) -> TemplateSource:
          raise NotImplementedError("async only loader")

      async def _is_up_to_date(self, name: str, updated: datetime.datetime) -> bool:
          async with self.pool.acquire() as connection:
              return updated == await connection.fetchval(
                  "SELECT updated FROM templates WHERE name = $1", name
              )

      async def get_source_async(
          self, env: Environment, template_name: str
      ) -> TemplateSource:
          async with self.pool.acquire() as connection:
              source = await connection.fetchrow(
                  "SELECT source, updated FROM templates WHERE name = $1", template_name
              )

          if not source:
              raise TemplateNotFound(template_name)

          return TemplateSource(
              source=source["source"],
              filename=template_name,
              uptodate=functools.partial(
                  self._is_up_to_date, name=template_name, updated=source["updated"]
              ),
          )

Custom "drops" can implement ``__getitem_async__``. If an instance of a drop that
implements ``__getitem_async__`` appears in a ``render_async`` context,
``__getitem_async__`` will be awaited instead of calling ``__getitem__``.

Most likely used for lazy loading objects from a database, an async drop would look
something like this.

.. code-block:: python

    class SomeAsyncDrop(abc.Mapping):
        def __init__(self, val):
            self.key = "foo"
            self.val = val

        def __len__(self):
            return 1

        def __iter__(self):
            return iter([self.key])

        def __getitem__(self, k):
            # Blocking IO here
            time.sleep(0.5)
            # ...

        async def __getitem_async__(self, k):
            # Do async IO here.
            asyncio.sleep(0.5)
            # ...
            

Related Projects
----------------

- `django-liquid <https://github.com/jg-rp/django-liquid>`_: A Django template backend
  for Liquid. Render Liquid templates in your Django apps.
- `Flask-Liquid <https://github.com/jg-rp/Flask-Liquid>`_: A Flask extension for Liquid.
  Render Liquid templates in your Flask applications.
- `python-liquid-extra <https://github.com/jg-rp/liquid-extra>`_: A growing collection
  of extra tags and filters for Python Liquid. Highlights of which are: 

  - an ``if`` tag that supports ``not`` and grouping with parentheses.
  - ``macro`` and ``call`` tags for defining and calling parameterized Liquid snippets.
  - a JSON encoding filter.

Compatibility
-------------

We strive to be 100% compatible with the `reference implementation`_ of Liquid, written
in Ruby. That is, given an equivalent render context, a template rendered with Python
Liquid should produce the same output as when rendered with Ruby Liquid.

Python Liquid faithfully reproduces the following tags.

- assign
- capture
- case/when
- comment
- cycle
- decrement
- echo
- for/break/continue
- ifchanged
- if/elsif/else
- include
- increment
- liquid
- raw
- render
- tablerow
- unless

Known Issues
************

`Please help by raising an issue if you notice an incompatibility.`

- Error handling. Python Liquid might not handle syntax or type errors in the same
  way as the reference implementation. We might fail earlier or later, and will 
  almost certainly produce a different error message.
  
- The built-in ``date`` filter uses `dateutil`_ for parsing strings to ``datetime``\s,
  and ``strftime`` for formatting. There are likely to be some inconsistencies between
  this and the reference implementation's equivalent parsing and formatting of dates and
  times.

Benchmark
---------

You can run the benchmark using ``make benchmark`` (or ``python -O performance.py`` if
you don't have ``make``) from the root of the source tree. On my ropey desktop computer
with a Ryzen 5 1500X, we get the following results.

.. code-block:: text

    Best of 5 rounds with 100 iterations per round and 60 ops per iteration (6000 ops per round).
    
    lex template (not expressions): 1.3s (4727.35 ops/s, 78.79 i/s)
                     lex and parse: 6.4s (942.15 ops/s, 15.70 i/s)
                            render: 1.7s (3443.62 ops/s, 57.39 i/s)
             lex, parse and render: 8.2s (733.30 ops/s, 12.22 i/s)

And PyPy3.7 gives us a decent increase in performance.

.. code-block:: text

    Best of 5 rounds with 100 iterations per round and 60 ops per iteration (6000 ops per round).

    lex template (not expressions): 0.58s (10421.14 ops/s, 173.69 i/s)
                     lex and parse: 2.9s (2036.33 ops/s, 33.94 i/s)
                            render: 1.1s (5644.80 ops/s, 94.08 i/s)
             lex, parse and render: 4.2s (1439.43 ops/s, 23.99 i/s)


On the same machine, running ``rake benchmark:run`` from the root of the reference
implementation source tree gives us these results.

.. code-block:: text

    /usr/bin/ruby ./performance/benchmark.rb lax

    Running benchmark for 10 seconds (with 5 seconds warmup).

    Warming up --------------------------------------
                 parse:     3.000  i/100ms
                render:     8.000  i/100ms
        parse & render:     2.000  i/100ms
    Calculating -------------------------------------
                 parse:     39.072  (± 0.0%) i/s -    393.000  in  10.058789s
                render:     86.995  (± 1.1%) i/s -    872.000  in  10.024951s
        parse & render:     26.139  (± 0.0%) i/s -    262.000  in  10.023365s

I've tried to match the benchmark workload to that of the reference implementation, so
that we might compare results directly. The workload is meant to be representative of
Shopify's use case, although I wouldn't be surprised if their usage has changed subtly
since the benchmark fixture was designed.

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


Custom Tags
-----------

Register a new tag with an ``Environment`` by calling its ``add_tag`` method. All tags
must  inherit from ``liquid.tag.Tag`` and implement its ``parse`` method.

``parse`` takes a single argument of type ``TokenStream`` that wraps an iterator of
``Token``\s, and returns an ``ast.Node`` instance. More often than not, a new subclass
of ``ast.node`` will accompany each ``Tag``. These ``Node``\s make up the parse tree,
and are responsible for writing rendered text to the output stream via the required
``render_to_output`` method.

Here's the implementation of ``UnlessTag``, which parses a boolean expression and a
block of statements before returning a ``UnlessNode``.

.. code-block:: python

    class UnlessTag(Tag):

        name = TAG_UNLESS
        end = TAG_ENDUNLESS

        def parse(self, stream: TokenStream) -> Node:
            parser = get_parser(self.env)

            expect(stream, TOKEN_TAG, value=TAG_UNLESS)
            tok = stream.current
            stream.next_token()

            expect(stream, TOKEN_EXPRESSION)
            expr_iter = tokenize_boolean_expression(stream.current.value)
            expr = parse_boolean_expression(TokenStream(expr_iter))

            stream.next_token()
            consequence = parser.parse_block(stream, ENDUNLESSBLOCK)

            expect(stream, TOKEN_TAG, value=TAG_ENDUNLESS)

            return UnlessNode(
                tok=tok,
                condition=expr,
                consequence=consequence
            )

Things worthy of note: 

- Block tags (those that have a start and end tag with any number of statements in
  between) are expected to leave the stream with their closing tag as the current token.

- The template lexer does not attempt to tokenize tag expressions. It is up to the
  ``Tag`` to tokenize and parse its expression, if any, possibly using or extending a
  built-in expression lexer found in ``liquid.lex``.

- The ``expect`` and ``expect_peek`` helper functions inspect tokens from the stream and
  raise an appropriate exception should a token's type or value not meet a tag's
  expectations.

- You can find parsers for common expression types in ``liquid.parse``, all of which
  return a ``liquid.expression.Expression``. ``Expression``\s have an
  ``evaluate(context)`` method for use from ``ast.Node.render_to_output``.


All built-in tags are implemented in this way, so have a look in
``liquid/builtin/tags/`` for examples. 

Custom Loaders
--------------

Write a custom loader class by inheriting from ``liquid.loaders.BaseLoader`` and
implementing its ``get_source`` method. Here we implement ``DictLoader``, a loader that
uses a dictionary of strings instead of the file system for loading templates.

.. code-block:: python

    from liquid.loaders import BaseLoader
    from liquid.loaders import TemplateSource
    from liquid.exceptions import TemplateNotFound

    class DictLoader(BaseLoader):
        def __init__(self, templates: Mapping[str, str]):
            self.templates = templates

        def get_source(self, _: Env, template_name: str) -> TemplateSource:
            try:
                source = self.templates[template_name]
            except KeyError as err:
                raise TemplateNotFound(template_name) from err

            return TemplateSource(source, template_name, None)

``TemplateSource`` is a named tuple containing the template source as a string, its name
and an optional ``uptodate`` callable. If ``uptodate`` is not ``None`` it should be a
callable that returns ``False`` if the template needs to be loaded again, or ``True``
otherwise.

You could then use ``DictLoader`` like this.

.. code-block:: Python

    from liquid import Environment
    from liquid.loaders import DictLoader

    snippets = {
        "greeting": "Hello {{ user.name }}",
        "row": """
            <div class="row"'
              <div class="col">
                {{ row_content }}
              </div>
            </div>
            """,
    }

    env = Environment(loader=DictLoader(snippets))
    
    template = env.from_string("""
        <html>
          {% include 'greeting' %}
          {% for i in (1..3) %}
            {% include 'row' with i as row_content %}
          {% endfor %}
        </html>
    """)

    print(template.render(user={"name": "Brian"}))

Contributing
------------

.. _Pylance: https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance
.. _Pyright: https://github.com/microsoft/pyright

- Install development dependencies with `Pipenv <https://github.com/pypa/pipenv>`_

- Python Liquid fully embraces type hints and static type checking. I like to use the
  `Pylance`_ extension for Visual Studio Code, which includes `Pyright`_ for static type
  checking.

- Format code using `black <https://github.com/psf/black>`_.

- Write tests using ``unittest.TestCase``.

- Run tests with ``make test`` or ``python -m unittest``.

- Check test coverage with ``make coverage`` and open ``htmlcov/index.html`` in your
  browser.

- Check your changes have not adversely affected performance with ``make benchmark``.
