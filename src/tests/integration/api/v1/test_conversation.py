import random
from http import HTTPStatus
from typing import AsyncGenerator
from unittest.mock import Mock
from uuid import uuid4

import pytest

from deps_agentic_ai.api.constants import PAGINATION_DEFAULT_PER_PAGE
from deps_agentic_ai.constants import V1_API_PREFIX
from deps_agentic_ai.domain.exceptions import AgentVendorNotFound, ModeNotFound
from deps_agentic_ai.infrastructure.proxies import (
    AgentVendorProxy,
    SSEEvent,
    SSEEventType,
)


@pytest.fixture
def mock_agent_vendor_proxy(containers):
    mock_adapter = Mock(spec=AgentVendorProxy)
    if hasattr(containers, "command_conversation_service"):
        containers.command_conversation_service.reset()

    containers.agent_vendor_proxy.override(mock_adapter)

    yield mock_adapter

    containers.agent_vendor_proxy.reset_override()
    if hasattr(containers, "command_conversation_service"):
        containers.command_conversation_service.reset()


async def _create_sse_event_generator(events: list[SSEEvent]) -> AsyncGenerator[SSEEvent, None]:
    for event in events:
        yield event


def setup_stream_chat_mock(mock_adapter: Mock, events: list[SSEEvent]) -> None:
    def stream_chat_mock(*args, **kwargs):
        return _create_sse_event_generator(events)

    mock_adapter.stream_chat.side_effect = stream_chat_mock


def _count_conversations_in_grouped_response(items: dict) -> int:
    return sum(len(convs) for convs in items.values())


@pytest.mark.asyncio
async def test_create_conversation__201(
    client,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
    test_agent_vendors,
    test_modes,
):
    source_mode = random.choice(test_modes)
    payload = {
        "agentVendorId": random.choice(test_agent_vendors).id(),
        "modeId": source_mode.id(),
        "relation": {"test": "test"},
        "title": "test_title",
        "arguments": {
            tool_set["code"]: {
                tool["code"]: [{"parameter": param["name"], "value": "test"} for param in tool["parameters"]]
                for tool in tool_set["tools"]
            }
            for tool_set in source_mode.to_data()["tool_sets"]
        },
    }

    response = await client.post(f"{V1_API_PREFIX}/conversations", json=payload)

    assert response.status_code == 201
    assert response.json()["id"] is not None


@pytest.mark.asyncio
async def test_create_conversation__no_agent_vendor__404(
    client,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
    test_agent_vendors,
    test_modes,
):
    source_mode = random.choice(test_modes)
    payload = {
        "agentVendorId": "fake_agent_vendor_id",
        "modeId": source_mode.id(),
        "relation": {"test": "test"},
        "title": "test_title",
        "arguments": {
            tool_set["code"]: {
                tool["code"]: [{"parameter": param["name"], "value": "test"} for param in tool["parameters"]]
                for tool in tool_set["tools"]
            }
            for tool_set in source_mode.to_data()["tool_sets"]
        },
    }

    response = await client.post(f"{V1_API_PREFIX}/conversations", json=payload)

    assert response.json()["code"] == AgentVendorNotFound.code


@pytest.mark.asyncio
async def test_create_conversation__no_mode__404(
    client,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
    test_agent_vendors,
    test_modes,
):
    source_mode = random.choice(test_modes)
    payload = {
        "agentVendorId": random.choice(test_agent_vendors).id(),
        "modeId": "fake_mode_id",
        "relation": {"test": "test"},
        "title": "test_title",
        "arguments": {
            tool_set["code"]: {
                tool["code"]: [{"parameter": param["name"], "value": "test"} for param in tool["parameters"]]
                for tool in tool_set["tools"]
            }
            for tool_set in source_mode.to_data()["tool_sets"]
        },
    }

    response = await client.post(f"{V1_API_PREFIX}/conversations", json=payload)

    assert response.json()["code"] == ModeNotFound.code


