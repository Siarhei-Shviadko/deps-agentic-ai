from ...shared import Guard, ImmutableCheck, LengthCheck, ValueObject
from ..types import ActiveToolData, ArgumentData
from .argument import Argument

__all__ = ["ActiveTool"]

MIN_ARGUMENTS_COUNT = 1


class ActiveTool(metaclass=ValueObject):
    code = Guard[str](str, ImmutableCheck())
    arguments = Guard[list[Argument]](list, ImmutableCheck(), LengthCheck(min_length=MIN_ARGUMENTS_COUNT))

    def __init__(self, code: str, arguments: list[Argument]) -> None:
        self.code = code
        self.arguments = arguments

    def to_data(self) -> ActiveToolData:
        return ActiveToolData(
            code=self.code,
            arguments=[ArgumentData(parameter=arg.name, value=arg.value) for arg in self.arguments],
        )
