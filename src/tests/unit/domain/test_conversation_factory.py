import pytest

from deps_agentic_ai.domain.model.agent_vendor import AgentVendorId
from deps_agentic_ai.domain.model.conversation import ConversationFactory
from deps_agentic_ai.domain.model.conversation.conversation import Conversation


@pytest.mark.parametrize(
    "params",
    [
        ("tenant_1", "agent_vendor_1", "Test Conversation", "user_1"),
    ],
    ids=["simple_data"],
)
def test_conversation_factory_create__ok(
    params,
    test_mode_data_1,
    test_raw_arguments_1,
):
    tenant_id, agent_vendor_id, title, user_id = params

    conversation = ConversationFactory.create(
        tenant_id=tenant_id,
        agent_provider_id=AgentVendorId(agent_vendor_id),
        mode=test_mode_data_1,
        relation=None,
        arguments=test_raw_arguments_1,
        title=title,
        user_id=user_id,
    )

    assert isinstance(conversation, Conversation)

    assert conversation.tenant_id() == tenant_id
    assert conversation.agent_vendor_id() == agent_vendor_id
    assert conversation.title == title
    assert conversation.created_by == user_id

    assert conversation.created_at
    assert conversation.updated_at
    assert conversation.created_at == conversation.updated_at

    assert conversation.mode.id == test_mode_data_1["id"]
    assert conversation.mode.code == test_mode_data_1["code"]
    assert len(conversation.mode.tool_sets) == len(test_mode_data_1["tool_sets"])

    assert conversation.relation is None

    mode_tool_sets = conversation.mode.tool_sets

    assert len(mode_tool_sets) == len(test_mode_data_1["tool_sets"])
    for tool_set in test_mode_data_1["tool_sets"]:
        assert tool_set["code"] in mode_tool_sets


def test_conversation_factory_create__with_relation__ok(test_mode_data_1, test_relation_data, test_raw_arguments_1):
    conversation = ConversationFactory.create(
        tenant_id="tenant_1",
        agent_provider_id=AgentVendorId("agent_vendor_1"),
        mode=test_mode_data_1,
        relation=test_relation_data,
        arguments=test_raw_arguments_1,
        title="Test Conversation",
        user_id="user_1",
    )

    assert conversation.relation.details == test_relation_data["details"]
