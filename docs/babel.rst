Internationalization and localization
=====================================

This page covers i18n and l10n filter and tag configuration, and how we support
translations and translation message catalogs.

Currency
--------

The ``currency`` filter returns the input number formatted as currency for the current
locale. For usage examples see ```currency`` <optional_filters.md#currency>`__ in the
filter reference.

Options
^^^^^^^

``currency`` defaults to looking for a locale in a render context variable called
``locale``, and a currency code in a render context variable called ``currency_code``. It
outputs in the locale's standard format and falls back to ``en_US`` and ``USD`` if those
context variables don't exist.

.. code-block:: python

   from liquid import parse

   template = parse("{{ 100457.99 | currency }}")

   print(template.render())
   print(template.render(currency_code="GBP"))
   print(template.render(locale="de", currency_code="CAD"))

.. code-block:: text

   $100,457.99
   £100,457.99
   100.457,99 CA$

To configure ``currency``, register a new instance of
```Currency`` <api/extra.md#liquid.extra.Currency>`__ with an
```Environment`` <environment.md#managing-tags-and-filters>`__, then render your templates
from that. See `the API reference <api/extra.md#liquid.extra.Currency>`__ for details of
all arguments accepted by ``Currency``.

.. code-block:: python

   from liquid.extra import Currency
   from liquid import Environment

   env = Environment()
   env.filters["currency"] = Currency(default_locale="de")

Money
^^^^^

For convenience, some “money” filters are defined that mimic Shopify's money filter
behavior. These are instances of ```Currency()`` <api/extra.md#liquid.extra.Currency>`__
with specific default formats. All other currency options are set to their defaults.

.. code-block:: python

   from liquid import parse

   template = parse("""\
   {% assign amount = 10 %}
   {{ amount | money }}
   {{ amount | money_with_currency }}
   {{ amount | money_without_currency }}
   {{ amount | money_without_trailing_zeros }}""")

   print(template.render(currency_code="CAD", locale="en_CA"))

.. code-block:: text

   $10.00
   $10.00 CAD
   10.00
   $10

DateTime
--------

The ``datetime`` filter returns the input *datetime* formatted for the current locale. For
usage examples see ```datetime`` <optional_filters.md#datetime>`__ in the filter
reference.

.. _options-1:

Options
^^^^^^^

``datetime`` defaults to looking for a timezone in a render context variable called
``timezone``, a locale in a render context variable called ``locale`` and a datetime
format in a render context variable called ``datetime_format``.

.. code-block:: python

   from liquid import parse

   template = parse("{{ 'Apr 1, 2007, 3:30:00 PM' | datetime }}")

   print(template.render())
   print(template.render(locale="de", datetime_format="long"))
   print(template.render(locale="de", timezone="CET", datetime_format="short"))

.. code-block:: text

   Apr 1, 2007, 3:30:00 PM
   1. April 2007 um 15:30:00 UTC
   01.04.07, 17:30

To configure ``datetime``, register a new instance of
```DateTime`` <api/extra.md#liquid.extra.DateTime>`__ with an
```Environment`` <environment.md#managing-tags-and-filters>`__, then render your templates
from that. See `the API reference <api/extra.md#liquid.extra.DateTime>`__ for details of
all arguments accepted by ``DateTime``.

.. code-block:: python

   from liquid.extra import DateTime
   from liquid import Environment

   env = Environment()
   env.filters["datetime"] = DateTime(timezone_var="tz")

Decimal
-------

The ``decimal`` filter returns the input number formatted as a decimal for the current
locale. For usage examples see ```decimal`` <optional_filters.md#decimal>`__ in the filter
reference.

.. _options-2:

Options
^^^^^^^

``decimal`` defaults to looking for a locale in a render context variable called
``locale``. It uses the locale's standard format and falls back to ``en_US`` if that
variable does not exist.

.. code-block:: python

   from liquid import parse

   # Parse a number from a string in the default (en_US) input locale.
   template = parse("""\
   {{ '10,000.23' | decimal }}
   {{ '10,000.23' | decimal: group_separator: false }}
   """)

   print(template.render(locale="de"))
   print(template.render(locale="en_GB"))

.. code-block:: text

   10.000,23
   10000,23

   10,000.23
   10000.23

To configure ``decimal``, register a new instance of
```Number`` <api/extra.md#liquid.extra.Number>`__ with an
```Environment`` <environment.md#managing-tags-and-filters>`__, then render your templates
from that.

.. code-block:: python

   from liquid.extra import Number
   from liquid import Environment

   env = Environment()
   env.filters["decimal"] = Number(default_locale="en_GB")

Unit
----

The ``unit`` filter returns he input number formatted with the given units according to
the current locale. For usage examples see ```unit`` <optional_filters.md#unit>`__ in the
filter reference.

