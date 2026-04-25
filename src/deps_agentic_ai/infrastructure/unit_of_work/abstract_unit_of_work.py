import abc

from deps_agentic_ai.domain.model.agent_vendor import ICommandAgentVendorRepository
from deps_agentic_ai.domain.model.conversation import ICommandConversationRepository
from deps_agentic_ai.domain.model.mode import ICommandModeRepository
from deps_agentic_ai.domain.model.tool_set import ICommandToolSetRepository

__all__ = ["AbstractUnitOfWork"]


class AbstractUnitOfWork(abc.ABC):
    tool_sets: ICommandToolSetRepository
    modes: ICommandModeRepository
    agent_vendors: ICommandAgentVendorRepository
    conversations: ICommandConversationRepository

    @abc.abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
