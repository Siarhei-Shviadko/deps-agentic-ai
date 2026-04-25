from functools import cached_property

from ...shared import (
    Guard,
    ImmutableCheck,
    LengthCheck,
    ToolCode,
    ToolSetCode,
    ValueObject,
)
from .tool import Tool

__all__ = ["ToolSet"]

MIN_TOOLS_COUNT = 1


class ToolSet(metaclass=ValueObject):
    id = Guard[str](str, ImmutableCheck())
    code = Guard[ToolSetCode](ToolSetCode, ImmutableCheck())
    name = Guard[str](str, ImmutableCheck())
    tools = Guard[dict[ToolCode, Tool]](dict, ImmutableCheck(), LengthCheck(min_length=MIN_TOOLS_COUNT))

    def __init__(self, id_: str, code: ToolSetCode, name: str, tools: list[Tool]) -> None:
        self.id = id_
        self.code = code
        self.name = name
        self.tools = {tool.code: tool for tool in tools}

    @cached_property
    def tool_codes(self) -> set[ToolCode]:
        return set(self.tools.keys())

    def has_tool(self, tool_code: ToolCode) -> bool:
        return tool_code in self.tools
