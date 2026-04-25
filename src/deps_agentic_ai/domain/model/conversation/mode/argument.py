from typing import Any

from ...shared import Guard, ImmutableCheck, ValueObject
from ..types import ArgumentData

__all__ = ["Argument", "ArgumentData"]


class Argument(metaclass=ValueObject):
    name = Guard[str](str, ImmutableCheck())

    def __init__(self, name: str, value: Any) -> None:
        self.name = name
        self.value = value

    @classmethod
    def from_data(cls, data: ArgumentData) -> "Argument":
        return cls(
            name=data["parameter"],
            value=data["value"],
        )
