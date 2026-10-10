from .._filter import FilterContext


def downcase(context: FilterContext, left: object) -> str:
    return context.to_str(left, "").lower()
