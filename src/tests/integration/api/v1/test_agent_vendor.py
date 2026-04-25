import http
from random import choice
from uuid import uuid4

import pytest

from deps_agentic_ai.constants import INTERNAL_API_PREFIX, V1_API_PREFIX


@pytest.mark.asyncio
async def test_get_agent_vendors__ok(client, add_agent_vendors, test_agent_vendors):
    response = await client.get(f"{V1_API_PREFIX}/agent-vendors")
    assert response.status_code == http.HTTPStatus.OK

    agent_vendors = response.json()["agentVendors"]

    assert agent_vendors

    for agent_vendor, orig_agent_vendor in zip(
        sorted(agent_vendors, key=lambda item: item["id"]), sorted(test_agent_vendors, key=lambda item: item.id())
    ):
        assert agent_vendor["id"] == orig_agent_vendor.id()
        assert agent_vendor["name"] == orig_agent_vendor.name
        assert agent_vendor["description"] == orig_agent_vendor.description
        assert agent_vendor["active"] == orig_agent_vendor.active
        assert agent_vendor["avatarUrl"] == orig_agent_vendor.avatar_url
        assert agent_vendor["connectionParameters"]["baseUrl"] == orig_agent_vendor.connection_parameters.base_url


@pytest.mark.asyncio
async def test_activate_agent_vendor__204_status(client, add_agent_vendors, test_agent_vendors):
    agent_vendor_for_activation = choice(test_agent_vendors)
    response = await client.patch(f"{V1_API_PREFIX}/agent-vendors/{agent_vendor_for_activation.id()}/activate")
    assert response.status_code == http.HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_activate_agent_vendor__wrong_id__404_status(client, add_agent_vendors, test_agent_vendors):
    response = await client.patch(f"{V1_API_PREFIX}/agent-vendors/fake_id/activate")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_delete_agent_vendor__204_status(client, add_agent_vendors, test_agent_vendors):
    agent_vendor = test_agent_vendors[0]
    response = await client.delete(f"{V1_API_PREFIX}/agent-vendors/{agent_vendor.id()}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_agent_vendor__wrong_id__404_status(client):
    response = await client.delete(f"{V1_API_PREFIX}/agent-vendors/non_existing_id")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_update_agent_vendor_info__ok(client, add_agent_vendors, test_agent_vendors):
    agent_vendor = choice(test_agent_vendors)
    payload = {
        "name": uuid4().hex,
        "description": uuid4().hex,
        "avatarUrl": uuid4().hex,
    }
    response = await client.patch(f"{V1_API_PREFIX}/agent-vendors/{agent_vendor.id()}/info", json=payload)
    assert response.status_code == http.HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_update_agent_vendor_info__with_none_avatar__ok(client, add_agent_vendors, test_agent_vendors):
    agent_vendor = choice(test_agent_vendors)
    payload = {
        "name": uuid4().hex,
        "description": uuid4().hex,
        "avatarUrl": None,
    }
    response = await client.patch(f"{V1_API_PREFIX}/agent-vendors/{agent_vendor.id()}/info", json=payload)
    assert response.status_code == http.HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_update_agent_vendor_info__wrong_id__404_status(client):
    payload = {
        "name": uuid4().hex,
        "description": uuid4().hex,
        "avatarUrl": uuid4().hex,
    }
    response = await client.patch(f"{V1_API_PREFIX}/agent-vendors/fake_id/info", json=payload)
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_update_agent_vendor_info__name_already_exists__409_status(client, add_agent_vendors, test_agent_vendors):
    agent_vendor_1 = test_agent_vendors[0]
    agent_vendor_2 = test_agent_vendors[1]
    payload = {
        "name": agent_vendor_2.name,
        "description": uuid4().hex,
        "avatarUrl": uuid4().hex,
    }
    response = await client.patch(f"{V1_API_PREFIX}/agent-vendors/{agent_vendor_1.id()}/info", json=payload)
    assert response.status_code == http.HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_update_agent_vendor_connection_parameters__ok(client, add_agent_vendors, test_agent_vendors):
    agent_vendor = choice(test_agent_vendors)
    payload = {
        "baseUrl": uuid4().hex,
    }
    response = await client.patch(
        f"{V1_API_PREFIX}/agent-vendors/{agent_vendor.id()}/connection-parameters", json=payload
    )
    assert response.status_code == http.HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_update_agent_vendor_connection_parameters__wrong_id__404_status(client):
    payload = {
        "baseUrl": uuid4().hex,
    }
    response = await client.patch(f"{V1_API_PREFIX}/agent-vendors/fake_id/connection-parameters", json=payload)
    assert response.status_code == http.HTTPStatus.NOT_FOUND
