from uuid import uuid4

import pytest

from deps_agentic_ai.domain.model.tool_set import ParameterData, ToolData


@pytest.mark.asyncio
async def test_register__tool_set_created(command_tool_set_service):
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

    await command_tool_set_service.register(code=uuid4().hex, name="NEW TS", tools=tools)


@pytest.mark.asyncio
async def test_register__tool_set_updated(command_tool_set_service, test_tool_set_1, add_tool_sets):
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

    await command_tool_set_service.register(code=test_tool_set_1.code, name="NEW TS", tools=tools)
