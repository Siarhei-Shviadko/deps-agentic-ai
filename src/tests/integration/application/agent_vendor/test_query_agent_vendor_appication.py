import pytest


@pytest.mark.asyncio
async def test_query_agent_vendor_service__find_all__ok(
    query_agent_vendor_service,
    test_agent_vendors,
    add_agent_vendors,
):
    agent_vendors_info = await query_agent_vendor_service.find_all()

    assert len(agent_vendors_info["agent_vendors"]) == len(test_agent_vendors)

    for agent_vendor_info, agent_vendor in zip(
        sorted(agent_vendors_info["agent_vendors"], key=lambda item: item["id"]),
        sorted(test_agent_vendors, key=lambda item: item.id()),
    ):
        assert agent_vendor_info["id"] == agent_vendor.id()
        assert agent_vendor_info["name"] == agent_vendor.name
        assert agent_vendor_info["description"] == agent_vendor.description
        assert agent_vendor_info["active"] == agent_vendor.active
        assert agent_vendor_info["avatar_url"] == agent_vendor.avatar_url
        assert agent_vendor_info["connection_parameters"]["base_url"] == agent_vendor.connection_parameters.base_url
