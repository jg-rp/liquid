import markupsafe

from .._filter import FilterContext


def join(context: FilterContext, left: object, sep: object = " ") -> str:
    left_ = context.input_array(left)
    sep_ = context.to_str(sep, " ")

    if context.env.autoescape and sep_ == " ":
        sep_ = markupsafe.Markup(sep_)

    return sep_.join(context.to_str(obj, "") for obj in left_)
