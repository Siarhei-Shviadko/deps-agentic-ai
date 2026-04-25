import pytest

from deps_agentic_ai.domain.model.agent_vendor import AgentVendorFactory


@pytest.mark.parametrize(
    "params",
    [
        ("test_name", "simple_description", "http://test-url", "http://avatar-url"),
        ("H", "", "http://test-url", None),
    ],
    ids=["simple_data", "corner_data"],
)
def test_agent_vendor_factory__ok(params):
    name, description, connection_url, avatar_url = params
    agent_vendor = AgentVendorFactory.create(
        name=name,
        description=description,
        base_url=connection_url,
        avatar_url=avatar_url,
    )

    assert agent_vendor.name == name
    assert agent_vendor.description == description
    assert agent_vendor.connection_parameters.base_url == connection_url
    assert agent_vendor.active == False
    assert agent_vendor.avatar_url == avatar_url


def test_agent_vendor_activate__ok(test_inactive_agent_vendor):
    assert not test_inactive_agent_vendor.active

    test_inactive_agent_vendor.activate()

    assert test_inactive_agent_vendor.active


def test_agent_vendor_activate__active_agent_vendor__no_errors(test_inactive_agent_vendor):
    assert not test_inactive_agent_vendor.active

    test_inactive_agent_vendor.activate()
    test_inactive_agent_vendor.activate()

    assert test_inactive_agent_vendor.active


def test_agent_vendor_deactivate__ok(test_agent_vendor_active):
    test_agent_vendor_active.activate()

    assert test_agent_vendor_active.active

    test_agent_vendor_active.deactivate()

    assert not test_agent_vendor_active.active


def test_agent_vendor_deactivate__not_active_agent_vendor__no_errors(test_agent_vendor_active):
    test_agent_vendor_active.activate()

    assert test_agent_vendor_active.active

    test_agent_vendor_active.deactivate()
    test_agent_vendor_active.deactivate()

    assert not test_agent_vendor_active.active


def test_agent_vendor_update_info__ok(test_agent_vendor_active):
    new_name = "new_name"
    new_description = "new_description"
    new_avatar_url = "http://new-avatar-url"

    test_agent_vendor_active.update_info(name=new_name, description=new_description, avatar_url=new_avatar_url)

    assert test_agent_vendor_active.name == new_name
    assert test_agent_vendor_active.description == new_description
    assert test_agent_vendor_active.avatar_url == new_avatar_url


def test_agent_vendor_update_info__with_none_avatar__ok(test_agent_vendor_active):
    original_avatar_url = test_agent_vendor_active.avatar_url
    new_name = "new_name"
    new_description = "new_description"

    test_agent_vendor_active.update_info(name=new_name, description=new_description, avatar_url=None)

    assert test_agent_vendor_active.name == new_name
    assert test_agent_vendor_active.description == new_description
    assert test_agent_vendor_active.avatar_url == original_avatar_url


def test_agent_vendor_update_connection_parameters__ok(test_agent_vendor_active):
    new_base_url = "http://new-base-url"

    test_agent_vendor_active.update_connection_parameters(base_url=new_base_url)

    assert test_agent_vendor_active.connection_parameters.base_url == new_base_url
