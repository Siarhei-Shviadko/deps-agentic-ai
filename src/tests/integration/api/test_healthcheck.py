from http import HTTPStatus

import pytest

from deps_agentic_ai import constants

endpoint = constants.BASE_API_PREFIX


@pytest.mark.asyncio
async def test_healthcheck__connection_work__200(client):
    response = await client.get(f"{endpoint}/healthcheck")

    assert response.status_code == HTTPStatus.OK
