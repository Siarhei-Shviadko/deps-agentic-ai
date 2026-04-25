from ...shared import EntityId, Guard, ImmutableCheck, ValueObject
from ...tool_set import ToolSetData
from .tool import Tool

__all__ = ["ToolSet"]


class ToolSet(metaclass=ValueObject):
    id = Guard[EntityId](EntityId, ImmutableCheck())
    code = Guard[str](str, ImmutableCheck())
    name = Guard[str](str, ImmutableCheck())
    tools = Guard[list[Tool]](list, ImmutableCheck())

    def __init__(
        self,
        id_: str,
        code: str,
        name: str,
        tools: list[Tool],
    ) -> None:
        self.id = EntityId(id_)
        self.code = code
        self.name = name
        self.tools = tools

    def to_data(self) -> ToolSetData:
        return ToolSetData(id=self.id(), code=self.code, name=self.name, tools=[t.to_data() for t in self.tools])

    @classmethod
    def from_data(cls, data: ToolSetData) -> "ToolSet":
        return cls(
            id_=data["id"],
            code=data["code"],
            name=data["name"],
            tools=[Tool.from_data(t) for t in data["tools"]],
        )
