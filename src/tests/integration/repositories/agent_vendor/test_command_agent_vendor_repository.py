import pytest
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
async def test_save_all_agent_vendors__saved(unit_of_work, test_agent_vendors):
    async with unit_of_work:
        await unit_of_work.agent_vendors.save_all(test_agent_vendors)

        for agent_vendor in test_agent_vendors:
            res = await unit_of_work.agent_vendors.has_agent_vendor_with_name(agent_vendor.name)
            assert res


@pytest.mark.asyncio
async def test_save_agent_vendor__saved(unit_of_work, test_agent_vendor_active):
    assert not await unit_of_work.agent_vendors.has_agent_vendor_with_name(test_agent_vendor_active.name)

    async with unit_of_work:
        await unit_of_work.agent_vendors.save(test_agent_vendor_active)
        await unit_of_work.commit()

    assert unit_of_work.agent_vendors.has_agent_vendor_with_name(test_agent_vendor_active.name)


@pytest.mark.asyncio
async def test_save_agent_vendor_with_duplicated_name__error(
    unit_of_work, test_agent_vendor_active, test_agent_vendor_2
):
    async with unit_of_work:
        await unit_of_work.agent_vendors.save(test_agent_vendor_active)
        test_agent_vendor_2.name = test_agent_vendor_active.name

        await unit_of_work.commit()

        with pytest.raises(IntegrityError):
            await unit_of_work.agent_vendors.save(test_agent_vendor_2)


@pytest.mark.asyncio
async def test_get_active_agent_vendor__no_active_vendor__no_errors(unit_of_work, test_inactive_agent_vendors):
    async with unit_of_work:
        await unit_of_work.agent_vendors.save_all(test_inactive_agent_vendors)
        await unit_of_work.commit()

        active_agent_vendor = await unit_of_work.agent_vendors.active_agent_vendor()
        assert not active_agent_vendor


@pytest.mark.asyncio
async def test_get_active_agent_vendor__active_vendor_exists__gotten(unit_of_work, test_agent_vendors):
    async with unit_of_work:
        test_agent_vendors[0].activate()
        await unit_of_work.agent_vendors.save_all(test_agent_vendors)
        await unit_of_work.commit()

        active_agent_vendor = await unit_of_work.agent_vendors.active_agent_vendor()
        assert active_agent_vendor
        assert active_agent_vendor.id == test_agent_vendors[0].id


@pytest.mark.asyncio
async def test_delete__removed(
    unit_of_work,
    test_agent_vendor_active,
):
    async with unit_of_work:
        await unit_of_work.agent_vendors.save(test_agent_vendor_active)

        assert await unit_of_work.agent_vendors.agent_vendor_of_id(test_agent_vendor_active.id())
        await unit_of_work.agent_vendors.delete(test_agent_vendor_active)
        await unit_of_work.commit()

    async with unit_of_work:
        assert await unit_of_work.agent_vendors.agent_vendor_of_id(test_agent_vendor_active.id()) is None
