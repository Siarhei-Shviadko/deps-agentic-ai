from ...shared import Guard, ImmutableCheck, ValueObject

__all__ = ["ExecutionContext"]


class ExecutionContext(metaclass=ValueObject):
    text = Guard[str](str, ImmutableCheck())

    def __init__(self, text: str) -> None:
        self.text = text
