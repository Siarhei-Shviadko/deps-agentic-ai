import logging
from abc import ABC
from contextvars import ContextVar

import httpx
from httpx_retries import Retry, RetryTransport

from .deps_token_auth import DEPSAsyncTokenAuth

__all__ = ["AbstractAsyncRESTClient"]


DEFAULT_RETRY_TOTAL = 8
DEFAULT_RETRY_BACKOFF = 1.0
DEFAULT_TIMEOUT = httpx.Timeout(300)  # noqa: WPS43


class AbstractAsyncRESTClient(ABC):
    def __init__(
        self,
        user_context: ContextVar,
        timeout: httpx.Timeout | None = None,
    ) -> None:
        self._timeout = timeout or DEFAULT_TIMEOUT
        self._auth = DEPSAsyncTokenAuth(user_context=user_context)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._client: httpx.AsyncClient | None = None

    async def _get_or_create_client(self, base_url: str) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = await self._create_client(base_url)
        return self._client

    async def _create_client(self, base_url: str) -> httpx.AsyncClient:
        transport = RetryTransport(retry=self._create_retry_policy())

        client = httpx.AsyncClient(
            base_url=base_url,
            timeout=self._timeout,
            transport=transport,
            auth=self._auth,
        )

        self._set_client_headers(client)

        return client

    def _create_retry_policy(self) -> Retry:
        return Retry(total=DEFAULT_RETRY_TOTAL, backoff_factor=DEFAULT_RETRY_BACKOFF)

    def _set_client_headers(self, client: httpx.AsyncClient) -> None:
        pass

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "AbstractAsyncRESTClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        await self.close()
