import random

import pytest

from deps_agentic_ai.domain.exceptions import ConversationNotFound


@pytest.mark.asyncio
async def test_get_conversation_completions__ok(
    query_conversation_service,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
    add_conversations_with_completions,
    add_other_user_conversations_with_completions,
    test_conversations_with_completions,
):
    target_conversation = random.choice(test_conversations_with_completions)

    completions, pagination_metadata = await query_conversation_service.get_conversation_completions(
        conversation_id=target_conversation.id(),
        user_id=target_conversation.created_by,
        tenant_id=target_conversation.tenant_id(),
        page=0,
        per_page=100,
    )

    assert len(completions) == len(target_conversation.completions)
    for completion_info, original_completion in zip(
        sorted(completions, key=lambda completion: completion["id"]),
        sorted(target_conversation.completions, key=lambda completion: completion.id()),
    ):
        assert completion_info["id"] == original_completion.id()
        assert completion_info["question"]["text"] == original_completion.question.text
        assert completion_info["question"]["created_at"] == original_completion.question.created_at

        assert len(completion_info["execution_context"]) == len(original_completion.execution_context)
        for execution_context_info, original_execution_context in zip(
            completion_info["execution_context"], original_completion.execution_context
        ):
            assert execution_context_info["text"] == original_execution_context.text

        if completion_info["answer"] or original_completion.answer:
            assert completion_info["answer"]["text"] == original_completion.answer.text
            assert completion_info["answer"]["created_at"] == original_completion.answer.created_at
        else:
            assert completion_info["answer"] is original_completion.answer

    assert pagination_metadata["result_set"]["count"] == len(target_conversation.completions)
    assert pagination_metadata["result_set"]["limit"] == 100
    assert pagination_metadata["result_set"]["offset"] == 0
    assert pagination_metadata["result_set"]["total"] == len(target_conversation.completions)


@pytest.mark.asyncio
async def test_get_conversation_completions__wrong_conversation_id__error(
    query_conversation_service,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
    add_conversations_with_completions,
    add_other_user_conversations_with_completions,
    test_conversations_with_completions,
):
    target_conversation = random.choice(test_conversations_with_completions)

    with pytest.raises(ConversationNotFound):
        await query_conversation_service.get_conversation_completions(
            conversation_id="fake_id",
            user_id=target_conversation.created_by,
            tenant_id=target_conversation.tenant_id(),
            page=0,
            per_page=100,
        )


@pytest.mark.asyncio
async def test_get_conversation_completions__conversation_belongs_other_user__error(
    query_conversation_service,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
    add_conversations_with_completions,
    add_other_user_conversations_with_completions,
    test_conversations_with_completions,
    test_other_user_conversations_with_completions,
):
    target_conversation = random.choice(test_conversations_with_completions)
    other_user_conversation = random.choice(test_other_user_conversations_with_completions)

    with pytest.raises(ConversationNotFound):
        await query_conversation_service.get_conversation_completions(
            conversation_id=target_conversation.id(),
            user_id=other_user_conversation.created_by,
            tenant_id=target_conversation.tenant_id(),
            page=0,
            per_page=100,
        )