.. _options-3:

Options
^^^^^^^

``unit`` defaults to looking for a locale in a render context variable called ``locale``,
a length in a render context variable called ``unit_length``, and a decimal format in a
render context variable called ``unit_format``.

.. code-block:: python

   from liquid import parse

   template = parse("""\
   {{ 12 | unit: 'length-meter', format: '#,##0.00' }}
   {{ 150 | unit: 'kilowatt', denominator_unit: 'hour' }}
   """)

   print(template.render(unit_length="long"))
   print(template.render(locale="de", unit_length="long"))

.. code-block:: text

   12.00 meters
   150 kilowatts per hour

   12,00 Meter
   150 Kilowatt pro Stunde

To configure ``unit``, register a new instance of
```Unit`` <api/extra.md#liquid.extra.Unit>`__ with an
```Environment`` <environment.md#managing-tags-and-filters>`__, then render your templates
from that.

.. code-block:: python

   from liquid.extra import Unit
   from liquid import Environment

   env = Environment()
   env.filters["unit"] = Unit(locale_var="_locale")

Translations
------------

Liquid Babel includes ```gettext`` <optional_filters.md#gettext>`__,
```ngettext`` <optional_filters.md#ngettext>`__,
```pgettext`` <optional_filters.md#pgettext>`__ and
```npgettext`` <optional_filters.md#npgettext>`__ filter equivalents to the functions
found in `Python's gettext
module <https://docs.python.org/3.10/library/gettext.html#gnu-gettext-api>`__. Application
developers can choose to use any of these filters, possibly using more user friendly
filter names, and/or the more general ```t (translate)`` <optional_filters.md#t>`__
filter.

The ```t`` <optional_filters.md#t>`__ filter can behave like any of the \*gettext filters,
depending on the arguments it is given. Where the \*gettext filters require positional
arguments for ``context``, ``count`` and ``plural``, ``t`` reserves optional ``count`` and
``plural`` keyword arguments.

Liquid Babel also offers a ```{% translate %}`` <optional_tags.md#translate>`__ tag. This
is similar to the
```{% trans %}`` <https://jinja.palletsprojects.com/en/3.1.x/templates/#i18n>`__ tag found
in Jinja or the
```{% blocktranslate %}`` <https://docs.djangoproject.com/en/4.1/topics/i18n/translation/#blocktranslate-template-tag>`__
tag found in Django's template language. Again, application developers can configure and
customize the included ``translate`` tag to suit an application's needs.

Filters
^^^^^^^

```gettext`` <optional_filters.md#gettext>`__,
```ngettext`` <optional_filters.md#ngettext>`__,
```npgettext`` <optional_filters.md#npgettext>`__,
```pgettext`` <optional_filters.md#pgettext>`__ and ```t`` <optional_filters.md#t>`__
filters all default to looking for `translations <#message-catalogs>`__ in a render
context variable called ``translations``, falling back to an instance of
```NullTranslations`` <https://docs.python.org/3.10/library/gettext.html#the-nulltranslations-class>`__
if ``translations`` can not be resolved.

.. code-block:: python

   from liquid import parse

   # You'll need to load an appropriate Translations object.
   # `get_translations()` is defined elsewhere.
   translations = get_translations(locale="de")

   template = parse("{{ 'Hello, World!' | t }}")
   print(template.render(translations=translations))  # Hallo Welt!

To configure ```gettext`` <optional_filters.md#gettext>`__,
```ngettext`` <optional_filters.md#ngettext>`__,
```npgettext`` <optional_filters.md#npgettext>`__,
```pgettext`` <optional_filters.md#pgettext>`__ or ```t`` <optional_filters.md#t>`__,
register a new instance of ```GetText`` <api/extra.md#liquid.extra.GetText>`__,
```NGetText`` <api/extra.md#liquid.extra.NGetText>`__,
```NPGetText`` <api/extra.md#liquid.extra.NPGetText>`__,
```PGetText`` <api/extra.md#liquid.extra.PGetText>`__ or
```Translate`` <api/extra.md#liquid.extra.Translate>`__ with an
```Environment`` <environment.md#managing-tags-and-filters>`__, then render your templates
from that. All of these classes inherit from
```BaseTranslateFilter`` <api/extra.md#liquid.extra.BaseTranslateFilter>`__ and accept the
same constructor arguments.

Message catalogs
^^^^^^^^^^^^^^^^

By default, all translation filters and tags will look for a render context variable
called ``translations``, which must be an object implementing the ``Translations``
protocol. It is the application developer's responsibility to provide a ``Translations``
object, being the interface between Liquid and a message catalog.

