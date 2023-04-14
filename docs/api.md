# API Reference

## Rendering Templates

::: liquid.Environment
    handler: python

::: liquid.Template
    handler: python

::: liquid.BoundTemplate
    handler: python

## Template Analysis

::: liquid.static_analysis.TemplateAnalysis
    handler: python

::: liquid.static_analysis.ContextualTemplateAnalysis
    handler: python

::: liquid.analyze_tags.TagAnalysis
    handler: python

## Template Loaders

::: liquid.loaders.FileSystemLoader
    handler: python

::: liquid.loaders.FileExtensionLoader
    handler: python

::: liquid.loaders.DictLoader
    handler: python

::: liquid.loaders.ChoiceLoader
    handler: python

::: liquid.loaders.BaseLoader
    handler: python

::: liquid.loaders.TemplateSource
    handler: python

## Undefined Types

::: liquid.Undefined
    handler: python

::: liquid.StrictUndefined
    handler: python

::: liquid.DebugUndefined
    handler: python

::: liquid.StrictDefaultUndefined
    handler: python

## Exceptions

::: liquid.exceptions.Error
    handler: python
    
::: liquid.exceptions.LiquidSyntaxError
    handler: python
    
::: liquid.exceptions.LiquidTypeError
    handler: python
    
::: liquid.exceptions.LiquidValueError
    handler: python
    
::: liquid.exceptions.DisabledTagError
    handler: python
    
::: liquid.exceptions.NoSuchFilterFunc
    handler: python
    
::: liquid.exceptions.FilterArgumentError
    handler: python
    
::: liquid.exceptions.FilterValueError
    handler: python
    
::: liquid.exceptions.TemplateNotFound
    handler: python
    
::: liquid.exceptions.TemplateTraversalError
    handler: python
    
::: liquid.exceptions.ContextDepthError
    handler: python
    
::: liquid.exceptions.LocalNamespaceLimitError
    handler: python
    
::: liquid.exceptions.LoopIterationLimitError
    handler: python
    
::: liquid.exceptions.OutputStreamLimitError
    handler: python
    
::: liquid.exceptions.UndefinedError
    handler: python
    