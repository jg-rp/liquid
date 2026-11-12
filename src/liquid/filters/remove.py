from .._filter import FilterContext


def remove(context: FilterContext, left: object, right: object) -> str:
    left_ = context.to_str(left, "")
    right_ = context.to_str(right, "")

    if not right_:
        return left_

    return left_.replace(right_, "")


def remove_first(context: FilterContext, left: object, right: object) -> str:
    left_ = context.to_str(left, "")
    right_ = context.to_str(right, "")

    if not right_:
        return left_

    return left_.replace(right_, "", 1)


def remove_last(context: FilterContext, left: object, right: object) -> str:
    left_ = context.to_str(left, "")
    right_ = context.to_str(right, "")

    if not right_:
        return left_

    before, _, after = left_.rpartition(right_)

    if before:
        return before + after

    return left_
