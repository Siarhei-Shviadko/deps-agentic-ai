from functools import cached_property

from ...shared import Guard, ImmutableCheck, ToolCode, ValueObject
from .parameter import Parameter

__all__ = ["Tool"]


class Tool(metaclass=ValueObject):
    code = Guard[ToolCode](ToolCode, ImmutableCheck())
    name = Guard[str](str, ImmutableCheck())
    parameters = Guard[list[Parameter]](list, ImmutableCheck())

    def __init__(self, code: ToolCode, name: str, parameters: list[Parameter]) -> None:
        self.code = code
        self.name = name
        self.parameters = parameters

    @cached_property
    def parameter_names(self) -> set[str]:
        return set(param.name for param in self.parameters)

    def has_parameter(self, parameter_name: str) -> bool:
        return parameter_name in self.parameter_names
