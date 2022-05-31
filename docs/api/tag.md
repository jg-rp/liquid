---
id: Tag
---

# liquid.tag.Tag

Base class for all built-in and [custom template tags](../guides/custom-tags.md).

## `Tag`

`class Tag(env)`

**Parameters**:

- `env: liquid.Environment` - The [`Environment`](./environment.md) that manages this tag.

## Class Attributes

### `block`

**Type**: `bool = True`

Indicates if the tag is a block tag.

### `name`

**Type**: `str = ""`

The name of the tag. Like `"if"` or `"for"`.

### `end`

**Type**: `str = ""`

The end or closing tag name. If `block` is `True`, `end` must be set. By convention it is
`"end<tag.name>"`.

## Properties

### `env`

**Type**: `liquid.Environment`

The [`Environment`](./environment.md) that manages this tag.

## Methods

### `get_node`

`get_node(self, stream: TokenStream) -> Node`

Used internally to delegate to `Tag.parse`.

### `parse`

`parse(self, stream: TokenStream) -> Node:`

Abstract method. Return a parse tree node by parsing tokens from the given stream. Every tag must implement `parse`.
