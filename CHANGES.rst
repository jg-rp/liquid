Python Liquid Change Log
========================

Version 1.4.0
--------------------------

**Features**

- ``StrictDefaultUndefined``, an undefined type that plays nicely with the ``default``
  filter, is now built in. (`docs <https://jg-rp.github.io/liquid/guides/undefined-variables#the-default-filter>`_)
- Configure resource limits with class attributes set on a Liquid ``Environment``. Those
  class attributes are ``context_depth_limit``, ``loop_iteration_limit``,
  ``local_namespace_limit`` and ``output_stream_limit``.
  (`docs <https://jg-rp.github.io/liquid/guides/resource-limits>`_)

**Fixes**

- Fixed a bug in ``StrictUndefined`` that, when extended, stopped if from looking at its
  own ``msg`` property. See #57.


Version 1.3.0
-------------

**Features**

- Allow render context customization by subclassing ``Context`` and ``BoundTemplate``.
- Contextual template analysis with ``BoundTemplate.analyze_with_context()``.
  Complementing static template analysis, released in version 1.2.0, contextual template
  analysis performs a template `render`, capturing information about template variable
  usage as it goes. (`docs <https://jg-rp.github.io/liquid/guides/contextual-template-analysis>`_)


Version 1.2.1
-------------

- Add ``typing-extensions`` dependency.

Version 1.2.0
-------------

**Features**

