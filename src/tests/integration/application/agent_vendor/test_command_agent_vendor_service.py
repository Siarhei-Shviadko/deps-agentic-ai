from random import choice
from uuid import uuid4

import pytest

from deps_agentic_ai.domain.exceptions import (
    AgentVendorAlreadyExists,
    AgentVendorNotFound,
)


@pytest.mark.asyncio
async def test_create_agent_vendor__created(command_agent_vendor_service):
    expected_name = uuid4().hex
    expected_description = uuid4().hex
    expected_base_url = uuid4().hex
    expected_avatar_url = choice([uuid4().hex, None])

    agent_vendor = await command_agent_vendor_service.create(
        name=expected_name,
        description=expected_description,
        base_url=expected_base_url,
        avatar_url=expected_avatar_url,
    )

    assert agent_vendor.name == expected_name
    assert agent_vendor.description == expected_description
    assert agent_vendor.avatar_url == expected_avatar_url
    assert agent_vendor.active is False
    assert agent_vendor.connection_parameters.base_url == expected_base_url


@pytest.mark.asyncio
async def test_create_agent_vendor__agent_vendor_with_name_exists__error(command_agent_vendor_service):
    name = uuid4().hex
    description = uuid4().hex
    base_url = uuid4().hex
    avatar_url = choice([uuid4().hex, None])

    await command_agent_vendor_service.create(
        name=name,
        description=description,
        base_url=base_url,
        avatar_url=avatar_url,
    )
    with pytest.raises(AgentVendorAlreadyExists) as err:
        await command_agent_vendor_service.create(
            name=name,
            description="test_desc",
            base_url="test_url",
            avatar_url="test_url",
        )

    assert name in err.value.args[0]


@pytest.mark.asyncio
async def test_activate_agent_vendor__no_active_vendors__activated(
    command_agent_vendor_service, test_inactive_agent_vendors, add_incative_agent_vendors
):
    target_agent_vendor = choice(test_inactive_agent_vendors)

    assert not target_agent_vendor.active

    await command_agent_vendor_service.activate(target_agent_vendor.id())

    saved_agent_vendor = await command_agent_vendor_service._uow.agent_vendors.agent_vendor_of_id(
        target_agent_vendor.id()
    )

    assert saved_agent_vendor.active


@pytest.mark.asyncio
async def test_activate_agent_vendor__active_vendor_exists__activated_new_and_deactivate_old(
    unit_of_work, command_agent_vendor_service, test_inactive_agent_vendors
):
    active_agent_vendor = choice(test_inactive_agent_vendors)
    active_agent_vendor.activate()

    deactive_agent_vendor = next(
        (agent_vendor for agent_vendor in test_inactive_agent_vendors if not agent_vendor.active)
    )

    async with unit_of_work:
        await unit_of_work.agent_vendors.save_all(test_inactive_agent_vendors)
        await unit_of_work.commit()

    await command_agent_vendor_service.activate(deactive_agent_vendor.id())

    expected_active_agent_vendor = await command_agent_vendor_service._uow.agent_vendors.agent_vendor_of_id(
        deactive_agent_vendor.id()
    )
    expected_deactive_agent_vendor = await command_agent_vendor_service._uow.agent_vendors.agent_vendor_of_id(
        active_agent_vendor.id()
    )

    assert expected_active_agent_vendor.active
    assert not expected_deactive_agent_vendor.active


@pytest.mark.asyncio
async def test_activate_agent_vendor__wrong_id__error(command_agent_vendor_service, add_agent_vendors):
    with pytest.raises(AgentVendorNotFound):
        await command_agent_vendor_service.activate("fake_id")


