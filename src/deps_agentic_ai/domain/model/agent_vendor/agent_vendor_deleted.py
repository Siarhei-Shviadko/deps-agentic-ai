from dataclasses import dataclass

from ..shared import Event

__all__ = ["AgentVendorDeleted"]


@dataclass
class AgentVendorDeleted(Event):
    id: str
