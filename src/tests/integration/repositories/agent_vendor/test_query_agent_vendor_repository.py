import pytest


@pytest.mark.asyncio
async def test_find_all_agent_vendors__agent_vendors_exist__ok(
    query_agent_vendor_repository,
    test_agent_vendors,
    add_agent_vendors,
):
    agent_vendors = await query_agent_vendor_repository.find_all()

    assert len(agent_vendors["agent_vendors"]) == len(test_agent_vendors)


@pytest.mark.asyncio
async def test_find_all_agent_vendors__agent_vendors_dont_exist__no_error(query_agent_vendor_repository):
    agent_vendors = await query_agent_vendor_repository.find_all()

    assert not agent_vendors["agent_vendors"]
