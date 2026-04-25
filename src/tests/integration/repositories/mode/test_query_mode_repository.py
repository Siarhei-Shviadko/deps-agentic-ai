import pytest

from deps_agentic_ai.domain.model.mode import ModeFiltering


@pytest.mark.asyncio
async def test_find_all(test_modes, query_mode_repository, add_modes, add_tool_sets):
    modes = await query_mode_repository.find_all()

    assert len(modes["modes"]) == len(test_modes)

    modes_info = sorted(modes["modes"], key=lambda m: m["code"])
    modes = sorted(test_modes, key=lambda m: m.code)

    for mode_info, mode in zip(modes_info, modes):
        assert mode_info["id"] == mode.id()
        assert mode_info["code"] == mode.code

        tool_sets_info = sorted(mode_info["tool_sets"], key=lambda ts: ts["name"])
        tool_sets = sorted(mode.tool_sets.values(), key=lambda ts: ts.name)

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
async def test_find_all__with_filtering(test_modes, test_mode_1, query_mode_repository, add_modes, add_tool_sets):
    modes = (await query_mode_repository.find_all(filtering=ModeFiltering(code=test_mode_1.code)))["modes"]

    assert len(modes) == 1

    mode_info = modes[0]
    mode = test_mode_1

    assert mode_info["id"] == mode.id()
    assert mode_info["code"] == mode.code
