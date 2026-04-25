from deps_agentic_ai.domain.model.agent_vendor import (
    AgentVendor,
    ICommandAgentVendorRepository,
)

__all__ = ["FakeCommandAgentVendorRepository"]


class FakeCommandAgentVendorRepository(ICommandAgentVendorRepository):
    def __init__(self, agent_vendors: list[AgentVendor] | None = None) -> None:
        self._db = {agv.id(): agv for agv in agent_vendors} if agent_vendors else {}

    async def has_agent_vendor_with_name(self, name: str) -> bool:
        for agv in self._db.values():
            if agv.name == name:
                return True

        return False

    async def save(self, agent_vendor: AgentVendor) -> None:
        self._db[agent_vendor.id()] = agent_vendor

    async def save_all(self, agent_vendor: list[AgentVendor]) -> None:
        raise NotImplementedError()

    async def agent_vendor_of_id(self, id_: str) -> AgentVendor | None:
        return self._db.get(id_)

    async def active_agent_vendor(self) -> AgentVendor | None:
        raise NotImplementedError()

    async def delete(self, agent_vendor: AgentVendor) -> None:
        raise NotImplementedError()

    async def _erase_all(self) -> None:
        self._db.clear()
