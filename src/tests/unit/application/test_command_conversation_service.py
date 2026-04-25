import random
from typing import AsyncGenerator
from unittest.mock import Mock

import pytest

from deps_agentic_ai.application import CommandConversationService
from deps_agentic_ai.domain.exceptions import (
    AgentVendorNotFound,
    ConversationNotFound,
    InactiveAgentVendor,
)
from deps_agentic_ai.domain.model.conversation import ArgumentData, ContextArguments
from deps_agentic_ai.infrastructure.proxies import (
    AgentVendorProxy,
    SSEEvent,
    SSEEventType,
)


@pytest.fixture
def mock_agent_vendor_adapter():
    return Mock(spec=AgentVendorProxy)


@pytest.fixture
def command_conversation_service_with_mock_adapter(containers, mock_agent_vendor_adapter):
    mock_agent_vendor_adapter.reset_mock()
    return CommandConversationService(
        unit_of_work=containers.unit_of_work(),
        domain_event_publisher=containers.domain_event_publisher(),
        agent_vendor_proxy=mock_agent_vendor_adapter,
    )


async def _create_sse_event_generator(events: list[SSEEvent]) -> AsyncGenerator[SSEEvent, None]:
    for event in events:
        yield event


def setup_stream_chat_mock(mock_adapter: Mock, events: list[SSEEvent]) -> None:
    def stream_chat_mock(*args, **kwargs):
        # Return a fresh async generator each time
        return _create_sse_event_generator(events)

    mock_adapter.stream_chat.side_effect = stream_chat_mock


@pytest.mark.asyncio
async def test_chat__successful_flow(
    command_conversation_service_with_mock_adapter,
    mock_agent_vendor_adapter,
    test_conversation_1,
    test_agent_vendor_active,
    unit_of_work,
    tenant_id,
    this_user,
):
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1)
        await unit_of_work.agent_vendors.save(test_agent_vendor_active)
        await unit_of_work.commit()

    sse_events = [
        SSEEvent(type=SSEEventType.REASONING, text="Thinking about the question"),
        SSEEvent(type=SSEEventType.TOOL_CALL, text="Calling tool X"),
        SSEEvent(type=SSEEventType.TOOL_CALL_RESPONSE, text="Tool response"),
        SSEEvent(type=SSEEventType.FINAL, text="Final answer"),
    ]

    setup_stream_chat_mock(mock_agent_vendor_adapter, sse_events)

    question = "Test question"
    tool_set_code = random.choice(list(test_conversation_1.mode.tool_sets.keys()))
    tool_code = random.choice(list(test_conversation_1.mode.tool_sets[tool_set_code].tools.keys()))
    parameter = random.choice(list(test_conversation_1.mode.tool_sets[tool_set_code].tools[tool_code].parameters))

    arguments = {
        tool_set_code: {
            test_conversation_1.mode.tool_sets[tool_set_code]
            .tools[tool_code]
            .code: [ArgumentData(parameter=parameter.name, value="test_value")]
        }
    }

    conversation, agent_vendor = await command_conversation_service_with_mock_adapter.validate_chat_preconditions(
        conversation_id=test_conversation_1.id(),
        user_id=this_user["subject"],
        tenant_id=tenant_id,
    )

    yielded_events = []
    async for event in command_conversation_service_with_mock_adapter.chat(
        conversation=conversation,
        agent_vendor=agent_vendor,
        user_question=question,
        arguments=arguments,
    ):
        yielded_events.append(event)

    assert len(yielded_events) == len(sse_events)
    for i, event in enumerate(yielded_events):
        assert event.type == sse_events[i].type
        assert event.text == sse_events[i].text

    async with unit_of_work:
        saved_conversation = await unit_of_work.conversations.conversation_of_id(
            id_=test_conversation_1.id(), user_id=this_user["subject"], tenant_id=tenant_id
        )

    assert saved_conversation is not None
    assert len(saved_conversation.completions) == 1
    completion = saved_conversation.completions[0]
    assert completion.question.text == question
    assert len(completion.execution_context) == 3
    assert completion.answer is not None
    assert completion.answer.text == "Final answer"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_type,event_text,expect_execution_context,expect_answer",
    [
        (SSEEventType.TOOL_CALL, "Tool call text", True, False),
        (SSEEventType.REASONING, "Reasoning text", True, False),
        (SSEEventType.TOOL_CALL_RESPONSE, "Tool response text", True, False),
        (SSEEventType.FINAL, "Final answer text", False, True),
    ],
)
async def test_chat__single_event_updates_completion(
    command_conversation_service_with_mock_adapter,
    mock_agent_vendor_adapter,
    test_conversation_1,
    test_agent_vendor_active,
    unit_of_work,
    tenant_id,
    this_user,
    event_type,
    event_text,
    expect_execution_context,
    expect_answer,
):
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1)
        await unit_of_work.agent_vendors.save(test_agent_vendor_active)
        await unit_of_work.commit()

    sse_events = [SSEEvent(type=event_type, text=event_text)]

    setup_stream_chat_mock(mock_agent_vendor_adapter, sse_events)

    conversation, agent_vendor = await command_conversation_service_with_mock_adapter.validate_chat_preconditions(
        conversation_id=test_conversation_1.id(),
        user_id=this_user["subject"],
        tenant_id=tenant_id,
    )

    async for _ in command_conversation_service_with_mock_adapter.chat(
        conversation=conversation,
        agent_vendor=agent_vendor,
        user_question="Test",
        arguments={},
    ):
        pass

    async with unit_of_work:
        saved_conversation = await unit_of_work.conversations.conversation_of_id(
            id_=test_conversation_1.id(), user_id=this_user["subject"], tenant_id=tenant_id
        )

    assert saved_conversation is not None
    assert len(saved_conversation.completions) == 1
    completion = saved_conversation.completions[0]

    if expect_execution_context:
        assert len(completion.execution_context) == 1
        assert completion.execution_context[0].text == event_text
        assert completion.answer is None

    if expect_answer:
        assert completion.answer is not None
        assert completion.answer.text == event_text


