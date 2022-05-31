# liquid.loaders.FileSystemLoader

A loader that loads templates from one or more directories on a file system.

## `FileSystemLoader`

`class FileSystemLoader(search_path, encoding)`

**Parameters**:

- `search_path: Union[str, Path, Iterable[Union[str, Path]]]` - One or more paths to search.

- `encoding: str = "utf-8"` - Open template files with the given encoding. Defaults to `"utf-8"`.

## Properties

### `search_path`

A list of paths to search.

**Type**: `List[pathlib.Path]`

## Methods

### `get_source`

`get_source(environment, template_name)`

Searches each path in `search_path`, in turn, returning the first template source it finds.

**Raises**: `liquid.exceptions.TemplateNotFound` if a template with the given name can not be
found.  
**Returns**: The source, filename and reload function for the named template.  
**Return Type**: `liquid.loaders.TemplateSource`

### `get_source_async`

`async get_source(environment, template_name)`

An async version of [`get_source()`](#get_source).

**Returns**: The source, filename and reload function for the named template.  
**Return Type**: `liquid.loaders.TemplateSource`
