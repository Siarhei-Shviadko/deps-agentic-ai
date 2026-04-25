from http import HTTPStatus
from uuid import uuid4

import pytest

from deps_agentic_ai.constants import INTERNAL_API_PREFIX


@pytest.mark.asyncio
async def test_register_tool_set__registered(client, unit_of_work):
    code = uuid4().hex
    name = uuid4().hex
    tools = [
        {
            "code": "t1",
            "name": "T1",
            "parameters": [{"name": "p1"}, {"name": "p2"}],
        },
        {
            "code": "t2",
            "name": "T2",
            "parameters": [{"name": "p3"}, {"name": "p4"}],
        },
    ]

    response = await client.put(
        f"{INTERNAL_API_PREFIX}/tool-sets",
        json={
            "code": code,
            "name": name,
            "tools": tools,
        },
    )

    assert response.status_code == HTTPStatus.CREATED

    tool_set_id = response.json()["id"]

    assert tool_set_id is not None

    tool_set = await unit_of_work.tool_sets.tool_set_with_code(code)

    assert tool_set.id() == tool_set_id
    assert tool_set.name == name
    assert tool_set.code == code

    for tool_data, tool in zip(tools, tool_set.tools):
        assert tool_data["code"] == tool.code
        assert tool_data["name"] == tool.name
        assert len(tool_data["parameters"]) == len(tool.parameters)

        for parameter_info, parameter in zip(tool_data["parameters"], tool.parameters):
            assert parameter_info["name"] == parameter.name


@pytest.mark.asyncio
async def test_register_tool_set__tool_code_is_not_unique(client, test_tool_set_1):
    response = await client.put(
        f"{INTERNAL_API_PREFIX}/tool-sets",
        json={
            "code": test_tool_set_1.code,
            "name": test_tool_set_1.name,
            "tools": [
                {
                    "code": "t1",
                    "name": "T1",
                    "parameters": [{"name": "p1"}, {"name": "p2"}],
                },
                {
                    "code": "t1",
                    "name": "T2",
                    "parameters": [{"name": "p3"}, {"name": "p4"}],
                },
            ],
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_register_tool_set__parameter_name_is_not_unique(client, test_tool_set_1):
    response = await client.put(
        f"{INTERNAL_API_PREFIX}/tool-sets",
        json={
            "code": test_tool_set_1.code,
            "name": test_tool_set_1.name,
            "tools": [
                {
                    "code": "t1",
                    "name": "T1",
                    "parameters": [{"name": "p1"}, {"name": "p2"}],
                },
                {
                    "code": "t2",
                    "name": "T2",
                    "parameters": [{"name": "p3"}, {"name": "p3"}],
                },
            ],
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
