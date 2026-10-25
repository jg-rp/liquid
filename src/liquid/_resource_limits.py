from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class ResourceLimits:
    max_assign_score: int | None = None
    max_assign_score_cumulative: int | None = None
    max_render_score: int | None = None
    max_render_score_cumulative: int | None = None
    max_render_size: int | None = None
    max_context_depth: int = 30
    max_loop_iterations: int | None = None
    max_block_depth: int = 30
    max_expression_depth: int = 100
