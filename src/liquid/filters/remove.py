from .._filter import FilterContext


def remove(context: FilterContext, left: object, right: object) -> str:
    left = context.to_str(left, "")
    right = context.to_str(right, "")

    if not right:
        return left

    return left.replace(right, "")


def remove_first(context: FilterContext, left: object, right: object) -> str:
    left = context.to_str(left, "")
    right = context.to_str(right, "")

    if not right:
        return left

    return left.replace(right, "", 1)


def remove_last(context: FilterContext, left: object, right: object) -> str:
    left = context.to_str(left, "")
    right = context.to_str(right, "")

    if not right:
        return left

    before, _, after = left.rpartition(right)

    if before:
        return before + after

    return left
