from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class ResourceLimits:
    """
    Parameters
    ----------
    max_assign_score
        The maximum assign score allowed per template before a
        :class:`liquid.ResourceLimitError` is raised.
    max_assign_score_cumulative
        The maximum combined assign score allowed for a template and all its descendant
        partial templates before a :class:`liquid.ResourceLimitError` is raised.
    max_render_score
        The maximum render score allowed per template before a
        :class:`liquid.ResourceLimitError` is raised.
    max_render_score_cumulative
        The maximum combined render score allowed for a template and all its descendant
        partial templates before a :class:`liquid.ResourceLimitError` is raised.
    max_render_size
        The maximum allowed length (in code points) of the output buffer per template
        before a :class:`liquid.ResourceLimitError` is raised.
    max_context_depth
        The maximum number of times a render context can be extended or copied before
        a :class:`liquid.ResourceLimitError` is raised. This helps us guard against
        circular ``{% render %}`` and ``{% include %}`` tags.
    max_loop_iterations
        The maximum number of loop iterations allowed before a
        :class:`liquid.ResourceLimitError` is raised, taking into account nested loops
        that could span multiple partial templates.
    max_block_depth
        The maximum block nesting depth allowed before a :class:`liquid.ResourceLimitError`
        is raised. This guards against specially crafted templates that could hit
        Python's recursion limit during the parsing phase.
    max_expression_depth
        The maximum expression nesting depth allowed before a
        :class:`liquid.ResourceLimitError` is raised. This guards against specially crafted
        expressions that could cause our recursive parser to hit Python's recursion limit.
    """

    max_assign_score: int | None = None
    max_assign_score_cumulative: int | None = None
    max_render_score: int | None = None
    max_render_score_cumulative: int | None = None
    max_render_size: int | None = None
    max_context_depth: int = 30
    max_loop_iterations: int | None = None
    max_block_depth: int = 30
    max_expression_depth: int = 100
