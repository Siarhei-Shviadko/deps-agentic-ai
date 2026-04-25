from ..shared import Guard, ImmutableCheck, LengthCheck, ValueObject
from .parameter import Parameter
from .tool_data import ToolData

__all__ = ["Tool", "MIN_TOOL_CODE_LENGTH", "MIN_TOOL_NAME_LENGTH", "MIN_TOOL_PARAMETERS_COUNT"]


MIN_TOOL_CODE_LENGTH = 1
MIN_TOOL_NAME_LENGTH = 1
MIN_TOOL_PARAMETERS_COUNT = 1


class Tool(metaclass=ValueObject):
    code = Guard[str](str, ImmutableCheck(), LengthCheck(min_length=MIN_TOOL_CODE_LENGTH))
    name = Guard[str](str, ImmutableCheck(), LengthCheck(min_length=MIN_TOOL_NAME_LENGTH))
    parameters = Guard[list[Parameter]](list, ImmutableCheck(), LengthCheck(min_length=MIN_TOOL_PARAMETERS_COUNT))

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
