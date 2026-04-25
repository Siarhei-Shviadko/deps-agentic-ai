import json
from collections import defaultdict
from contextvars import ContextVar
from typing import Any, AsyncGenerator, TypeAlias

import httpx

from deps_agentic_ai.domain.model.conversation import AgentRequest

from ..abstract_stream_proxy import AbstractStreamProxy
from ..constants import DEFAULT_PROXY_TIMEOUT
from ..exceptions import AgentVendorProxyError
from ..sse_event_parser import SSEEventParser
from ..types import SSEEvent, SSEEventType

__all__ = ["AgentVendorProxy"]


toolDataCode: TypeAlias = str


class AgentVendorProxy(AbstractStreamProxy):
    exception = AgentVendorProxyError

    def __init__(
        self,
        user_context: ContextVar,
        timeout: int = DEFAULT_PROXY_TIMEOUT,
    ) -> None:
        super().__init__(user_context=user_context, timeout=httpx.Timeout(timeout))

    async def stream_chat(self, agent_request: AgentRequest, base_url: str) -> AsyncGenerator[SSEEvent, None]:
        agent_url = f"{base_url}"
        params = {"request": json.dumps(self._build_request_params(agent_request))}

        client = await self._get_or_create_client(base_url)

        async with client.stream("GET", agent_url, params=params) as response:
            await self._check_response(response)

            parser = SSEEventParser()
            async for event in self._parse_sse_stream(response, parser):
                yield event

    async def _parse_sse_stream(
        self, response: httpx.Response, parser: SSEEventParser
    ) -> AsyncGenerator[SSEEvent, None]:
        async for line in response.aiter_lines():
            event = parser.parse_line(line)
            if event:
                yield event
                if event.type == SSEEventType.FINAL:
                    break

    def _build_request_params(self, agent_request: AgentRequest) -> dict[str, Any]:
        arguments = defaultdict(list)

        for _, active_tools in agent_request.context["tools"].items():
            for active_tool in active_tools:
                for arg in active_tool.get("arguments", {}):
                    arguments[arg["parameter"]].append({"value": arg["value"]})

        return {
            "conversationId": agent_request.conversation_id,
            "turnId": agent_request.completion_id,
            "userQuestion": agent_request.question,
            "activeToolSets": list(agent_request.active_tool_sets),
            "contextBundle": agent_request.context_bundle,
            "arguments": arguments,
        }
