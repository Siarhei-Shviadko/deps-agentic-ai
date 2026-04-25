from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_update_code(test_mode_1):
    new_code = uuid4().hex

    test_mode_1.update_code(new_code)

    assert test_mode_1.code == new_code


@pytest.mark.asyncio
async def test_update_tool_sets(test_mode_1, test_tool_set_1, test_tool_set_2, test_tool_set_3):
    test_mode_1.update_tool_sets(remove=[test_tool_set_1.id()], add=[test_tool_set_3.to_data()])

    assert test_mode_1.tool_set_ids == {test_tool_set_3.id(), test_tool_set_2.id()}
