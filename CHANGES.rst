Python Liquid Change Log
========================

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
  