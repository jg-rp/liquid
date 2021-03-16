
Python Liquid
=============

A Python implementation of `Liquid <https://shopify.github.io/liquid/>`_.
A non evaling templating language suitable for end users.

- `Installing`_
- `Quick Start`_
- `Related Projects`_
- `Compatibility`_
- `Benchmark`_
- `Custom Filters`_
- `Custom Tags`_
- `Custom Loaders`_
- `Contributing`_


Installing
----------

Install and update using `pip <https://pip.pypa.io/en/stable/quickstart/>`_:

.. code-block:: text

    $ python -m pip install -U python-liquid

Liquid requires Python>=3.7 or PyPy3.7.


Quick Start
-----------

Please see `Shopify's documentation <https://shopify.github.io/liquid/>`_ for template
syntax and a reference of available tags and filters.

An application typically creates a single ``Environment``, with a template ``Loader``, 
then loads and renders templates from that environment. This example assumes a folder
called ``templates`` exists in the current working directory, and that the template file
``index.html`` exists within it.

.. code-block:: python

    from liquid import Environment, FileSystemLoader

    env = Environment(loader=FileSystemLoader("templates/"))
    template = env.get_template("index.html")

    print(template.render(some="variable", other="thing"))

Keyword arguments passed to the ``render`` method of a ``Template`` are made available
for templates to use in template statements and expressions.

A ``Loader`` is only required if you plan to use the built-in ``include`` or ``render``
tags. You could instead create a ``Template`` directly from a string.

.. code-block:: python

    from liquid import Environment

    env = Environment()

    template = env.from_string("""
        <html>
        {% for i in (1..3) %}
            hello {{ some }} {{ i }}
        {% endfor %}
        </html>
    """)

    print(template.render(some="variable", other="thing"))

The ``Environment`` constructor and ``get_template`` method of an environment also accept
``globals``, a dictionary of variables made available to all templates rendered from
the environment or for each call to ``render``, respectively.

.. code-block:: python

    from liquid import Environment, FileSystemLoader

    env = Environment(
        loader=FileSystemLoader("templates/"),
        globals={"site_name": "Google"},
    )

    template = env.get_template(
        "index.html",
        globals={"title": "Home Page"},
    )

    print(template.render(some="variable", other="thing"))


Templates are parsed and rendered in `strict` mode by default, where syntax and render-time
type errors raise an exception as soon as possible. You can change the error tolerance mode
with the ``tolerance`` argument to the ``Environment`` constructor.

Available modes are ``Mode.STRICT``, ``Mode.WARN`` and ``Mode.LAX``.

.. code-block:: python

    from liquid import Environment, FileSystemLoader, Mode

    env = Environment(
        loader=FileSystemLoader("templates/"),
        tolerance=Mode.LAX,
    )


Related Projects
----------------

- `Flask-Liquid <https://github.com/jg-rp/Flask-Liquid>`_: A Flask extension for Liquid. Render
  Liquid templates in your Flask applications.
- `python-liquid-extra <https://github.com/jg-rp/liquid-extra>`_: A growing collection of extra
  tags and filters for Python Liquid. For example, an ``if`` tag that supports ``not`` and grouping
  with parentheses.

Compatibility
-------------

We strive to be 100% compatible with the reference implementation of Liquid, written in Ruby.
That is, given an equivalent render context, a template rendered with Python Liquid should
produce the same output as when rendered with Ruby Liquid.

Known Issues
************

`Please help by raising an issue if you notice an incompatibility.`

- Error handling. Python Liquid might not handle syntax or type errors in the same
  way as the reference implementation. We might fail earlier or later, and will 
  almost certainly produce a different error message.
  
- The built-in ``date`` filter uses `dateutils <https://dateutil.readthedocs.io/en/stable/>`_
  for parsing strings to ``datetime``\s, and ``strftime`` for formatting. There are likely to
  be some inconsistencies between this and the reference implementation's equivalent parsing 
  and formatting of dates and times.

Benchmark
*********

You can run the benchmark using ``make benchmark`` (or ``python -O performance.py`` if you
don't have ``make``) from the root of the source tree. On my ropey desktop computer with a 
Ryzen 5 1500X, we get the following results.

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


On the same machine, running ``rake benchmark:run`` from the root of the reference implementation
source tree gives us these results.

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

I've tried to match the benchmark workload to that of the reference implementation, so that
we might compare results directly. The workload is meant to be representative of Shopify's 
use case, although I wouldn't be surprised if their usage has changed subtly since the 
benchmark fixture was designed.

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


If you want to add more complex filters, probably including some type checking and/or casting,
or the filter needs access to the active context or environment, you'll want to inherit from
``Filter`` and implement its ``__call__`` method.

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

Note that the ``Filter`` constructor takes a single argument, a reference to the environment,
which is available to ``Filter`` methods as ``self.env``. The class variable ``name`` is used by
the ``string_required`` decorator (and all other helpers/decorators found in ``liquid.filter``)
to give informative error messages.

All built-in filters are implemented in this way, so have a look in ``liquid/builtin/filters/``
for many more examples.


Custom Tags
-----------

Register a new tag with an ``Environment`` by calling its ``add_tag`` method. All tags must 
inherit from ``liquid.tag.Tag`` and implement its ``parse`` method.

``parse`` takes a single argument of type ``TokenStream`` that wraps an iterator of ``Token``\s,
and returns an ``ast.Node`` instance. More often than not, a new subclass of ``ast.node`` will
accompany each ``Tag``. These ``Node``\s make up the parse tree, and are responsible for writing
rendered text to the output stream via the required  ``render_to_output`` method.

Here's the implementation of ``UnlessTag``, which parses a boolean expression and a block of
statements before returning a ``UnlessNode``.

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

- Block tags (those that have a start and end tag with any number of statements in between)
  are expected to leave the stream with their closing tag as the current token.

- The template lexer does not attempt to tokenize tag expressions. It is up to the ``Tag``
  to tokenize and parse its expression, if any, possibly using or extending a built-in
  expression lexer found in ``liquid.lex``.

- The ``expect`` and ``expect_peek`` helper functions inspect tokens from the stream and
  raise an appropriate exception should a token's type or value not meet a tag's expectations.

- You can find parsers for common expression types in ``liquid.parse``, all of which return
  a ``liquid.expression.Expression``. ``Expression``\s have an ``evaluate(context)`` method
  for use from ``ast.Node.render_to_output``.


All built-in tags are implemented in this way, so have a look in ``liquid/builtin/tags/``
for examples. 

Custom Loaders
--------------

Write a custom loader class by inheriting from ``liquid.loaders.BaseLoader`` and implementing
its ``get_source`` method. Here we implement ``DictLoader``, a loader that uses a dictionary
of strings instead of the file system for loading templates.

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

``TemplateSource`` is a named tuple containing the template source as a string, its name and an
optional ``uptodate`` callable. If ``uptodate`` is not ``None`` it should be a callable that
returns ``False`` if the template needs to be loaded again, or ``True`` otherwise.

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

- Install development dependencies with `Pipenv <https://github.com/pypa/pipenv>`_

- Python Liquid fully embraces type hints and static type checking. I like to use the
  `Pylance <https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance>`_ 
  extension for Visual Studio Code, which includes `Pyright <https://github.com/microsoft/pyright>`_
  for static type checking.

- Format code using `black <https://github.com/psf/black>`_.

- Write tests using ``unittest.TestCase``.

- Run tests with ``make test`` or ``python -m unittest``.

- Check test coverage with ``make coverage`` and open ``htmlcov/index.html`` in your browser.

- Check your changes have not adversely affected performance with ``make benchmark``.
