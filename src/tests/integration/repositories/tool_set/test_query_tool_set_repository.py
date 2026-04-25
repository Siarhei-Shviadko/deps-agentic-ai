import pytest


@pytest.mark.asyncio
async def test_find_all(test_tool_sets, query_tool_set_repository, add_tool_sets):
    tool_sets = await query_tool_set_repository.find_all()

    assert len(tool_sets["tool_sets"]) == len(test_tool_sets)

    tool_sets_info = sorted(tool_sets["tool_sets"], key=lambda ts: ts["name"])
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
