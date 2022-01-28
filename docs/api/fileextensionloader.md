# liquid.loaders.FileExtensionLoader

A loader that inherits from [FileSystemLoader](/api/FileSystemLoader) and adds a file name extension to any `template_name` that does not have one.

When rendering from an environment configured with a `FileExtensionLoader`, templates can, for example, use `{% render 'somesnippet' %}` and `{% include 'mysection' %}` instead of `{% render 'somesnippet.liquid' %}` or `{% include 'mysection.html' %}`.

## FileExtensionLoader

`class FileExtensionLoader(search_path, encoding="utf-8", ext=".liquid")`

**Parameters**:

- `search_path: Union[str, Path, Iterable[Union[str, Path]]]` - One or more paths to search.

- `encoding: str = "utf-8"` - Open template files with the given encoding. Defaults to `"utf-8"`.

- `ext: str = ".liquid"` - A default file extension. Should include a leading period. Defaults to `.liquid`.
