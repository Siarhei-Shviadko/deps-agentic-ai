import pytest


@pytest.mark.asyncio
async def test_save__mode_created(unit_of_work, test_mode_1, add_tool_sets):
    async with unit_of_work:
        await unit_of_work.modes.save(test_mode_1)

        assert (await unit_of_work.modes.mode_of_id(test_mode_1.id())).equals(test_mode_1)


@pytest.mark.asyncio
async def test_modes_of_ids(unit_of_work, test_modes, add_modes, add_tool_sets):
    async with unit_of_work:
        test_modes = sorted(test_modes, key=lambda m: m.id())
        modes = sorted(await unit_of_work.modes.modes_of_ids([m.id() for m in test_modes]), key=lambda m: m.id())

        assert len(modes) == len(test_modes)

        for mode, test_mode in zip(modes, test_modes):
            assert mode.equals(test_mode)


@pytest.mark.asyncio
async def test_mode_of_id__tool_sets_deleted(unit_of_work, test_mode_1, add_modes):
    async with unit_of_work:
        mode = await unit_of_work.modes.mode_of_id(test_mode_1.id())

        assert mode
        assert mode.id == test_mode_1.id
        assert not mode.tool_sets


@pytest.mark.asyncio
async def test_mode_of_id__some_tool_sets_deleted(unit_of_work, test_mode_1, test_tool_set_1, add_modes):
    async with unit_of_work:
        await unit_of_work.tool_sets.save(test_tool_set_1)

        mode = await unit_of_work.modes.mode_of_id(test_mode_1.id())

        assert mode
        assert mode.id == test_mode_1.id
        assert len(mode.tool_sets) == 1
        assert list(mode.tool_sets.values())[0].id == test_tool_set_1.id


@pytest.mark.asyncio
async def test_delete_all(unit_of_work, test_mode_1, test_mode_2, test_mode_3, add_modes):
    async with unit_of_work:
        assert len(await unit_of_work.modes.modes_of_ids([test_mode_1.id(), test_mode_2.id(), test_mode_3.id()])) == 3

        await unit_of_work.modes.delete_all([test_mode_1, test_mode_2])

        modes = await unit_of_work.modes.modes_of_ids([test_mode_1.id(), test_mode_2.id(), test_mode_3.id()])

        assert len(modes) == 1
        assert modes[0] == test_mode_3


@pytest.mark.asyncio
async def test_mode_of_id_data__mode_exists(unit_of_work, test_mode_1, add_modes, add_tool_sets):
    async with unit_of_work:
        assert await unit_of_work.modes.mode_of_id_data(test_mode_1.id()) == test_mode_1.to_data()


@pytest.mark.asyncio
async def test_mode_of_id_data__mode_does_not_exist(unit_of_work, test_mode_1):
    async with unit_of_work:
        assert await unit_of_work.modes.mode_of_id_data(test_mode_1.id()) is None


@pytest.mark.asyncio
async def test_has_mode_with_code__mode_exists(unit_of_work, test_mode_1, add_modes):
    async with unit_of_work:
        assert await unit_of_work.modes.has_mode_with_code(test_mode_1.code)


@pytest.mark.asyncio
async def test_has_mode_with_code__mode_does_not_exist(
    unit_of_work,
    test_mode_1,
):
    async with unit_of_work:
        assert not (await unit_of_work.modes.has_mode_with_code(test_mode_1.code))
