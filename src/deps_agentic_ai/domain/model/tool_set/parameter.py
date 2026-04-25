from ..shared import Guard, ImmutableCheck, LengthCheck, ValueObject
from .parameter_data import ParameterData

__all__ = ["Parameter", "MIN_PARAMETER_NAME_LENGTH"]

MIN_PARAMETER_NAME_LENGTH = 1


class Parameter(metaclass=ValueObject):
    name = Guard[str](str, ImmutableCheck(), LengthCheck(min_length=MIN_PARAMETER_NAME_LENGTH))

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