@pytest.mark.asyncio
async def test_chat__conversation_saved_after_each_event(
    command_conversation_service_with_mock_adapter,
    mock_agent_vendor_adapter,
    test_conversation_1,
    test_agent_vendor_active,
    unit_of_work,
    tenant_id,
    this_user,
):
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1)
        await unit_of_work.agent_vendors.save(test_agent_vendor_active)
        await unit_of_work.commit()

    sse_events = [
        SSEEvent(type=SSEEventType.REASONING, text="Event 1"),
        SSEEvent(type=SSEEventType.TOOL_CALL, text="Event 2"),
    ]

    setup_stream_chat_mock(mock_agent_vendor_adapter, sse_events)

    conversation, agent_vendor = await command_conversation_service_with_mock_adapter.validate_chat_preconditions(
        conversation_id=test_conversation_1.id(),
        user_id=this_user["subject"],
        tenant_id=tenant_id,
    )

    event_count = 0
    async for _ in command_conversation_service_with_mock_adapter.chat(
        conversation=conversation,
        agent_vendor=agent_vendor,
        user_question="Test",
        arguments={},
    ):
        event_count += 1

        async with unit_of_work:
            saved_conversation = await unit_of_work.conversations.conversation_of_id(
                id_=test_conversation_1.id(), user_id=this_user["subject"], tenant_id=tenant_id
            )

        assert saved_conversation is not None
        assert len(saved_conversation.completions) == 1
        completion = saved_conversation.completions[0]
        assert len(completion.execution_context) == event_count

    assert event_count == len(sse_events)


@pytest.mark.asyncio
async def test_chat__conversation_saved_in_finally_block(
    command_conversation_service_with_mock_adapter,
    mock_agent_vendor_adapter,
    test_conversation_1,
    test_agent_vendor_active,
    unit_of_work,
    tenant_id,
    this_user,
):
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1)
        await unit_of_work.agent_vendors.save(test_agent_vendor_active)
        await unit_of_work.commit()

    async def event_generator_with_error():
        yield SSEEvent(type=SSEEventType.REASONING, text="Event before error")
        raise Exception("Streaming error")

    def stream_chat_mock(*args, **kwargs):
        return event_generator_with_error()

    mock_agent_vendor_adapter.stream_chat = stream_chat_mock

    conversation, agent_vendor = await command_conversation_service_with_mock_adapter.validate_chat_preconditions(
        conversation_id=test_conversation_1.id(),
        user_id=this_user["subject"],
        tenant_id=tenant_id,
    )

    with pytest.raises(Exception, match="Streaming error"):
        async for _ in command_conversation_service_with_mock_adapter.chat(
            conversation=conversation,
            agent_vendor=agent_vendor,
            user_question="Test",
            arguments={},
        ):
            pass

    async with unit_of_work:
        saved_conversation = await unit_of_work.conversations.conversation_of_id(
            id_=test_conversation_1.id(), user_id=this_user["subject"], tenant_id=tenant_id
        )

    assert saved_conversation is not None
    assert len(saved_conversation.completions) == 1
    completion = saved_conversation.completions[0]
    assert len(completion.execution_context) == 1
    assert completion.execution_context[0].text == "Event before error"


