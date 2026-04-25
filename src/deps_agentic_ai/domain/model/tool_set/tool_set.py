from datetime import datetime

from ...exceptions import ParameterNameIsNotUnique, ToolCodeIsNotUnique
from ..shared import Entity, EntityId, Event, Guard, ImmutableCheck, LengthCheck
from .tool import Tool
from .tool_data import ToolData
from .tool_set_data import ToolSetData

__all__ = ["ToolSet", "MIN_TOOL_SET_CODE_LENGTH", "MIN_TOOL_SET_NAME_LENGTH", "MIN_TOOL_SET_TOOLS_COUNT"]

MIN_TOOL_SET_CODE_LENGTH = 1
MIN_TOOL_SET_NAME_LENGTH = 1
MIN_TOOL_SET_TOOLS_COUNT = 1


class ToolSet(metaclass=Entity):
    id = Guard[EntityId](EntityId, ImmutableCheck())
    code = Guard[str](str, ImmutableCheck(), LengthCheck(min_length=MIN_TOOL_SET_CODE_LENGTH))
    name = Guard[str](str, LengthCheck(min_length=MIN_TOOL_SET_NAME_LENGTH))
    tools = Guard[list[Tool]](list, LengthCheck(min_length=MIN_TOOL_SET_TOOLS_COUNT))
    created_at = Guard[datetime](datetime, ImmutableCheck())

    def __init__(
        self,
        id_: str,
        code: str,
        name: str,
        tools: list[Tool],
        created_at: datetime,
        *,
        events: list[Event] | None = None,
    ) -> None:
        self.id = EntityId(id_)
        self.code = code
        self.name = name
        self.tools = tools
        self.created_at = created_at

        self.events = events or []

        self._check_tools()

    def update(self, name: str, tools: list[ToolData]) -> None:
        self.name = name
        self.tools = [Tool.from_data(td) for td in tools]

        self._check_tools()

    def delete(self) -> None:
        pass

    def to_data(self) -> ToolSetData:
        return ToolSetData(id=self.id(), code=self.code, name=self.name, tools=[t.to_data() for t in self.tools])

    def _check_tools(self) -> None:
        tool_codes = set()

        for tool in self.tools:
            if tool.code in tool_codes:
                raise ToolCodeIsNotUnique(tool.code)

            self._check_tool(tool)

            tool_codes.add(tool.code)

    @staticmethod
    def _check_tool(tool: Tool) -> None:
        parameter_names = set()

        for parameter in tool.parameters:
            if parameter.name in parameter_names:
                raise ParameterNameIsNotUnique(parameter.name, tool.code)

            parameter_names.add(parameter.name)
