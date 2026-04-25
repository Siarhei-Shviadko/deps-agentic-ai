from typing import Protocol

from .agent_vendor_info import AgentVendorsInfo

__all__ = ["IQueryAgentVendorRepository"]


class IQueryAgentVendorRepository(Protocol):
    async def find_all(self) -> AgentVendorsInfo:
        pass
