Python Liquid Change Log
========================

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
  