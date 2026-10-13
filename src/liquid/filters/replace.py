from .._filter import FilterContext


def replace(
    context: FilterContext, left: object, sub: object, rep: object = None
) -> str:
    left = context.to_str(left, "")
    sub = context.to_str(sub, "")
    rep = context.to_str(rep, "")
    return left.replace(sub, rep)


def replace_first(
    context: FilterContext, left: object, sub: object, rep: object = None
) -> str:
    left = context.to_str(left, "")
    sub = context.to_str(sub, "")
    rep = context.to_str(rep, "")
    return left.replace(sub, rep, 1)


def replace_last(context: FilterContext, left: object, sub: object, rep: object) -> str:
    left = context.to_str(left, "")
    sub = context.to_str(sub, "")

    if not sub:
        return left + context.to_str(rep, "")

    before, _, after = left.rpartition(sub)

    if before:
        return before + context.to_str(rep, "") + after

    return left
