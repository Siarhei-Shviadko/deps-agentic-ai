from ...shared import Guard, ImmutableCheck, ToolSetCode, ValueObject
from ..types import ContextData
from .active_tool import ActiveTool

__all__ = ["Context", "ContextData"]


class Context(metaclass=ValueObject):
    tools = Guard[dict[ToolSetCode, list[ActiveTool]]](dict, ImmutableCheck())

    def __init__(self, tools: dict[ToolSetCode, list[ActiveTool]]) -> None:
        self.tools = tools

    def to_data(self) -> ContextData:
        return ContextData(
            tools={tool_set_code: [tool.to_data() for tool in tools] for tool_set_code, tools in self.tools.items()},
        )