@pytest.mark.asyncio
async def test_chat__conversation_not_found(
    command_conversation_service_with_mock_adapter,
    unit_of_work,
    tenant_id,
    this_user,
):
    with pytest.raises(ConversationNotFound):
        await command_conversation_service_with_mock_adapter.validate_chat_preconditions(
            conversation_id="non_existent_id",
            user_id=this_user["subject"],
            tenant_id=tenant_id,
        )


@pytest.mark.asyncio
async def test_chat__agent_vendor_not_found(
    command_conversation_service_with_mock_adapter,
    test_conversation_1,
    unit_of_work,
    tenant_id,
    this_user,
):
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1)
        await unit_of_work.commit()

    with pytest.raises(AgentVendorNotFound):
        await command_conversation_service_with_mock_adapter.validate_chat_preconditions(
            conversation_id=test_conversation_1.id(),
            user_id=this_user["subject"],
            tenant_id=tenant_id,
        )


@pytest.mark.asyncio
async def test_chat__agent_vendor_inactive__error(
    command_conversation_service_with_mock_adapter,
    mock_agent_vendor_adapter,
    test_conversation_with_inactive_agent_vendor,
    test_inactive_agent_vendor,
    unit_of_work,
    tenant_id,
    this_user,
):
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_with_inactive_agent_vendor)
        await unit_of_work.agent_vendors.save(test_inactive_agent_vendor)
        await unit_of_work.commit()

    with pytest.raises(InactiveAgentVendor):
        await command_conversation_service_with_mock_adapter.validate_chat_preconditions(
            conversation_id=test_conversation_with_inactive_agent_vendor.id(),
            user_id=this_user["subject"],
            tenant_id=tenant_id,
        )


@pytest.mark.asyncio
async def test_edit_question__ok(
    command_conversation_service_with_mock_adapter,
    mock_agent_vendor_adapter,
    test_conversation_1_with_completed_completions,
    test_agent_vendor_active,
    unit_of_work,
    tenant_id,
    this_user,
):
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1_with_completed_completions)
        await unit_of_work.agent_vendors.save(test_agent_vendor_active)
        await unit_of_work.commit()

    sse_events = [
        SSEEvent(type=SSEEventType.REASONING, text="Thinking about the question"),
        SSEEvent(type=SSEEventType.TOOL_CALL, text="Calling tool X"),
        SSEEvent(type=SSEEventType.TOOL_CALL_RESPONSE, text="Tool response"),
        SSEEvent(type=SSEEventType.FINAL, text="Final answer"),
    ]

    setup_stream_chat_mock(mock_agent_vendor_adapter, sse_events)

    edited_question = "New question"
    completions_number = len(test_conversation_1_with_completed_completions.completions)
    tool_set_code = random.choice(list(test_conversation_1_with_completed_completions.mode.tool_sets.keys()))
    tool_code = random.choice(
        list(test_conversation_1_with_completed_completions.mode.tool_sets[tool_set_code].tools.keys())
    )
    parameter = random.choice(
        list(test_conversation_1_with_completed_completions.mode.tool_sets[tool_set_code].tools[tool_code].parameters)
    )

    arguments = {
        tool_set_code: {
            test_conversation_1_with_completed_completions.mode.tool_sets[tool_set_code]
            .tools[tool_code]
            .code: [ArgumentData(parameter=parameter.name, value="test_value")]
        }
    }

    conversation, agent_vendor = await command_conversation_service_with_mock_adapter.validate_chat_preconditions(
        conversation_id=test_conversation_1_with_completed_completions.id(),
        user_id=this_user["subject"],
        tenant_id=tenant_id,
    )

    yielded_events = []
    async for event in command_conversation_service_with_mock_adapter.edit_question(
        conversation=conversation,
        agent_vendor=agent_vendor,
        completion_id=test_conversation_1_with_completed_completions.completions[-3].id(),
        user_question=edited_question,
        arguments=arguments,
    ):
        yielded_events.append(event)

    assert len(yielded_events) == len(sse_events)
    for i, event in enumerate(yielded_events):
        assert event.type == sse_events[i].type
        assert event.text == sse_events[i].text

    async with unit_of_work:
        saved_conversation = await unit_of_work.conversations.conversation_of_id(
            id_=test_conversation_1_with_completed_completions.id(), user_id=this_user["subject"], tenant_id=tenant_id
        )

    assert saved_conversation is not None
    assert len(saved_conversation.completions) == completions_number - 2

    edited_completion = saved_conversation.completions[-1]
    assert edited_completion.question.text == edited_question
    assert edited_completion.answer is not None
    assert edited_completion.answer.text == "Final answer"
