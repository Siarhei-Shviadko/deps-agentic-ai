from uuid import uuid4

import pytest

from deps_agentic_ai.domain.exceptions import ModeAlreadyExists, ToolSetsNotFound


@pytest.mark.asyncio
async def test_create_mode__mode_created(command_mode_service, test_tool_set_1, test_tool_set_2, add_tool_sets):
    code = "test"
    tool_set_ids = [test_tool_set_1.id(), test_tool_set_2.id()]

    mode = await command_mode_service.create(code=code, tool_set_ids=tool_set_ids)

    assert mode.code == code
    assert len(mode.tool_sets) == len(tool_set_ids)


@pytest.mark.asyncio
async def test_create_mode__mode_already_exists(
    command_mode_service,
    test_mode_1,
    test_tool_set_1,
    test_tool_set_2,
    add_modes,
    add_tool_sets,
):
    code = test_mode_1.code
    tool_set_ids = [test_tool_set_1.id(), test_tool_set_2.id()]

    with pytest.raises(ModeAlreadyExists):
        await command_mode_service.create(code=code, tool_set_ids=tool_set_ids)


@pytest.mark.asyncio
async def test_create_mode__tool_sets_not_found(
    command_mode_service,
    test_tool_set_1,
    test_tool_set_2,
    add_modes,
    add_tool_sets,
):
    code = "test"
    tool_set_ids = [test_tool_set_1.id(), test_tool_set_2.id(), uuid4().hex]

    with pytest.raises(ToolSetsNotFound):
        await command_mode_service.create(code=code, tool_set_ids=tool_set_ids)


@pytest.mark.asyncio
async def test_delete_mode__deleted(command_mode_service, test_mode_1, test_mode_2, add_modes, add_tool_sets):
    mode_ids = [test_mode_1.id(), test_mode_2.id()]

    await command_mode_service.delete(mode_ids)


@pytest.mark.asyncio
async def test_update_mode_code__updated(command_mode_service, test_mode_1, add_modes, add_tool_sets):
    new_code = uuid4().hex

    mode = await command_mode_service.update_code(id_=test_mode_1.id(), code=new_code)

    assert mode.code == new_code


@pytest.mark.asyncio
async def test_update_mode_code__mode_with_code_already_exists(
    command_mode_service, test_mode_1, test_mode_2, add_modes, add_tool_sets
):
    new_code = test_mode_2.code

    with pytest.raises(ModeAlreadyExists):
        await command_mode_service.update_code(id_=test_mode_1.id(), code=new_code)


@pytest.mark.asyncio
async def test_update_tool_sets__updated(
    command_mode_service,
    test_mode_1,
    test_tool_set_1,
    test_tool_set_2,
    test_tool_set_3,
    add_modes,
    add_tool_sets,
):
    mode = await command_mode_service.update_tool_sets(
        id_=test_mode_1.id(),
        tool_sets_to_add_ids=[test_tool_set_3.id()],
        tool_sets_to_remove_ids=[test_tool_set_1.id()],
    )

    assert mode.tool_set_ids == {test_tool_set_2.id(), test_tool_set_3.id()}


@pytest.mark.asyncio
async def test_update_tool_sets__tool_sets_not_found(
    command_mode_service,
    test_mode_1,
    test_tool_set_1,
    test_tool_set_3,
    add_modes,
):
    with pytest.raises(ToolSetsNotFound):
        await command_mode_service.update_tool_sets(
            id_=test_mode_1.id(),
            tool_sets_to_add_ids=[test_tool_set_3.id()],
            tool_sets_to_remove_ids=[test_tool_set_1.id()],
        )
