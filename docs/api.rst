
API Reference
=============

.. module:: liquid

Also see documentation at https://jg-rp.github.io/liquid/.

Rendering Templates
-------------------

.. autoclass:: Environment([options])
    :members: from_string, get_template, get_template_async, add_tag, add_filter, analyze_tags, analyze_tags_async, analyze_tags_from_string, parse

    .. attribute:: context_depth_limit

        Class attribute.The maximum number of times a render context can be extended or
        wrapped before a :class:`liquid.exceptions.ContextDepthError` is raised.

    .. attribute:: local_namespace_limit

        Class attribute. The maximum number of bytes (according to :func:`sys.getsizeof`)
        allowed in a template's local namespace, per render, before a 
        :class:`liquid.exceptions.LocalNamespaceLimitError` exception is raised. Note
        that we only count the size of the local namespace values, not its keys.

    .. attribute:: loop_iteration_limit

        Class attribute. The maximum number of loop iterations allowed before a 
        :class:`liquid.exceptions.LoopIterationLimitError` is raised.

    .. attribute:: output_stream_limit

        Class attribute. The maximum number of bytes that can be written to a template's
        output stream, per render, before an :class:`liquid.exceptions.OutputStreamLimitError`
        exception is raised.

    .. attribute:: undefined

        The undefined type. When an identifier can not be resolved, an instance of
        `undefined` is returned.

    .. attribute:: strict_filters

        Indicates if an undefined filter should raise an exception or be ignored.

    .. attribute:: autoescape

        Indicates if auto-escape is enabled.

    .. attribute:: tags

        A dictionary mapping tag names to :class:`liquid.tag.Tag` instances.
       
    .. attribute:: filters

        A dictionary mapping filter names to callable objects implementing a filter's 
        behavior.

    .. attribute:: mode

        The current tolerance mode.

    .. attribute:: cache

        The template cache.

    .. attribute:: auto_reload

        Indicates if automatic reloading of templates is enabled.

    .. attribute:: template_class

        :meth:`Environment.get_template` and :meth:`Environment.from_string` return an
        instance of :attr:`Environment.template_class`. Defaults to
        :class:`liquid.template.BoundTemplate`.

    .. attribute:: globals

        A dictionary of variables that will be added to the context of every template
        rendered from the environment.


.. autofunction:: Template(source: str, [options])

.. autoclass:: liquid.template.BoundTemplate
    :members: render, render_async, render_with_context, render_with_context_async, analyze, analyze_async, analyze_with_context, analyze_with_context_async

    .. attribute:: name

        The template's name. As it would have been passed to
        :meth:`liquid.Environment.get_template`.
    
    .. attribute:: globals

        A dictionary of variables that will be added to the context of every template
        rendered from the environment.

Template Analysis
-----------------

.. autoclass:: liquid.template.TemplateAnalysis

.. autoclass:: liquid.template.ContextualTemplateAnalysis

.. autoclass:: liquid.analyze_tags.TagAnalysis


Template Loaders
----------------

.. autoclass:: liquid.loaders.FileSystemLoader

.. autoclass:: liquid.loaders.FileExtensionLoader

.. autoclass:: liquid.loaders.DictLoader

.. autoclass:: liquid.loaders.ChoiceLoader

.. autoclass:: liquid.loaders.BaseLoader
    :members: get_source, get_source_async

.. autoclass:: liquid.loaders.TemplateSource


Undefined Types
---------------

.. autoclass:: liquid.Undefined
.. autoclass:: liquid.StrictUndefined
.. autoclass:: liquid.DebugUndefined
.. autoclass:: liquid.StrictDefaultUndefined

Exceptions
----------

.. autoclass:: liquid.exceptions.Error
.. autoclass:: liquid.exceptions.LiquidSyntaxError
.. autoclass:: liquid.exceptions.LiquidTypeError
.. autoclass:: liquid.exceptions.LiquidValueError
.. autoclass:: liquid.exceptions.DisabledTagError
.. autoclass:: liquid.exceptions.NoSuchFilterFunc
.. autoclass:: liquid.exceptions.FilterArgumentError
.. autoclass:: liquid.exceptions.FilterValueError
.. autoclass:: liquid.exceptions.TemplateNotFound
.. autoclass:: liquid.exceptions.TemplateTraversalError
.. autoclass:: liquid.exceptions.ContextDepthError
.. autoclass:: liquid.exceptions.LocalNamespaceLimitError
.. autoclass:: liquid.exceptions.LoopIterationLimitError
.. autoclass:: liquid.exceptions.OutputStreamLimitError
.. autoclass:: liquid.exceptions.UndefinedError

