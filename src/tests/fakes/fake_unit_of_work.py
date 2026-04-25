from deps_agentic_ai.infrastructure.unit_of_work import AbstractUnitOfWork

__all__ = ["FakeUnitOfWork"]


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        tool_sets,
        modes,
        agent_vendors,
        conversations,
    ) -> None:
        self.tool_sets = tool_sets
        self.modes = modes
        self.agent_vendors = agent_vendors
        self.conversations = conversations

    async def __aenter__(self) -> None:
        pass

    async def __aexit__(self, *args) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass
