import pytest

from deps_agentic_ai.domain.model.tool_set import ParameterData, ToolData


@pytest.mark.asyncio
async def test_save__tool_set_created(test_tool_set_1_code, test_tool_set_1, unit_of_work):
    async with unit_of_work:
        await unit_of_work.tool_sets.save(test_tool_set_1)

        assert (await unit_of_work.tool_sets.tool_set_with_code(test_tool_set_1_code)).equals(test_tool_set_1)


@pytest.mark.asyncio
async def test_save__tool_set_updated(test_tool_set_1_code, test_tool_set_1, unit_of_work, add_tool_sets):
    async with unit_of_work:
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

        test_tool_set_1.update(name="NEW TS", tools=tools)

        await unit_of_work.tool_sets.save(test_tool_set_1)

        assert (await unit_of_work.tool_sets.tool_set_with_code(test_tool_set_1_code)).equals(test_tool_set_1)


@pytest.mark.asyncio
async def test_delete_all__tool_sets_deleted(test_tool_set_1, test_tool_set_3, unit_of_work, add_tool_sets):
    async with unit_of_work:
        ids = [test_tool_set_1.id(), test_tool_set_3.id()]

        assert len(await unit_of_work.tool_sets.tool_sets_of_ids(ids)) == len(ids)

        await unit_of_work.tool_sets.delete_all([test_tool_set_1, test_tool_set_3])

        assert not await unit_of_work.tool_sets.tool_sets_of_ids(ids)
