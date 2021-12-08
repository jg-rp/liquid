# Custom Template Cache

An in-memory template cache is included with every [liquid.Environment](../api/Environment). It
caches parsed templates so repeated calls to [get_template()](../api/Environment#get_template) don't
have to do time consuming lexing and parsing unnecessarily. You can control the default cache
capacity with the `cache_size` argument to the `Environment` constructor.

One common use case for Liquid is to expose templating to "untrusted" users, rather than trusted
developers. A situation where the number of templates increases with the number of users. Resulting
in more templates than can reasonably be held in memory on one server.

## Redis Example

Coming soon.
