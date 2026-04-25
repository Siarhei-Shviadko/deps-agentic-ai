from ...shared import Guard, ImmutableCheck, ValueObject
from ...tool_set import ParameterData

__all__ = ["Parameter"]


class Parameter(metaclass=ValueObject):
    name = Guard[str](str, ImmutableCheck())

    def __init__(self, name: str) -> None:
        self.name = name

    @classmethod
    def from_data(cls, data: ParameterData) -> "Parameter":
        return cls(
            name=data["name"],
        )

    def to_data(self) -> ParameterData:
        return ParameterData(
            name=self.name,
        )
