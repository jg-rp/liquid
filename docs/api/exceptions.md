# liquid.exceptions

## liquid.exceptions.Error

`class liquid.exceptions.Error(*args, linenum=None, filename=None)`

Base class for all Liquid exceptions.

## liquid.exceptions.LiquidSyntaxError

`class liquid.exceptions.LiquidSyntaxError(*args, linenum=None, filename=None)`

Exception raised when there is a parser error.

## liquid.exceptions.LiquidTypeError

`class liquid.exceptions.LiquidTypeError(*args, linenum=None, filename=None)`

Exception raised when an error occurs at render time.

## liquid.exceptions.DisabledTagError

`class liquid.exceptions.DisabledTagError(*args, linenum=None, filename=None)`

Exception raised when an attempt is made to render a disabled tag.

## liquid.exceptions.NoSuchFilterFunc

`class liquid.exceptions.NoSuchFilterFunc(*args, linenum=None, filename=None)`

Exception raised when a filter lookup fails.

## liquid.exceptions.FilterError

`class liquid.exceptions.FilterError(*args, linenum=None, filename=None)`

Base class of all filter related errors.

## liquid.exceptions.FilterArgumentError

`class liquid.exceptions.FilterArgumentError(*args, linenum=None, filename=None)`

Exception raised when a filter's arguments are invalid.

## liquid.exceptions.FilterValueError

`class liquid.exceptions.FilterValueError(*args, linenum=None, filename=None)`

Exception raised when a filter'ss value is invalid.

## liquid.exceptions.TemplateNotFound

`class liquid.exceptions.TemplateNotFound(*args, linenum=None, filename=None)`

Exception raised when a template could not be found.

## liquid.exceptions.ContextDepthError

`class liquid.exceptions.ContextDepthError(*args, linenum=None, filename=None)`

Exception raised when the maximum context depth is reached.

Usually indicates recursive use of render or include tags.

## liquid.exceptions.LocalNamespaceLimitError

`class liquid.exceptions.LocalNamespaceLimitError(*args, linenum=None, filename=None)`

Exception raised when the maximum size of a render context's local namespace has been exceeded.

## liquid.exceptions.LoopIterationLimitError

`class liquid.exceptions.LoopIterationLimitError(*args, linenum=None, filename=None)`

Exception raised when the maximum number of loop iterations has been exceeded.

## liquid.exceptions.OutputStreamLimitError

`class liquid.exceptions.OutputStreamLimitError(*args, linenum=None, filename=None)`

Exception raised when an output stream limit has been exceeded.

## liquid.exceptions.TemplateTraversalError

`class liquid.exceptions.TemplateTraversalError(*args, linenum=None, filename=None)`

Exception raised when an AST node or expression can not be visited..

## liquid.exceptions.UndefinedError

`class liquid.exceptions.UndefinedError(*args, linenum=None, filename=None)`

Exception raised by the StrictUndefined type.
