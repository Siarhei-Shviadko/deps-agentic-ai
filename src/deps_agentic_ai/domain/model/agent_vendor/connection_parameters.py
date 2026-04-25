from ..shared import Guard, ImmutableCheck, ValueObject

__all__ = ["ConnectionParameters"]


class ConnectionParameters(metaclass=ValueObject):
    base_url = Guard[str](str, ImmutableCheck())

    def __init__(self, basse_url: str) -> None:
        self.base_url = basse_url
