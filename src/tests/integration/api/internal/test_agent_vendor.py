import http
from uuid import uuid4

import pytest

from deps_agentic_ai.constants import INTERNAL_API_PREFIX


@pytest.mark.asyncio
async def test_create_agent_vendor__ok(client):
    payload = {"name": uuid4().hex, "description": uuid4().hex, "baseUrl": uuid4().hex, "avatarUrl": uuid4().hex}
    response = await client.post(f"{INTERNAL_API_PREFIX}/agent-vendors", json=payload)

    assert response.status_code == http.HTTPStatus.CREATED
    assert response.json()["id"]
