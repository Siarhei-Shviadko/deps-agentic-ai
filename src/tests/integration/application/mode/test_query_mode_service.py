import pytest


@pytest.mark.asyncio
async def test_find_all(test_modes, query_mode_service, add_modes, add_tool_sets):
    modes = await query_mode_service.find_all()

    assert len(modes["modes"]) == len(test_modes)


@pytest.mark.asyncio
async def test_find_all__with_code(test_modes, test_mode_1, query_mode_service, add_modes, add_tool_sets):
    modes = await query_mode_service.find_all(code=test_mode_1.code)

    assert len(modes["modes"]) == 1
