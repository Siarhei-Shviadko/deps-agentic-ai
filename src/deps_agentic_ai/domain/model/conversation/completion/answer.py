from datetime import datetime

from ...shared import Guard, ImmutableCheck, ValueObject

__all__ = ["Answer"]


class Answer(metaclass=ValueObject):
    text = Guard[str](str, ImmutableCheck())
    created_at = Guard[datetime](datetime, ImmutableCheck())

    def __init__(self, text: str, created_at: datetime) -> None:
        self.text = text
        self.created_at = created_at
