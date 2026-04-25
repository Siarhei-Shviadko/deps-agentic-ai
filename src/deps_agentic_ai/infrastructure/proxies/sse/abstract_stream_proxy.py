import abc
from contextvars import ContextVar
from typing import AsyncGenerator

import httpx

from deps_agentic_ai.domain.model.conversation import AgentRequest
from deps_agentic_ai.extras.async_rest_client import AbstractAsyncRESTClient

from .exceptions import RestClientError
from .types import SSEEvent

__all__ = ["AbstractStreamProxy"]


LENGTH_LIMIT = 100


class AbstractStreamProxy(AbstractAsyncRESTClient):
    exception = RestClientError

    def __init__(
        self,
        user_context: ContextVar,
        timeout: httpx.Timeout | None = None,
    ) -> None:
        super().__init__(timeout=timeout, user_context=user_context)

    async def _check_response(self, response: httpx.Response) -> None:
        if not response.is_success:
            await response.aread()
            self._logger.error(
                "Response to %s failed with status %s and error %s",
                str(response.url)[:LENGTH_LIMIT],
                response.status_code,
                response.text[:LENGTH_LIMIT],
            )
            raise self.exception(response.text)

    @abc.abstractmethod
    def stream_chat(self, agent_request: AgentRequest, base_url: str) -> AsyncGenerator[SSEEvent, None]:
        raise NotImplementedError