The ``Translations`` protocol is defined as follows. It is simply a subset of the
```NullTranslations`` <https://docs.python.org/3.10/library/gettext.html#gettext.NullTranslations>`__
class found in the `gettext
module <https://docs.python.org/3.10/library/gettext.html#gnu-gettext-api>`__.

.. code-block:: python

   class Translations(Protocol):
       def gettext(self, message: str) -> str: ...

       def ngettext(self, singular: str, plural: str, n: int) -> str: ...

       def pgettext(self, context: str, message: str) -> str: ...

       def npgettext(self, context: str, singular: str, plural: str, n: int) -> str: ...

It could be a
```GNUTranslations`` <https://docs.python.org/3.10/library/gettext.html#the-gnutranslations-class>`__
instance, a `Babel
``Translations`` <https://babel.pocoo.org/en/latest/support.html#extended-translations-class>`__
instance, or any object implementing ``gettext``, ``ngettext``, ``pgettext`` and
``npgettext`` methods.

Message variables
^^^^^^^^^^^^^^^^^

Translatable message text can contain placeholders for variables. When using variables in
strings to be translated by filters, variables are defined using percent-style formatting.
Only the ``s`` modifier is supported and every variable must have a name. In this example
``you`` is the variable name.

.. code-block:: liquid2

   {{ "Hello, %(you)s!" | t }}

Filter keyword arguments are merged with the current render context before being used to
replace variables in message text. All variables are converted to their string
representation before substitution. Dotted property/attribute access is not supported
inside message variables.

.. code-block:: liquid2

   {{ "Hello, %(you)s!" | t: you: user.name }}

The ```translate`` <optional_tags.md#translate>`__ block tag recognizes simplified Liquid
output statements as translation message variables. These variables must be valid
identifiers without dotted or bracketed property/attribute access, and no filters.

.. code-block:: liquid2

   {% translate %}
       Hello, {{ you }}!
   {% endtranslate %}

Keyword arguments passed to the ```translate`` <optional_tags.md#translate>`__ tag will be
merged with the current render context before being used to replace variables in message
text.

.. code-block:: liquid2

   {% translate you: user.name, count: users.size %}
       Hello, {{ you }}!
   {% plural %}
       Hello, {{ you }}s!
   {% endtranslate %}

Message Extraction
^^^^^^^^^^^^^^^^^^

Use the ```extract_from_templates()`` <api/messages.md#liquid.extract_from_template>`__
function to build a message
`catalog <https://babel.pocoo.org/en/latest/api/messages/catalog.html#catalogs>`__ from
one or more templates. You are then free to make use of `Babel's PO file
features <https://babel.pocoo.org/en/latest/api/messages/pofile.html>`__, or convert the
catalog to a more convenient internal representation.

.. code-block:: python

   import io

   from babel.messages.pofile import write_po

   from liquid import parse
   from liquid.messages import extract_from_templates

   source = """
   {% # Translators: some comment %}
   {{ 'Hello, World!' | t }}
   {% comment %}Translators: other comment{% endcomment %}
   {% translate count: 2 %}
       Hello, {{ you }}!
   {% plural %}
       Hello, all!
   {% endtranslate %}
   """

   template = parse(source, name="something.liquid")
   catalog = extract_from_templates(template)

   buf = io.BytesIO()
   write_po(buf, catalog, omit_header=True)
   print(buf.getvalue().decode("utf-8"))

.. code-block:: text

   #. Translators: some comment
   #: something.liquid:3
   msgid "Hello, World!"
   msgstr ""

   #. Translators: other comment
   #: something.liquid:5
   #, python-format
   msgid "Hello, %(you)s!"
   msgid_plural "Hello, all!"
   msgstr[0] ""
   msgstr[1] ""

Translator Comments
^^^^^^^^^^^^^^^^^^^

When a Liquid comment tag immediately precedes a translatable filter or tag, and the
comment starts with a string in ``comment_tags``, that comment will be included as a
translator comment with the message. Use the ``comment_tags`` argument to
```extract_liquid()`` <api/convenience.md#liquid.extract_liquid>`__, or
```extract_from_templates()`` <api/messages.md#liquid.extract_from_template>`__ to change
translator comment prefixes. The default is ``["Translators:"]``.

.. code-block:: python

   from liquid import parse
   from liquid.messages import extract_from_templates

   source = """
   {% # Translators: some comment %}
   {{ 'Hello, World!' | t }}
   {% comment %}Translators: other comment{% endcomment %}
   {% translate count: 2 %}
       Hello, {{ you }}!
   {% plural %}
       Hello, all!
   {% endtranslate %}
   """

   template = parse(source, name="something.liquid")
   catalog = extract_from_templates(template, strip_comment_tags=True)

   message = catalog.get("Hello, World!")
   print(message.auto_comments[0])  # some comment


