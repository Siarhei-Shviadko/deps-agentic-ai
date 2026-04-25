from datetime import datetime

from ...shared import Guard, ImmutableCheck, LengthCheck, ValueObject

__all__ = ["Question"]

MIN_QUESTION_TEXT_LENGTH = 1


class Question(metaclass=ValueObject):
    text = Guard[str](str, ImmutableCheck(), LengthCheck(min_length=MIN_QUESTION_TEXT_LENGTH))
    created_at = Guard[datetime](datetime, ImmutableCheck())

    def __init__(self, text: str, created_at: datetime) -> None:
        self.text = text
        self.created_at = created_at
