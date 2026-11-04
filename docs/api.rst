API Docs
========

.. autofunction:: liquid.parse

.. autofunction:: liquid.render

.. autofunction:: liquid.render_async

.. autofunction:: liquid.extract_liquid


.. autoclass:: liquid.Environment
    :members:

.. autoclass:: liquid.Template
    :members:

.. autoclass:: liquid.LegacyLexer
    :show-inheritance:

.. autoclass:: liquid.ExtendedLexer
    :show-inheritance:

.. autoclass:: liquid.LegacyParser
    :show-inheritance:

.. autoclass:: liquid.LaxLegacyParser
    :show-inheritance:

.. autoclass:: liquid.ExtendedParser
    :show-inheritance:

.. autoclass:: liquid.LaxExtendedParser
    :show-inheritance:

.. autoclass:: liquid.ResourceLimits

.. autoclass:: liquid.RenderContext

Loaders
-------

.. autoclass:: liquid.Loader
    :members:
    :show-inheritance:

.. autoclass:: liquid.DictLoader
    :members:
    :show-inheritance:

.. autoclass:: liquid.CachingDictLoader
    :members:
    :show-inheritance:

.. autoclass:: liquid.FileSystemLoader
    :members:
    :show-inheritance:

.. autoclass:: liquid.CachingFileSystemLoader
    :members:
    :show-inheritance:

.. autoclass:: liquid.PackageLoader
    :members:
    :show-inheritance:

.. autoclass:: liquid.ChoiceLoader
    :members:
    :show-inheritance:

.. autoclass:: liquid.CachingChoiceLoader
    :members:
    :show-inheritance:

Drop interface
--------------

.. autoclass:: liquid.LiquidObject
    :members:
    :special-members: __liquid_hasattr__, __liquid_getattr__
    :show-inheritance:

.. autoclass:: liquid.LiquidAsyncObject
    :members:
    :special-members: __liquid_hasattr_async__, __liquid_getattr_async__
    :show-inheritance:

.. autoclass:: liquid.LiquidIterable
    :members:
    :special-members: __liquid_iter__
    :show-inheritance:

.. autoclass:: liquid.LiquidAsyncIterable
    :members:
    :special-members: __liquid_iter_async__
    :show-inheritance:

.. autoclass:: liquid.LiquidPrimitive
    :members:
    :special-members: __liquid__
    :show-inheritance:

Exceptions
----------

.. automodule:: liquid.exceptions
    :members:
    :member-order: bysource


Tag API
-------

.. autotype:: liquid.Node

.. autotype:: liquid.Block

.. autoclass:: liquid.Tag
    :members:
    :show-inheritance:

.. autoclass:: liquid.Markup
    :members:
    :show-inheritance:

.. autoclass:: liquid.Parser
    :members:

.. autoclass:: liquid.StringBuffer
    :members:

Filter API
----------

.. autotype:: liquid.Filter

    