from typing import Protocol

from .agent_vendor import AgentVendor

__all__ = ["ICommandAgentVendorRepository"]


class ICommandAgentVendorRepository(Protocol):
    async def save(self, agent_vendor: AgentVendor) -> None:
        pass

    async def save_all(self, agent_vendors: list[AgentVendor]) -> None:
        pass

    async def agent_vendor_of_id(self, id_: str) -> AgentVendor | None:
        pass

    async def active_agent_vendor(self) -> AgentVendor | None:
        pass

    async def has_agent_vendor_with_name(self, name: str) -> bool:
        pass

    async def delete(self, agent_vendor: AgentVendor) -> None:
        pass
