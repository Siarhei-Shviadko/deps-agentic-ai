from dataclasses import dataclass

from ..shared import Event

__all__ = ["ConversationDeleted"]


@dataclass
class ConversationDeleted(Event):
    id: str
