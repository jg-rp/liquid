# liquid.ast.Node

Abstract base class for all nodes in a parse tree.

## `Node`

`class Node()`

## Properties

### `tok`

**Type**: `liquid.token.Token`

The token that started this node. All subclasses of include a `tok` property or override [token()](#token).

## Methods

### `token`

`token() -> liquid.token.Token`

Return the token that started this node. Looks for [`self.tok`](#tok).

### `render`

`render(context: Context, buffer: TextIO) -> Optional[bool]`

Check disabled tags before delegating to [render_to_output](#render-to-output).

### `render_async`

`async render_async(context: Context, buffer: TextIO) -> Optional[bool]`

An async version of [render](#render)

**Raises**: DisabledTagError if `self.token()` is disabled in the current context.

### `render_to_output`

`render_to_output(context: Context, buffer: TextIO) -> Optional[bool]`

Abstract method. Render this node to the output buffer with the given context.

### `render_to_output_async`

`async render_to_output_async(context: Context, buffer: TextIO) -> Optional[bool]`

An async version of [render_to_output](#render-to-output). Delegates to [render_to_output] by default.
