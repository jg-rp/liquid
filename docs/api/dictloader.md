# liquid.loaders.DictLoader

A loader that loads templates from a dictionary mapping template names to template source strings.

## `DictLoader`

`class FileSystemLoader(templates)`

**Parameters**:

- `templates: Dict[str, str]` - A dictionary mapping template names to template source strings.

## Methods

### `get_source`

`get_source(environment, template_name)`

Return a template source by looking up the given name in the dictionary of templates.

**Raises**: `liquid.exceptions.TemplateNotFound` if a template with the given name can not be
found.  
**Returns**: The source, filename and reload function for the named template.  
**Return Type**: `liquid.loaders.TemplateSource`

### `get_source_async`

`async get_source(environment, template_name)`

An async version of [get_source](#get_source).

**Returns**: The source, filename and reload function for the named template.  
**Return Type**: `liquid.loaders.TemplateSource`
