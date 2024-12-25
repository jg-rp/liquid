from liquid.builtin.tags.tablerow_tag import TablerowNode
from liquid.builtin.tags.tablerow_tag import TablerowTag


class InterruptingTablerowNode(TablerowNode):
    """A _tablerow_ node with interrupt handling enabled."""

    interrupts = True


class InterruptingTablerowTag(TablerowTag):
    """A _tablerow_ tag that handles `break` and `continue` tags."""

    node_class = InterruptingTablerowNode
