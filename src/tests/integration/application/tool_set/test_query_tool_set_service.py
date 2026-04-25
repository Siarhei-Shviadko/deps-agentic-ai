import pytest


@pytest.mark.asyncio
async def test_find_all(test_tool_sets, query_tool_set_service, add_tool_sets):
    tool_sets = await query_tool_set_service.find_all()

    assert len(tool_sets["tool_sets"]) == len(test_tool_sets)
