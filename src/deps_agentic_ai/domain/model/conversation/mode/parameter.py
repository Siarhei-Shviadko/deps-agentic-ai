from ...shared import Guard, ImmutableCheck, ValueObject

__all__ = ["Parameter"]


class Parameter(metaclass=ValueObject):
    name = Guard[str](str, ImmutableCheck())

    def __init__(self, name: str) -> None:
        self.name = name