@pytest.mark.asyncio
async def test_create_conversation__invalid_tool_set__400(
    client,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
    test_agent_vendors,
    test_modes,
    test_relation_data,
):
    source_mode = random.choice(test_modes)
    fake_tool_set_code = uuid4().hex

    payload = {
        "agentVendorId": random.choice(test_agent_vendors).id(),
        "modeId": source_mode.id(),
        "relation": {"test": "test"},
        "title": "test_title",
        "arguments": {
            fake_tool_set_code: {
                tool["code"]: [{"parameter": param["name"], "value": "test"} for param in tool["parameters"]]
                for tool in tool_set["tools"]
            }
            for tool_set in source_mode.to_data()["tool_sets"]
        },
    }

    response = await client.post(f"{V1_API_PREFIX}/conversations", json=payload)

    assert response.status_code == 400
    assert f"Tool set {fake_tool_set_code} not found in mode {source_mode.code}" == response.json()["message"]


@pytest.mark.asyncio
async def test_create_conversation__invalid_tool__400(
    client,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
    test_agent_vendors,
    test_modes,
    test_relation_data,
):
    source_mode = random.choice(test_modes)
    fake_tool_code = uuid4().hex
    expected_tool_set_code = source_mode.to_data()["tool_sets"][0]["code"]

    payload = {
        "agentVendorId": random.choice(test_agent_vendors).id(),
        "modeId": source_mode.id(),
        "relation": {"test": "test"},
        "title": "test_title",
        "arguments": {
            tool_set["code"]: {
                fake_tool_code: [{"parameter": param["name"], "value": "test"} for param in tool["parameters"]]
                for tool in tool_set["tools"][:1]
            }
            for tool_set in source_mode.to_data()["tool_sets"][:1]
        },
    }

    response = await client.post(f"{V1_API_PREFIX}/conversations", json=payload)

    assert response.status_code == 400
    assert f"Tool {fake_tool_code} not found in tool set {expected_tool_set_code}" == response.json()["message"]


@pytest.mark.asyncio
async def test_create_conversation__invalid_parameter__400(
    client,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
    test_agent_vendors,
    test_modes,
    test_relation_data,
):
    source_mode = random.choice(test_modes)
    fake_param = uuid4().hex
    expected_tool_code = source_mode.to_data()["tool_sets"][0]["tools"][0]["code"]

    payload = {
        "agentVendorId": random.choice(test_agent_vendors).id(),
        "modeId": source_mode.id(),
        "relation": {"test": "test"},
        "title": "test_title",
        "arguments": {
            tool_set["code"]: {
                tool["code"]: [{"parameter": fake_param, "value": "test"} for param in tool["parameters"][:1]]
                for tool in tool_set["tools"][:1]
            }
            for tool_set in source_mode.to_data()["tool_sets"][:1]
        },
    }

    response = await client.post(f"{V1_API_PREFIX}/conversations", json=payload)

    assert response.status_code == 400
    assert f"Parameter {fake_param} not found in tool {expected_tool_code}" == response.json()["message"]


@pytest.mark.asyncio
async def test_get_conversation__ok(
    client, unit_of_work, test_conversation_1_with_completions, add_modes, add_tool_sets
):
    test_conversation_1 = test_conversation_1_with_completions
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1)
        await unit_of_work.commit()

    response = await client.get(f"{V1_API_PREFIX}/conversations/{test_conversation_1.id()}")
    assert response.status_code == HTTPStatus.OK
    json_response = response.json()

    assert json_response["id"] == test_conversation_1.id()
    assert json_response["title"] == test_conversation_1.title
    assert "relation" in json_response
    assert json_response["relation"]["details"] is None

    completions = json_response["completions"]
    assert len(completions) == len(test_conversation_1_with_completions.completions)

    for completion, original_completion in zip(
        sorted(completions, key=lambda completion: completion["question"]["createdAt"]),
        sorted(test_conversation_1_with_completions.completions, key=lambda completion: completion.question.created_at),
    ):
        assert completion["question"]["text"] == original_completion.question.text
        assert "createdAt" in completion["question"]

        if completion["answer"] or original_completion.answer:
            assert completion["answer"]["text"] == original_completion.answer.text
            assert "createdAt" in completion["answer"]
        for execution_context, original_execution_context in zip(
            completion["executionContext"], original_completion.execution_context
        ):
            assert execution_context["text"] == original_execution_context.text


