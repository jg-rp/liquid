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

Exception raised when a filters arguments are invalid.

## liquid.exceptions.FilterValueError

`class liquid.exceptions.FilterValueError(*args, linenum=None, filename=None)`

Exception raised when a filters value is invalid.

## liquid.exceptions.TemplateNotFound

`class liquid.exceptions.TemplateNotFound(*args, linenum=None, filename=None)`

Exception raised when a template could not be found.

## liquid.exceptions.ContextDepthError

`class liquid.exceptions.ContextDepthError(*args, linenum=None, filename=None)`

Exception raised when the maximum context depth is reached.

Usually indicates recursive use of render or include tags.

## liquid.exceptions.UndefinedError

`class liquid.exceptions.UndefinedError(*args, linenum=None, filename=None)`

Exception raised by the StrictUndefined type.
