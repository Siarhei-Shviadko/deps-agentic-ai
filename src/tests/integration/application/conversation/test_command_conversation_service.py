import random
from uuid import uuid4

import pytest

from deps_agentic_ai.domain.exceptions import (
    AgentVendorNotFound,
    ConversationNotFound,
    ModeNotFound,
)
from deps_agentic_ai.domain.model.conversation import ArgumentData


@pytest.mark.asyncio
async def test_create_conversation__no_agent_vendor__error(
    command_conversation_service,
    add_agent_vendors,
    add_modes,
    test_modes,
):
    source_mode = random.choice(test_modes)

    with pytest.raises(AgentVendorNotFound):
        await command_conversation_service.create(
            tenant_id=uuid4().hex,
            agent_vendor_id=uuid4().hex,
            mode_id=source_mode.id(),
            title=uuid4().hex,
            arguments=uuid4().hex,
            user_id=uuid4().hex,
            relation_data=uuid4().hex,
        )


@pytest.mark.asyncio
async def test_create_conversation__no_mode__error(
    command_conversation_service,
    add_agent_vendors,
    add_modes,
    test_agent_vendors,
):
    source_agent_vendor = random.choice(test_agent_vendors)

    with pytest.raises(ModeNotFound):
        await command_conversation_service.create(
            tenant_id=uuid4().hex,
            agent_vendor_id=source_agent_vendor.id(),
            mode_id=uuid4().hex,
            title=uuid4().hex,
            arguments=uuid4().hex,
            user_id=uuid4().hex,
            relation_data=uuid4().hex,
        )


@pytest.mark.asyncio
async def test_create_conversation__created(
    command_conversation_service,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
    test_agent_vendors,
    test_modes,
    test_relation_data,
):
    expected_tenant_id = uuid4().hex
    expected_title = uuid4().hex
    expected_user_id = uuid4().hex

    source_agent_vendor = random.choice(test_agent_vendors)
    source_mode = random.choice(test_modes)
    source_arguments = {
        tool_set["code"]: {
            tool["code"]: [ArgumentData(parameter=param["name"], value=uuid4().hex) for param in tool["parameters"]]
            for tool in tool_set["tools"]
        }
        for tool_set in source_mode.to_data()["tool_sets"]
    }
    conversation = await command_conversation_service.create(
        tenant_id=expected_tenant_id,
        agent_vendor_id=source_agent_vendor.id(),
        mode_id=source_mode.id(),
        title=expected_title,
        arguments=source_arguments,
        user_id=expected_user_id,
        relation_data=test_relation_data,
    )

    saved_conversation = await command_conversation_service._uow.conversations.conversation_of_id(
        id_=conversation.id(),
        user_id=expected_user_id,
        tenant_id=expected_tenant_id,
    )

    assert saved_conversation.tenant_id() == expected_tenant_id
    assert saved_conversation.agent_vendor_id() == source_agent_vendor.id()
    assert saved_conversation.mode.id == source_mode.id()
    assert saved_conversation.title == expected_title
    assert saved_conversation.created_by == expected_user_id
    assert saved_conversation.relation.details == test_relation_data["details"]
    assert saved_conversation.created_at == saved_conversation.updated_at


@pytest.mark.asyncio
async def test_delete_conversations__deleted(
    command_conversation_service,
    test_conversation_1,
    add_agent_vendors,
    add_modes,
    add_conversations,
):
    await command_conversation_service.delete_conversations(
        ids=[test_conversation_1.id()],
        user_id=test_conversation_1.created_by,
        tenant_id=test_conversation_1.tenant_id(),
    )

    with pytest.raises(ConversationNotFound):
        await command_conversation_service.conversation_of_id(
            id_=test_conversation_1.id(),
            user_id=test_conversation_1.created_by,
            tenant_id=test_conversation_1.tenant_id(),
        )


@pytest.mark.asyncio
async def test_delete_with_agent_vendor__deleted(
    command_conversation_service,
    test_conversation_1,
    add_agent_vendors,
    add_modes,
    add_conversations,
):
    await command_conversation_service.delete_with_agent_vendor(agent_vendor_id=test_conversation_1.agent_vendor_id())

    with pytest.raises(ConversationNotFound):
        await command_conversation_service.conversation_of_id(
            id_=test_conversation_1.id(),
            user_id=test_conversation_1.created_by,
            tenant_id=test_conversation_1.tenant_id(),
        )


@pytest.mark.asyncio
async def test_delete_with_document_relation__deleted(
    command_conversation_service,
    test_conversation_with_document_relation,
    add_conversations_with_relations,
    add_agent_vendors,
    add_modes,
):
    await command_conversation_service.delete_with_document_relation(
        document_id=test_conversation_with_document_relation.relation.details["documentId"]
    )

    with pytest.raises(ConversationNotFound):
        await command_conversation_service.conversation_of_id(
            id_=test_conversation_with_document_relation.id(),
            user_id=test_conversation_with_document_relation.created_by,
            tenant_id=test_conversation_with_document_relation.tenant_id(),
        )


@pytest.mark.asyncio
async def test_delete_with_document_type_relation__deleted(
    command_conversation_service,
    test_conversation_with_document_type_relation,
    add_conversations_with_relations,
    add_agent_vendors,
    add_modes,
    add_conversations,
):
    await command_conversation_service.delete_with_document_type_relation(
        document_type_id=test_conversation_with_document_type_relation.relation.details["documentTypeId"],
        tenant_id=test_conversation_with_document_type_relation.tenant_id(),
    )

    with pytest.raises(ConversationNotFound):
        await command_conversation_service.conversation_of_id(
            id_=test_conversation_with_document_type_relation.id(),
            user_id=test_conversation_with_document_type_relation.created_by,
            tenant_id=test_conversation_with_document_type_relation.tenant_id(),
        )