@pytest.mark.asyncio
async def test_get_conversation__wrong_conversation_id__error(
    client, unit_of_work, add_conversations, add_modes, add_tool_sets
):
    response = await client.get(f"{V1_API_PREFIX}/conversations/fake_id")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_get_conversation__belongs_to_another_user__404(
    client,
    unit_of_work,
    test_conversation_1,
    test_conversation_2,
    add_modes,
    add_tool_sets,
    test_other_user_conversations_with_completions,
):
    other_user_conversation = random.choice(test_other_user_conversations_with_completions)
    for test_conversation in [
        test_conversation_1,
        test_conversation_2,
        *test_other_user_conversations_with_completions,
    ]:
        async with unit_of_work:
            await unit_of_work.conversations.save(test_conversation)
            await unit_of_work.commit()

    response = await client.get(f"{V1_API_PREFIX}/conversations/{other_user_conversation.id()}")
    assert response.status_code == HTTPStatus.NOT_FOUND


async def test_get_completions__200(
    client,
    add_conversations_with_completions,
    test_conversations_with_completions,
    add_modes,
    add_tool_sets,
):
    target_conversation = max(
        test_conversations_with_completions, key=lambda conversation: len(conversation.completions)
    )
    response = await client.get(f"{V1_API_PREFIX}/conversations/{target_conversation.id()}/completions")
    assert response.status_code == 200

    response_json = response.json()
    assert len(response_json["completions"]) == len(target_conversation.completions)
    assert response_json["metadata"]["total"] == len(target_conversation.completions)
    assert (
        response_json["metadata"]["size"] == len(target_conversation.completions)
        if len(target_conversation.completions) <= PAGINATION_DEFAULT_PER_PAGE
        else PAGINATION_DEFAULT_PER_PAGE
    )


@pytest.mark.asyncio
async def test_get_completions__with_pagination__200(
    client,
    add_conversations_with_completions,
    test_conversations_with_completions,
    add_modes,
    add_tool_sets,
):
    target_conversation = max(
        test_conversations_with_completions, key=lambda conversation: len(conversation.completions)
    )
    page = 2
    per_page = 1

    response = await client.get(
        f"{V1_API_PREFIX}/conversations/{target_conversation.id()}/completions?page={page}&perPage={per_page}"
    )
    assert response.status_code == 200

    response_json = response.json()
    assert len(response_json["completions"]) == per_page
    assert response_json["metadata"]["total"] == len(target_conversation.completions)
    assert response_json["metadata"]["size"] == per_page


@pytest.mark.asyncio
async def test_get_completions__wrong_conversation_id__404(
    client,
    add_conversations_with_completions,
    test_conversations_with_completions,
    add_modes,
    add_tool_sets,
):
    response = await client.get(f"{V1_API_PREFIX}/conversations/fake_id/completions")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_completions__conversation_belongs_to_other_user__404(
    client,
    add_conversations_with_completions,
    add_other_user_conversations_with_completions,
    test_conversations_with_completions,
    test_other_user_conversations_with_completions,
    add_modes,
    add_tool_sets,
):
    target_conversation = random.choice(test_other_user_conversations_with_completions)
    response = await client.get(f"{V1_API_PREFIX}/conversations/{target_conversation.id()}/completions")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_conversation__200(
    client,
    unit_of_work,
    test_conversation_1,
    add_modes,
    add_tool_sets,
):
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1)
        await unit_of_work.commit()

    new_title = "Updated Title"
    payload = {"title": new_title}

    response = await client.patch(f"{V1_API_PREFIX}/conversations/{test_conversation_1.id()}", json=payload)

    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == test_conversation_1.id()

    async with unit_of_work:
        updated_conversation = await unit_of_work.conversations.conversation_of_id(
            id_=test_conversation_1.id(),
            user_id=test_conversation_1.created_by,
            tenant_id=test_conversation_1.tenant_id(),
        )
        assert updated_conversation.title == new_title


