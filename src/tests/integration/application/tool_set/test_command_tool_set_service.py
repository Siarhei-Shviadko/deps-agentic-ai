from uuid import uuid4

import pytest

from deps_agentic_ai.domain.model.tool_set import ParameterData, ToolData


@pytest.mark.asyncio
async def test_register__tool_set_created(command_tool_set_service, unit_of_work):
    tools = [
        ToolData(
            code="new_t1",
            name="new_T1",
            parameters=[
                ParameterData(name="new_p11"),
                ParameterData(name="new_p12"),
            ],
        )
    ]

    tool_set = await command_tool_set_service.register(code=uuid4().hex, name="NEW TS", tools=tools)

    assert await unit_of_work.tool_sets.tool_set_with_code(tool_set.code) == tool_set


@pytest.mark.asyncio
async def test_register__tool_set_updated(command_tool_set_service, test_tool_set_1, unit_of_work):
    tools = [
        ToolData(
            code="new_t1",
            name="new_T1",
            parameters=[
                ParameterData(name="new_p11"),
                ParameterData(name="new_p12"),
            ],
        )
    ]

    tool_set = await command_tool_set_service.register(code=test_tool_set_1.code, name="NEW TS", tools=tools)

    assert await unit_of_work.tool_sets.tool_set_with_code(tool_set.code) == tool_set


@pytest.mark.asyncio
async def test_delete__tool_sets_deleted(
    command_tool_set_service, test_tool_set_1, test_tool_set_3, unit_of_work, add_tool_sets
):
    ids = {test_tool_set_1.id(), test_tool_set_3.id()}

    assert len(await unit_of_work.tool_sets.tool_sets_of_ids(ids)) == len(ids)

    assert {ts.id() for ts in await command_tool_set_service.delete(ids)} == ids

    assert not await unit_of_work.tool_sets.tool_sets_of_ids(ids)
