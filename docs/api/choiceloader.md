# liquid.loaders.ChoiceLoader

A template loader that will try each of a list of loaders until a template is found.

## `ChoiceLoader`

`class FileSystemLoader(loaders)`

**Parameters**:

- `loaders: List[liquid.loaders.BaseLoader]` - A list of loaders to try.

## Methods

### `get_source`

`get_source(environment, template_name)`

Calls `get_source` on each loader, returning the first template source found.

**Raises**: `liquid.exceptions.TemplateNotFound` if a template with the given name can not be
found.  
**Returns**: The source, filename and reload function for the named template.  
**Return Type**: `liquid.loaders.TemplateSource`

### `get_source_async`

`async get_source(environment, template_name)`

An async version of [get_source](#get_source).

**Returns**: The source, filename and reload function for the named template.  
**Return Type**: `liquid.loaders.TemplateSource`
