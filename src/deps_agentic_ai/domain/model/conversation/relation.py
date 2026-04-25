from typing import Any

from ..shared import Guard, ImmutableCheck, ValueObject
from .types import RelationData

__all__ = ["Relation", "RelationData"]


class Relation(metaclass=ValueObject):
    details = Guard[dict[str, Any]](dict, ImmutableCheck())

    def __init__(self, details: dict[str, Any]) -> None:
        self.details = details