- New inline comment tag ``{% # .. %}``. See `Shopify Liquid PR #1498 <https://github.com/Shopify/liquid/pull/1498>`_
- Template static analysis. ``BoundTemplate.analyze()`` and ``BoundTemplate.analyze_async()``
  traverse a template's abstract syntax tree and report template variable usage. Static 
  tree traversal (without rendering or evaluating expressions) is supported by the new,
  optional ``children()`` methods of ``liquid.expression.Expression`` and ``liquid.ast.Node``.
  (`docs <https://jg-rp.github.io/liquid/guides/static-template-analysis>`_)

**Fixes**

- Fixed a bug where the lexer would incorrectly calculate an expression's line number
  if there were one or more newlines between a tag name and it's expression. Most 
  notable with ``liquid`` tags where it is common to put a newline immediately after
  "liquid".
- More robust syntax error handling when parsing Liquid expression filters. The 
  refactored expression lexers from version 1.1.3 failed to account for some classes of
  syntax error.

Version 1.1.7
-------------

- Fixed a bug where double pipe characters (``||``) in a filtered expression would cause
  an ``IndexError``. A ``LiquidSyntaxError`` is now raised in such cases, including the
  line number of the offending error.
- Changed ``Environment.fromString`` to catch unexpected parsing errors. A Liquid
  ``Error`` will now be raised with a message of "unexpected liquid parsing error"
  and its ``__cause__`` set to the offending exception.

Version 1.1.6
-------------

- Fixed a bug where the ``where`` filter would incorrectly ignore an explicit ``false``
  given as the target value. See #51.

Version 1.1.5
-------------

- Prioritise object properties and keys named ``size``, ``first`` and ``last`` over the
  special built-in properties of the same names. See #46.
- Fixed a bug with the ``uniq`` filter. It no longer raises an exception when given a 
  key argument and a sequence containing objects that don't have that key/property.
  See #47.
- The ``strip_html`` filter now removes ``style`` and ``script`` tag blocks in their
  entirety, including everything in between. See #45.
- Added ``remove_last`` and ``replace_last`` filters.

Version 1.1.4
-------------

- Lazy ``forloop`` helper variables. Don't calculate ``index``, ``rindex`` etc. unless
  accessed.
- Implemented ``forloop.name``, as per the reference implementation. ``forloop.name`` is
  the concatenation of the loop variable identifier and the target iterable identifier,
  or a string representation of a range literal, separated by a hyphen.
- Fixed a bug with the ``divided_by`` filter. Given a float value and integer argument,
  it was incorrectly doing integer division.
- Simplified ``tablerowloop`` and ``tablerow`` HTML generation.

Version 1.1.3
-------------

- Refactored expression lexers. New, subtly different, tag expression tokenizers are now
  in ``liquid.expressions``. Built-in tags use these lexers indirectly via new 
  specialized expression parsers. Older expression lexers and parsers will be maintained
  until at least Python Liquid version 2.0 for those that use them in custom tags.
  See #42.
- Specialized expression parsers. Each of the three built-in expression types now have a
  dedicated parser defined in ``liquid.expressions``, whereas before all expression
  parsing went through ``liquid.parse.ExpressionParser.parse_expression()``. Built-in
  tags now use these new parsers. The more general parser will be maintained until at
  least Python Liquid Version 2.0. See #42.
- ``liquid.parse.Parser.parse_block()`` now accepts any container as its ``end``
  argument. Benchmarks show that using a ``frozenset`` for ``end`` instead of a tuple
  gives a small performance improvement.
- Fixed an incompatibility with the reference implementation where Python Liquid would
  not recognize identifiers with a trailing question mark. This seems to be a common
  idiom in Ruby to indicate something returns a Boolean value.
- Added ``get_source_with_context()`` and ``get_source_with_context_async()`` to 
  ``liquid.loaders.BaseLoader``. Custom loaders can now use the active render context to
  dynamically modify their search space when used from ``include`` or ``render``, or any
  custom tag using ``Context.get_template_with_context()``.

  ``Context.get_template_with_context()`` also accepts arbitrary keyword arguments that
  are passed along to ``get_source_with_context()``. The build-in ``include`` and
  ``render`` tags add a ``tag`` argument with their tag name, so custom loaders can 
  modify their search space depending on which tag was used.

  See the `Custom Loaders <https://jg-rp.github.io/liquid/guides/custom-loaders>`_
  documentation for examples.

Version 1.1.2
-------------

- Fixed a bug where a for loop's limit would be incorrect when using
  ``offset: continue`` multiple times (three or more ``for`` tags looping over the same
  sequence). See #41.

Version 1.1.1
-------------
 
- Fixed a bug where blocks that contain whitespace only were being suppressed when the
  whitespace was explicitly output. Automatic whitespace suppression now only occurs in
  ``if``, ``unlesss`` and ``for`` blocks that don't contain an output statement or
  ``echo`` tag, even if the output itself is whitespace. See #38.
- Fixed a bug where the behavior of the special ``.first`` and ``.last`` properties did
  not match that of the ``first`` and ``last`` filters. Now, if given a string,
  ``.first`` and ``.last`` will return an undefined, and the ``first`` and ``last``
  filters will return ``None``. See #34.

Version 1.1.0
-------------

- Added new comment syntax. Disabled by default, enable shorthand comments with the
  ``template_comments`` argument to ``liquid.Template`` or ``liquid.Environment``.
  When ``True``, anything between ``{#`` and ``#}`` will be considered a comment.
- New expression cache. Distinct from the existing template cache, optionally cache
  common Liquid expression types (conditions, loops and filtered expressions) to
  avoid lexing and parsing the same expression multiple times.
- Fixed a bug where, in some cases, ``forloop.length`` would be incorrect when using
  ``offsset: continue`` in a loop expression.

Version 1.0.4
-------------

- A range literal will now use a default of ``0`` rather than raising a
  ``LiquidTypeError`` if either its start or stop values can't be cast to an integer.
- Gracefully handle ``liquid`` tags that are empty or only contain whitespace.
- Gracefully handle empty ``echo`` tags.

Version 1.0.3
-------------

- Explicit re-export
- Changed ``Context._tag_namespace`` to ``Context.tag_namespace``.

Version 1.0.2
-------------

- Fixed manifest error.

Version 1.0.1
-------------

- Added ``py.typed``

Version 1.0.0
-------------

Version bump. First stable release.

Version 0.11.1
--------------

- Template loaders can now include additional template meta data using the ``matter``
  argument of ``liquid.loaders.TemplateSource``. See the example
  ``FrontMatterFileSystemLoader`` in the README. See #32.
- Implemented ``ChoiceLoader``, a loader that tries to load a template from a list of
  loaders.
- Added a ``FileExtensionLoader``, a template loader that inherits from
  ``FileSystemLoader`` and automatically appends a file extension if one is missing.
- The built-in ``date`` filter now accepts the special input value of "today" as well as
  "now".
- The built-in ``truncate`` filter now has a default length of 50.
- The built-in ``truncatewords`` filter now has a default number of words of 15.
- Fixed a bug with the ``slice`` filter where it would return an empty string when
  presented with a negative start index and length that would have exceeded the length
  of the sequence. See #35.
- Drops can now define safe HTML string representations using a ``__html__`` method.
- Removed ``liquid.mode.error()`` in favour of ``liquid.Environment.error()``

Version 0.11.0
--------------

The following behavioral changes are the result of feedback gained from exporting Python
Liquid's "golden" test cases, and running them against Ruby Liquid (the reference
implementation). Both Python Liquid version 0.11.0 and Ruby Liquid version 5.1.0 pass
all tests currently defined in ``liquid/golden/``.

- Added support for comma separated ``when`` expressions. See #31.
- The built-in ``join``, ``concat``, ``where``, ``uniq`` and ``compact`` filters now use
  the new ``sequence_filter`` decorator. ``sequence_filter`` coerces filter left values
  to array-like objects. ``sequence_filter`` will also flatten nested array-like
  objects, just like the reference implementation.
- The built-in ``first``, ``last`` and ``map`` filters now operate on any array-like
  objects. Previously they were limited to lists and tuples. Strings still don't work.
- The built-in ``uniq`` and ``compact`` filters now accept an optional argument. If an
  argument is provided, it should be the name of a property and the left value should be
  a sequence of objects.
- The ``size`` filter now returns a default of ``0`` if its left value does not have a 
  ``__len__`` method.
- The ``replace`` and ``replace_first`` filters now treat undefined arguments as an
  empty string.
- The ``slice`` filter now works on lists, tuples and ranges, as well as strings.
- Fixed a bug where the ``math_filter`` decorator would cast strings representations of
  negative integers to a float rather than an int.
- Added golden test cases for all filters.


Version 0.10.2
--------------

- Moved and organized "render" test cases into importable "golden" test cases.
- Change ``RangeLiteral`` string representation to match the reference implementation.
- Add newlines to ``tablerow`` output. As per the reference implementation.

Version 0.10.1
--------------

- Range literals can now be assigned, compared and passed as arguments to ``include`` or
  ``render`` tags. They can also be filtered as if they were an array.
- Range literals will accept a float value for start and/or stop values. If a float is
  given for start or stop, it will be cast to an integer.
- Fixed a bug where the token stream would return the wrong token when peeking
  immediately after a push.

Version 0.10.0
--------------

- Changed named counter (``increment`` and ``decrement``) scoping. Unless a named
  counter is shadowed by an ``assign`` or ``capture``, the counter will be in scope for
  all subsequent Liquid expressions.
- Changed ``{% increment %}`` to be a post-increment operation. ``{% decrement %}``
  remains a pre-decrement operation.
- Added ``forloop.parentloop``. Access parent ``forloop`` objects from nested loops.

Version 0.9.1
-------------

- ``unless`` blocks can now contain ``else`` and ``elsif`` blocks.
- Added support for array item access with negative indices. Closes #27.
- Improved error messages for context lookups that resulting an ``IndexError`` or
  ``KeyError``.

Version 0.9.0
-------------

- Fixed a bug where arguments to ``Template()`` where not being passed to the implicit
  environment properly (again).
- Fixed a bug where some errors from the ``sort`` and ``map`` filters were being
  ignored. Those filters can now raise a ``FilterError``.
- Removed depreciated class-based filters.

Version 0.8.1
-------------

- Removed ``@abstractmethod`` from ``liquid.loaders.BaseLoader.get_source``. Custom
  loaders are now free to implement either ``get_source`` or ``get_source_async`` or
  both. The ``BaseLoader`` implementation of ``get_source`` simply raises a 
  ``NotImplementedError``.
- ``liquid.loaders.TemplateSource.uptodate`` (as returned by ``get_source`` and
  ``get_source_async``) can now be a coroutine function. This means async loaders can
  check a template's source for changes asynchronously.
- Added the ``cache_size`` argument to ``Environment`` and ``Template`` for controlling 
  the capacity of the default template cache.
- Easier subclassing of ``liquid.parser.ExpressionParser`` with ``END_EXPRESSION``.

Version 0.8.0
-------------

Version bump. Last release before removing depreciated class-based filters.

Version 0.7.8
-------------

- The ``default`` filter now uses ``__liquid__``, if available, when testing an object
  for truthy-ness.

Version 0.7.7
-------------

- Recursive use of the "render" tag now raises a ``ContextDepthError`` if
  ``MAX_CONTEXT_DEPTH`` is exceeded. This is now consistent with recursive "include".
- Drops (custom classes in a render context) can now mimic primitive Liquid values when
  used as array indexes or hash keys, or in conditional expressions (including 
  ``case``/``when`` and ``unless``). If defined, the result of calling a drop's
  ``__liquid__`` method will be used in those scenarios.
- Added ``base64_encode``, ``base64_decode``, ``base64_url_safe_encode`` and 
  ``base64_url_safe_decode`` filters.
- Added asynchronous template loading and rendering. When ``Template.render_async`` is
  awaited, ``render`` and ``include`` tags will load templates asynchronously. Custom 
  loaders should implement ``get_source_async``.
- Added support for asynchronous drops. If a class implements ``__getitem_async__``,
  which is assumed to be an async version of ``__getitem__``, it will be awaited instead
  of calling ``__getitem__``.

Version 0.7.6
-------------

- Class-based filters are now depreciated in favour of decorated filter functions. 
  Abstract filter classes (such as ``liquid.builtin.filters.string.StringFilter``) will
  be removed in Liquid 0.9.
- All built-in filters are now implemented as decorated functions. Legacy, class-based
  filters are no longer registered automatically and will be removed in Liquid 0.9.
- Legacy filter "helpers" are now depreciated and will be removed in Liquid 0.9. Use
  the new decorators, like ``liquid.filter.string_filter`` and
  ``liquid.filter.with_context``, instead.
- The ``block`` argument to the ``liquid.ast.ConditionalBlockNode`` constructor is no 
  longer optional.


Version 0.7.5
-------------

- Auto reload. Disable automatic reloading of templates by passing ``auto_reload=False``
  to ``Environment`` or ``Template``. For deployments where template sources don't
  change between service reloads, setting auto_reload to `False` can yield an increase
  in performance by avoiding calls to ``uptodate``.
- Fixed a bug where, when using the ``Template`` API, ``undefined``, ``strict_filters``,
  and ``autoescape`` where not always passed through to the implicit environment
  correctly.
- Added support for continuing a for loop using ``offset: continue``. See #14.

Version 0.7.4
-------------

.. _MarkupSafe: https://github.com/pallets/markupsafe

- HTML auto-escaping. If `MarkupSafe`_ is installed and the ``autoescape`` argument to
  ``Environment`` or ``Template`` is ``True``, context variables will be HTML escaped
  automatically.
- ``LiquidSyntaxError`` exceptions now include the offending template source in the
  ``source`` property.

Version 0.7.3
-------------

- The built-in ``FileSystemLoader`` now accepts a list of paths to search, in order,
  returning the first template source found. The ``search_path`` argument can be a
  string or path-like, or an iterable of strings or path-like objects.
- Added the ``encoding`` argument to ``FileSystemLoader``. Files will be opened with the
  given encoding. Defaults to ``"utf-8"``.
- ``FileSystemLoader`` will raise a ``TemplateNotFound`` exception if ``..`` appears in
  a template name.

Version 0.7.2
-------------

- Undefined variables are now represented by the ``Undefined`` type, or a subclass of 
  ``Undefined``. ``Undefined`` behaves like ``nil``, but can also be iterated over and
  indexed without error.
- Attempting to loop over an undefined variable no longer raises a ``LiquidTypeError``.
- Optionally pass ``liquid.StrictUndefined`` as the ``undefined`` argument to
  ``Template()`` or ``Environment()`` to render in `strict variables` mode. All
  operations on an instance of ``StrictUndefined`` raise an ``UndefinedError``.
- Filters can now raise ``FilterValueError`` in addition to ``FilterArgumentError``.
  Where a ``FilterValueError`` refers to an issue with the left value a filter is
  applied to.
- Applying a built-in filter to an undefined variable no longer raises a
  ``FilterArgumentError`` in most cases.
- Added the ``strict_filters`` argument to the ``Environment`` and ``Template``
  constructors. When ``True``, the default, undefined filters raise a
  ``NoSuchFilterFunc`` exception at render time. When ``False``, undefined filters are
  silently ignored.
- The ``join`` filter now forces items in its left value to strings before joining them.
- The ``join`` filter's argument is now optional, defaulting to a string containing a 
  single space.


Version 0.7.0
-------------

- New ``Template`` API. Create templates from strings without an ``Environment``.
- The ``template`` object is no longer included in every render context automatically.

Version 0.6.4
-------------

- Implemented the ``blank`` keyword. Empty string and strings containing only whitespace
  are equal to ``blank``.
- Implemented the ``null`` keyword. ``null`` is an alias for ``nil``.
- Implemented the ``ifchanged`` tag.

Version 0.6.2
-------------

- Refactored the standard expression parser. It's now possible to extend 
  ``ExpressionParser`` for use with custom tags.
- Decoupled boolean expression parsing for easier ``if``, ``unless`` and ``case`` tag
  subclassing.

Version 0.6.1
-------------

- Added support for Python 3.7 and PyPy3.7.


Version 0.6.0
-------------

- Added support for named filter parameters.
- The ``default`` filter now accepts the named parameter ``allow_false``.
- The ``truncate_words`` filter now forces a minimum number of words to 1.
- The ``newline_to_br`` filter now replaces ``\n`` and ``\r\n`` with ``<br />\n``.
- The ``strip_newlines`` filter strips ``\r\n``.
