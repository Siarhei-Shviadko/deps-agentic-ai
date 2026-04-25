from http import HTTPStatus

import pytest

from deps_agentic_ai.constants import V1_API_PREFIX


@pytest.mark.asyncio
async def test_get_tool_sets__ok(client, test_tool_sets, add_tool_sets):
    response = await client.get(f"{V1_API_PREFIX}/tool-sets")

    assert response.status_code == HTTPStatus.OK

    tool_sets_info = response.json()["toolSets"]

    assert len(tool_sets_info) == len(test_tool_sets)

    tool_sets_info = sorted(tool_sets_info, key=lambda ts: ts["name"])
    tool_sets = sorted(test_tool_sets, key=lambda ts: ts.name)

    for tool_set_info, tool_set in zip(tool_sets_info, tool_sets):
        assert tool_set_info["id"] == tool_set.id()
        assert tool_set_info["code"] == tool_set.code
        assert tool_set_info["name"] == tool_set.name
        assert len(tool_set_info["tools"]) == len(tool_set.tools)

        for tool_info, tool in zip(tool_set_info["tools"], tool_set.tools):
            assert tool_info["code"] == tool.code
            assert tool_info["name"] == tool.name
            assert len(tool_info["parameters"]) == len(tool.parameters)

            for parameter_info, parameter in zip(tool_info["parameters"], tool.parameters):
                assert parameter_info["name"] == parameter.name


@pytest.mark.asyncio
async def test_delete_tool_sets__deleted(client, unit_of_work, test_tool_set_1, test_tool_set_3, add_tool_sets):
    ids = {test_tool_set_1.id(), test_tool_set_3.id()}

    assert len(await unit_of_work.tool_sets.tool_sets_of_ids(ids)) == len(ids)

    response = await client.delete(
        f"{V1_API_PREFIX}/tool-sets?id={test_tool_set_1.id()}&id={test_tool_set_3.id()}",
    )

    assert response.status_code == HTTPStatus.NO_CONTENT

    assert not await unit_of_work.tool_sets.tool_sets_of_ids(ids)