@pytest.mark.asyncio
async def test_update_conversation__wrong_conversation_id__404(
    client,
    add_modes,
    add_tool_sets,
):
    payload = {"title": "New Title"}
    response = await client.patch(f"{V1_API_PREFIX}/conversations/fake_id", json=payload)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_update_conversation__belongs_to_another_user__404(
    client,
    unit_of_work,
    add_modes,
    add_tool_sets,
    test_other_user_conversations_with_completions,
):
    other_user_conversation = random.choice(test_other_user_conversations_with_completions)
    async with unit_of_work:
        await unit_of_work.conversations.save(other_user_conversation)
        await unit_of_work.commit()

    payload = {"title": "New Title"}
    response = await client.patch(f"{V1_API_PREFIX}/conversations/{other_user_conversation.id()}", json=payload)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query_params, expected_count, expected_total, with_mode, description",
    [
        ({"page": 1, "size": 10}, 2, 2, False, "basic listing"),
        ({"page": 1, "size": 1}, 1, 2, False, "pagination page 1 size 1"),
        ({"page": 2, "size": 1}, 1, 2, False, "pagination page 2 size 1"),
        ({"page": 1, "size": 10}, 1, 1, True, "filter by mode"),
    ],
)
async def test_get_conversations__various_cases(
    client,
    unit_of_work,
    test_conversation_1_with_completions,
    test_conversation_2,
    add_modes,
    add_tool_sets,
    query_params,
    expected_count,
    expected_total,
    with_mode,
    description,
):
    for test_conversation in [test_conversation_1_with_completions, test_conversation_2]:
        async with unit_of_work:
            await unit_of_work.conversations.save(test_conversation)
            await unit_of_work.commit()

    if with_mode:
        query_params = {
            **query_params,
            "mode": test_conversation_1_with_completions.mode.code,
        }

    response = await client.get(f"{V1_API_PREFIX}/conversations", query_string=query_params)
    assert response.status_code == HTTPStatus.OK, f"failed on case: {description}"

    json_response = response.json()
    assert "items" in json_response
    assert "total" in json_response
    assert isinstance(json_response["items"], dict)

    total_conversations = _count_conversations_in_grouped_response(json_response["items"])
    assert total_conversations == expected_count, f"unexpected item count for {description}"
    assert json_response["total"] == expected_total, f"unexpected total for {description}"

    if with_mode:
        for doc_id, convs in json_response["items"].items():
            for conv in convs:
                assert conv["mode"]["code"] == test_conversation_1_with_completions.mode.code


@pytest.mark.asyncio
async def test_get_conversations__grouped_by_document_id__200(
    client,
    unit_of_work,
    test_conversation_1_with_completions,
    test_conversation_2,
    add_modes,
    add_tool_sets,
):
    for test_conversation in [test_conversation_1_with_completions, test_conversation_2]:
        async with unit_of_work:
            await unit_of_work.conversations.save(test_conversation)
            await unit_of_work.commit()

    response = await client.get(f"{V1_API_PREFIX}/conversations", query_string={"page": 1, "size": 10})
    assert response.status_code == HTTPStatus.OK

    json_response = response.json()
    assert json_response["total"] == 2

    total_conversations = _count_conversations_in_grouped_response(json_response["items"])
    assert total_conversations == 2

    assert "_no_document" in json_response["items"]
    assert len(json_response["items"]["_no_document"]) == 1

    non_empty_groups = [k for k in json_response["items"].keys() if k != "_no_document"]
    assert len(non_empty_groups) == 1
    assert len(json_response["items"][non_empty_groups[0]]) == 1


@pytest.mark.asyncio
async def test_get_conversations__filter_by_title__200(
    client,
    unit_of_work,
    test_conversation_1_with_completions,
    test_conversation_2,
    add_modes,
    add_tool_sets,
):
    for test_conversation in [test_conversation_1_with_completions, test_conversation_2]:
        async with unit_of_work:
            await unit_of_work.conversations.save(test_conversation)
            await unit_of_work.commit()

    response = await client.get(
        f"{V1_API_PREFIX}/conversations",
        query_string={"page": 1, "size": 10, "title": "Conversation 1"},
    )
    assert response.status_code == HTTPStatus.OK

    json_response = response.json()
    assert json_response["total"] == 1

    for doc_id, convs in json_response["items"].items():
        for conv in convs:
            assert "Conversation 1" in conv["title"]


@pytest.mark.asyncio
async def test_get_conversations__empty__200(
    client,
    add_modes,
    add_tool_sets,
):
    response = await client.get(f"{V1_API_PREFIX}/conversations", query_string={"page": 1, "size": 10})
    assert response.status_code == HTTPStatus.OK

    json_response = response.json()
    assert json_response["items"] == {}
    assert json_response["total"] == 0


