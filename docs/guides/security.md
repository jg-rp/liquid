# Security

Designed for situations where template authors are untrusted and, perhaps, not software developers, Liquid has security goals that are distinct from many other template languages. Most notably:

- Liquid is non-evaling. User (template authors) submitted code must not be executed on the server.
- Liquid must not leak arbitrary properties and methods of objects added to a template's render context without being explicitly whitelisted. See [Objects and Drops](/introduction/objects-and-drops).
- Tags and filters must not mutate global context variables. See [namespaces](/introduction/render-context#namespaces).

## Guidelines

When developing custom [tags](/guides/custom-tags), [filters](/guides/custom-filters) and [loaders](/guides/custom-loaders), the following recommendations apply.

- Don't use [`eval`](https://docs.python.org/3/library/functions.html#eval) to evaluate tag expressions.
- Respect the global namespace by using [`context.assign()`](/api/context#assign) rather than updating a namespace directly.
- Implement filters as pure functions, without side effects.
- Actively guard against loading templates from outside the search path when implementing loaders that deal with a filesystem.
