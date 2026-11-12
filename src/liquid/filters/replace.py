from .._filter import FilterContext


def replace(
    context: FilterContext, left: object, sub: object, rep: object = None
) -> str:
    return context.to_str(left, "").replace(
        context.to_str(sub, ""), context.to_str(rep, "")
    )


def replace_first(
    context: FilterContext, left: object, sub: object, rep: object = None
) -> str:
    return context.to_str(left, "").replace(
        context.to_str(sub, ""), context.to_str(rep, ""), 1
    )


def replace_last(context: FilterContext, left: object, sub: object, rep: object) -> str:
    left_ = context.to_str(left, "")
    sub_ = context.to_str(sub, "")

    if not sub_:
        return left_ + context.to_str(rep, "")

    before, _, after = left_.rpartition(sub_)

    if before:
        return before + context.to_str(rep, "") + after

    return left_