@pytest.mark.asyncio
async def test_delete_conversations__204(
    client,
    test_conversation_1,
    test_conversation_2,
    add_agent_vendors,
    add_modes,
    add_conversations,
):
    response = await client.delete(
        f"{V1_API_PREFIX}/conversations?id={test_conversation_1.id()}&id={test_conversation_2.id()}"
    )

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_conversations__does_not_exist__204(
    client,
    test_conversation_1,
):
    response = await client.delete(f"{V1_API_PREFIX}/conversations?id={test_conversation_1.id()}")

    assert response.status_code == HTTPStatus.NO_CONTENT


async def test_chat_api__successful_flow(
    client,
    unit_of_work,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
    test_conversation_1,
    test_agent_vendor_active,
    mock_agent_vendor_proxy,
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

    setup_stream_chat_mock(mock_agent_vendor_proxy, sse_events)

    question = "Test question"

    response = await client.get(
        f"{V1_API_PREFIX}/conversations/{test_conversation_1.id()}/chat",
        query_string={"userQuestion": question},
    )

    assert response.status_code == HTTPStatus.OK
    resp = response.content  # Consume SSE stream to trigger event processing

    async with unit_of_work:
        saved_conversation = await unit_of_work.conversations.conversation_of_id(
            id_=test_conversation_1.id(), user_id=this_user["subject"], tenant_id=tenant_id
        )
        await unit_of_work.commit()

    assert saved_conversation is not None
    assert len(saved_conversation.completions) == 1

    completion = saved_conversation.completions[0]
    assert completion.question.text == question
    assert len(completion.execution_context) == 3
    assert completion.answer is not None
    assert completion.answer.text == "Final answer"


@pytest.mark.asyncio
async def test_chat_api__conversation_not_found__404(
    client,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
):
    response = await client.get(
        f"{V1_API_PREFIX}/conversations/non_existent_id/chat",
        query_string={"userQuestion": "Test"},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_chat_api__includes_context_bundle_in_request(
    client,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
    test_conversation_1_with_completed_completions,
    test_agent_vendor_active,
    mock_agent_vendor_proxy,
    unit_of_work,
):
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1_with_completed_completions)
        await unit_of_work.agent_vendors.save(test_agent_vendor_active)
        await unit_of_work.commit()

    sse_events = [
        SSEEvent(type=SSEEventType.FINAL, text="Final answer"),
    ]

    setup_stream_chat_mock(mock_agent_vendor_proxy, sse_events)

    question = "New question"

    response = await client.get(
        f"{V1_API_PREFIX}/conversations/{test_conversation_1_with_completed_completions.id()}/chat",
        query_string={"userQuestion": question},
    )

    assert response.status_code == HTTPStatus.OK
    resp = response.content  # Consume SSE stream

    assert mock_agent_vendor_proxy.stream_chat.called

    call_args = mock_agent_vendor_proxy.stream_chat.call_args
    agent_request = call_args[0][0]

    assert "conversationTrim" in agent_request.context_bundle

    assert len(agent_request.context_bundle["conversationTrim"]) > 0


async def test_edit_question__ok(
    client,
    unit_of_work,
    add_tool_sets,
    add_agent_vendors,
    add_modes,
    test_conversation_1_with_completed_completions,
    test_agent_vendor_active,
    mock_agent_vendor_proxy,
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

    setup_stream_chat_mock(mock_agent_vendor_proxy, sse_events)

    edited_question = "New question"
    completions = test_conversation_1_with_completed_completions.completions
    complition_to_edit_question = completions[-3]

    response = await client.patch(
        f"{V1_API_PREFIX}/conversations/{test_conversation_1_with_completed_completions.id()}/completions/{complition_to_edit_question.id()}",
        query_string={"userQuestion": edited_question, "arguments": {}},
    )

    assert response.status_code == HTTPStatus.OK
    resp = response.content  # Consume SSE stream to trigger event processing

    async with unit_of_work:
        saved_conversation = await unit_of_work.conversations.conversation_of_id(
            id_=test_conversation_1_with_completed_completions.id(), user_id=this_user["subject"], tenant_id=tenant_id
        )

    assert saved_conversation is not None
    assert len(saved_conversation.completions) == len(completions) - 2

    edited_completion = saved_conversation.completions[-1]
    assert edited_completion.question.text == edited_question
    assert edited_completion.answer is not None
    assert edited_completion.answer.text == "Final answer"
