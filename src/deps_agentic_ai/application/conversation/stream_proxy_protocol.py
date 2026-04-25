from typing import AsyncGenerator, Protocol

from deps_agentic_ai.domain.model.conversation import AgentRequest

__all__ = ["StreamProxyProtocol", "SSEEvent"]


class SSEEvent(Protocol):
    @property
    def type(self) -> str:
        ...

    @property
    def text(self) -> str:
        ...


class StreamProxyProtocol(Protocol):
    async def stream_chat(self, agent_request: AgentRequest, base_url: str) -> AsyncGenerator[SSEEvent, None]:
        ...
