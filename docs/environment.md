### Ternary expressions

```
{{ <expression> if <expression> else <expression> }}
```

Inline conditional expressions can be used as an alternative to the longer form [`{% if %}` tag](#if).

```liquid2
{{ "bar" if x.y == z else "baz" }}
```

Filters can be applied to either branch.

```liquid2
{{ "bar" | upcase if x else "baz" | capitalize }}
```

Or applied to the result of the conditional expression as a whole using _tail filters_. Notice the double pipe symbol (`||`).

```liquid2
{{ "bar" if x else "baz" || upcase | append: "!" }}
```