@pytest.mark.asyncio
async def test_activate_agent_vendor__active_vendor_already_activated__no_errors(
    unit_of_work, command_agent_vendor_service, test_agent_vendors
):
    active_agent_vendor = choice(test_agent_vendors)
    active_agent_vendor.activate()

    async with unit_of_work:
        await unit_of_work.agent_vendors.save_all(test_agent_vendors)
        await unit_of_work.commit()

    activated_agent_vendor = await command_agent_vendor_service.activate(active_agent_vendor.id())

    assert activated_agent_vendor == active_agent_vendor


@pytest.mark.asyncio
async def test_update_info__ok(command_agent_vendor_service, test_agent_vendors, add_agent_vendors):
    target_agent_vendor = choice(test_agent_vendors)
    new_name = uuid4().hex
    new_description = uuid4().hex
    new_avatar_url = uuid4().hex

    updated_agent_vendor = await command_agent_vendor_service.update_info(
        id_=target_agent_vendor.id(),
        name=new_name,
        description=new_description,
        avatar_url=new_avatar_url,
    )

    assert updated_agent_vendor.name == new_name
    assert updated_agent_vendor.description == new_description
    assert updated_agent_vendor.avatar_url == new_avatar_url

    saved_agent_vendor = await command_agent_vendor_service._uow.agent_vendors.agent_vendor_of_id(
        target_agent_vendor.id()
    )

    assert saved_agent_vendor.name == new_name
    assert saved_agent_vendor.description == new_description
    assert saved_agent_vendor.avatar_url == new_avatar_url


@pytest.mark.asyncio
async def test_update_info__with_none_avatar__ok(command_agent_vendor_service, test_agent_vendors, add_agent_vendors):
    target_agent_vendor = choice(test_agent_vendors)
    original_avatar_url = target_agent_vendor.avatar_url
    new_name = uuid4().hex
    new_description = uuid4().hex

    updated_agent_vendor = await command_agent_vendor_service.update_info(
        id_=target_agent_vendor.id(),
        name=new_name,
        description=new_description,
        avatar_url=None,
    )

    assert updated_agent_vendor.name == new_name
    assert updated_agent_vendor.description == new_description
    assert updated_agent_vendor.avatar_url == original_avatar_url


@pytest.mark.asyncio
async def test_update_info__wrong_id__error(command_agent_vendor_service):
    with pytest.raises(AgentVendorNotFound):
        await command_agent_vendor_service.update_info(
            id_="fake_id",
            name="test_name",
            description="test_description",
            avatar_url=None,
        )


@pytest.mark.asyncio
async def test_update_info__name_already_exists__error(
    command_agent_vendor_service, test_agent_vendors, add_agent_vendors
):
    agent_vendor_1 = test_agent_vendors[0]
    agent_vendor_2 = test_agent_vendors[1]

    with pytest.raises(AgentVendorAlreadyExists) as err:
        await command_agent_vendor_service.update_info(
            id_=agent_vendor_1.id(),
            name=agent_vendor_2.name,
            description="test_description",
            avatar_url=None,
        )

    assert agent_vendor_2.name in err.value.args[0]


@pytest.mark.asyncio
async def test_update_connection_parameters__ok(command_agent_vendor_service, test_agent_vendors, add_agent_vendors):
    target_agent_vendor = choice(test_agent_vendors)
    new_base_url = uuid4().hex

    updated_agent_vendor = await command_agent_vendor_service.update_connection_parameters(
        id_=target_agent_vendor.id(),
        base_url=new_base_url,
    )

    assert updated_agent_vendor.connection_parameters.base_url == new_base_url

    saved_agent_vendor = await command_agent_vendor_service._uow.agent_vendors.agent_vendor_of_id(
        target_agent_vendor.id()
    )

    assert saved_agent_vendor.connection_parameters.base_url == new_base_url


@pytest.mark.asyncio
async def test_update_connection_parameters__wrong_id__error(command_agent_vendor_service):
    with pytest.raises(AgentVendorNotFound):
        await command_agent_vendor_service.update_connection_parameters(
            id_="fake_id",
            base_url="test_url",
        )
