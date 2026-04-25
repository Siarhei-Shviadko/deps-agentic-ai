from ...shared import Guard, ImmutableCheck, ValueObject
from ...tool_set import ToolData
from .parameter import Parameter

__all__ = ["Tool"]


class Tool(metaclass=ValueObject):
    code = Guard[str](str, ImmutableCheck())
    name = Guard[str](str, ImmutableCheck())
    parameters = Guard[list[Parameter]](list, ImmutableCheck())

    def __init__(self, code: str, name: str, parameters: list[Parameter]) -> None:
        self.code = code
        self.name = name
        self.parameters = parameters

    @classmethod
    def from_data(cls, data: ToolData) -> "Tool":
        return cls(
            code=data["code"],
            name=data["name"],
            parameters=[Parameter.from_data(pd) for pd in data["parameters"]],
        )

    def to_data(self) -> ToolData:
        return ToolData(
            code=self.code,
            name=self.name,
            parameters=[p.to_data() for p in self.parameters],
        )
