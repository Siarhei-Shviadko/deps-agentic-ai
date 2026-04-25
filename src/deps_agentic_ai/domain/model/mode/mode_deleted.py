from dataclasses import dataclass

from ..shared import Event

__all__ = ["ModeDeleted"]


@dataclass
class ModeDeleted(Event):
    id: str
