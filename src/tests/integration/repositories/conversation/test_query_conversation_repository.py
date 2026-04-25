from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from deps_agentic_ai.domain.model.conversation import (
    ConversationFactory,
    ConversationSortField,
    ConversationSortOrder,
    RelationData,
)
from deps_agentic_ai.domain.model.shared import Pagination
from deps_agentic_ai.infrastructure.repositories.conversation.query_conversation_repository import (
    QueryConversationRepository,
)


@pytest.fixture
def create_conversation_with_document_id(tenant_id, test_agent_vendor_active, test_mode_data_1, this_user):
    def _create(document_id: str | None, title: str, created_at_offset_minutes: int = 0):
        relation = RelationData(details={"documentId": document_id}) if document_id else None
        conversation = ConversationFactory.create(
            tenant_id=tenant_id,
            agent_provider_id=test_agent_vendor_active.id,
            mode=test_mode_data_1,
            relation=relation,
            arguments={},
            title=title,
            user_id=this_user["subject"],
        )
        conversation.events.clear()
        conversation._created_at = datetime.now() + timedelta(minutes=created_at_offset_minutes)
        conversation._updated_at = conversation._created_at
        return conversation

    return _create


@pytest.mark.asyncio
async def test_completions_of_conversation_id__completions_retrieved(
    unit_of_work, add_modes, add_tool_sets, test_conversation_1_with_completions, query_conversation_repository
):
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1_with_completions)
        await unit_of_work.commit()

    retrieved_completions, _ = await query_conversation_repository.conversation_completions(
        test_conversation_1_with_completions.id()
    )

    assert len(retrieved_completions) == len(test_conversation_1_with_completions.completions)

    for completion_info, original_completion in zip(
        retrieved_completions, test_conversation_1_with_completions.completions
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


@pytest.mark.asyncio
async def test_completions_of_conversation_id__wrong_conversation_id__empty_results(
    unit_of_work, add_modes, add_tool_sets, test_conversation_1_with_completions, query_conversation_repository
):
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1_with_completions)
        await unit_of_work.commit()

    retrieved_completions, total = await query_conversation_repository.conversation_completions("fake_id")

    assert retrieved_completions == []
    assert total == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "limit,offset",
    [(2, 0), (2, 2), (100, 2)],
    ids=("first_two_completions", "second_two_completions", "all_completions_instead_of_first_two"),
)
async def test_completions_of_conversation_id__with_pagination__completions_retrieved(
    limit,
    offset,
    unit_of_work,
    add_modes,
    add_tool_sets,
    test_conversation_1_with_completions,
    query_conversation_repository,
):
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1_with_completions)
        await unit_of_work.commit()

    pagination = Pagination(limit=limit, offset=offset)

    expected_completions = test_conversation_1_with_completions.completions[offset : limit + offset]

    retrieved_completions, total = await query_conversation_repository.conversation_completions(
        test_conversation_1_with_completions.id(),
        pagination=pagination,
    )
    assert total == len(test_conversation_1_with_completions.completions)
    assert len(retrieved_completions) == len(expected_completions)

    for completion_info, original_completion in zip(retrieved_completions, expected_completions):
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


@pytest.mark.asyncio
async def test_find_all__filter_by_single_document_id__returns_only_matching(
    unit_of_work,
    add_modes,
    add_tool_sets,
    add_agent_vendors,
    query_conversation_repository,
    create_conversation_with_document_id,
    this_user,
    tenant_id,
):
    doc_id_1 = uuid4().hex
    doc_id_2 = uuid4().hex

    conv_1 = create_conversation_with_document_id(doc_id_1, "Conv 1")
    conv_2 = create_conversation_with_document_id(doc_id_1, "Conv 2")
    conv_3 = create_conversation_with_document_id(doc_id_2, "Conv 3")

    async with unit_of_work:
        await unit_of_work.conversations.save(conv_1)
        await unit_of_work.conversations.save(conv_2)
        await unit_of_work.conversations.save(conv_3)
        await unit_of_work.commit()

    grouped, total = await query_conversation_repository.find_all(
        tenant_id=tenant_id,
        created_by=this_user["subject"],
        page=1,
        size=10,
        document_ids=[doc_id_1],
    )

    assert total == 1
    assert doc_id_1 in grouped
    assert doc_id_2 not in grouped
    assert len(grouped[doc_id_1]) == 2


@pytest.mark.asyncio
async def test_find_all__filter_by_multiple_document_ids__returns_only_matching(
    unit_of_work,
    add_modes,
    add_tool_sets,
    add_agent_vendors,
    query_conversation_repository,
    create_conversation_with_document_id,
    this_user,
    tenant_id,
):
    doc_id_1 = uuid4().hex
    doc_id_2 = uuid4().hex
    doc_id_3 = uuid4().hex

    conv_1 = create_conversation_with_document_id(doc_id_1, "Conv 1")
    conv_2 = create_conversation_with_document_id(doc_id_2, "Conv 2")
    conv_3 = create_conversation_with_document_id(doc_id_3, "Conv 3")

    async with unit_of_work:
        await unit_of_work.conversations.save(conv_1)
        await unit_of_work.conversations.save(conv_2)
        await unit_of_work.conversations.save(conv_3)
        await unit_of_work.commit()

    grouped, total = await query_conversation_repository.find_all(
        tenant_id=tenant_id,
        created_by=this_user["subject"],
        page=1,
        size=10,
        document_ids=[doc_id_1, doc_id_2],
    )

    assert total == 2
    assert doc_id_1 in grouped
    assert doc_id_2 in grouped
    assert doc_id_3 not in grouped


@pytest.mark.asyncio
async def test_find_all__empty_document_ids_list__returns_all(
    unit_of_work,
    add_modes,
    add_tool_sets,
    add_agent_vendors,
    query_conversation_repository,
    create_conversation_with_document_id,
    this_user,
    tenant_id,
):
    doc_id_1 = uuid4().hex
    doc_id_2 = uuid4().hex

    conv_1 = create_conversation_with_document_id(doc_id_1, "Conv 1")
    conv_2 = create_conversation_with_document_id(doc_id_2, "Conv 2")
    conv_3 = create_conversation_with_document_id(None, "Conv 3")

    async with unit_of_work:
        await unit_of_work.conversations.save(conv_1)
        await unit_of_work.conversations.save(conv_2)
        await unit_of_work.conversations.save(conv_3)
        await unit_of_work.commit()

    grouped, total = await query_conversation_repository.find_all(
        tenant_id=tenant_id,
        created_by=this_user["subject"],
        page=1,
        size=10,
        document_ids=[],
    )

    assert total == 3
    assert doc_id_1 in grouped
    assert doc_id_2 in grouped
    assert QueryConversationRepository.NO_DOCUMENT_KEY in grouped


@pytest.mark.asyncio
async def test_find_all__none_document_ids__returns_all(
    unit_of_work,
    add_modes,
    add_tool_sets,
    add_agent_vendors,
    query_conversation_repository,
    create_conversation_with_document_id,
    this_user,
    tenant_id,
):
    doc_id_1 = uuid4().hex
    doc_id_2 = uuid4().hex

    conv_1 = create_conversation_with_document_id(doc_id_1, "Conv 1")
    conv_2 = create_conversation_with_document_id(doc_id_2, "Conv 2")

    async with unit_of_work:
        await unit_of_work.conversations.save(conv_1)
        await unit_of_work.conversations.save(conv_2)
        await unit_of_work.commit()

    grouped, total = await query_conversation_repository.find_all(
        tenant_id=tenant_id,
        created_by=this_user["subject"],
        page=1,
        size=10,
        document_ids=None,
    )

    assert total == 2
    assert doc_id_1 in grouped
    assert doc_id_2 in grouped


@pytest.mark.asyncio
async def test_find_all__pagination_by_document_id__returns_correct_page(
    unit_of_work,
    add_modes,
    add_tool_sets,
    add_agent_vendors,
    query_conversation_repository,
    create_conversation_with_document_id,
    this_user,
    tenant_id,
):
    doc_id_1 = uuid4().hex
    doc_id_2 = uuid4().hex
    doc_id_3 = uuid4().hex
    conv_1a = create_conversation_with_document_id(doc_id_1, "Conv 1a", created_at_offset_minutes=30)
    conv_1b = create_conversation_with_document_id(doc_id_1, "Conv 1b", created_at_offset_minutes=25)
    conv_2 = create_conversation_with_document_id(doc_id_2, "Conv 2", created_at_offset_minutes=20)
    conv_3 = create_conversation_with_document_id(doc_id_3, "Conv 3", created_at_offset_minutes=10)

    async with unit_of_work:
        await unit_of_work.conversations.save(conv_1a)
        await unit_of_work.conversations.save(conv_1b)
        await unit_of_work.conversations.save(conv_2)
        await unit_of_work.conversations.save(conv_3)
        await unit_of_work.commit()

    grouped_page1, total = await query_conversation_repository.find_all(
        tenant_id=tenant_id,
        created_by=this_user["subject"],
        page=1,
        size=2,
        sort_by=ConversationSortField.CREATED_AT,
        sort_order=ConversationSortOrder.DESC,
    )

    assert total == 3
    assert len(grouped_page1) == 2
    assert doc_id_1 in grouped_page1
    assert len(grouped_page1[doc_id_1]) == 2

    grouped_page2, total = await query_conversation_repository.find_all(
        tenant_id=tenant_id,
        created_by=this_user["subject"],
        page=2,
        size=2,
        sort_by=ConversationSortField.CREATED_AT,
        sort_order=ConversationSortOrder.DESC,
    )

    assert total == 3
    assert len(grouped_page2) == 1


@pytest.mark.asyncio
async def test_find_all__total_is_unique_document_id_count(
    unit_of_work,
    add_modes,
    add_tool_sets,
    add_agent_vendors,
    query_conversation_repository,
    create_conversation_with_document_id,
    this_user,
    tenant_id,
):
    doc_id_1 = uuid4().hex

    for i in range(5):
        conv = create_conversation_with_document_id(doc_id_1, f"Conv {i}")
        async with unit_of_work:
            await unit_of_work.conversations.save(conv)
            await unit_of_work.commit()

    grouped, total = await query_conversation_repository.find_all(
        tenant_id=tenant_id,
        created_by=this_user["subject"],
        page=1,
        size=10,
    )

    assert total == 1
    assert len(grouped[doc_id_1]) == 5


@pytest.mark.asyncio
async def test_find_all__sorting_determines_document_id_order(
    unit_of_work,
    add_modes,
    add_tool_sets,
    add_agent_vendors,
    query_conversation_repository,
    create_conversation_with_document_id,
    this_user,
    tenant_id,
):
    doc_id_old = uuid4().hex
    doc_id_new = uuid4().hex

    conv_old = create_conversation_with_document_id(doc_id_old, "Old Conv", created_at_offset_minutes=-10)
    conv_new = create_conversation_with_document_id(doc_id_new, "New Conv", created_at_offset_minutes=10)

    async with unit_of_work:
        await unit_of_work.conversations.save(conv_old)
        await unit_of_work.conversations.save(conv_new)
        await unit_of_work.commit()

    grouped_desc, _ = await query_conversation_repository.find_all(
        tenant_id=tenant_id,
        created_by=this_user["subject"],
        page=1,
        size=10,
        sort_by=ConversationSortField.CREATED_AT,
        sort_order=ConversationSortOrder.DESC,
    )

    keys_desc = list(grouped_desc.keys())
    assert keys_desc[0] == doc_id_new

    grouped_asc, _ = await query_conversation_repository.find_all(
        tenant_id=tenant_id,
        created_by=this_user["subject"],
        page=1,
        size=10,
        sort_by=ConversationSortField.CREATED_AT,
        sort_order=ConversationSortOrder.ASC,
    )

    keys_asc = list(grouped_asc.keys())
    assert keys_asc[0] == doc_id_old


@pytest.mark.asyncio
async def test_find_all__conversations_without_document_id__grouped_as_no_document(
    unit_of_work,
    add_modes,
    add_tool_sets,
    add_agent_vendors,
    query_conversation_repository,
    create_conversation_with_document_id,
    this_user,
    tenant_id,
):
    doc_id_1 = uuid4().hex

    conv_with_doc = create_conversation_with_document_id(doc_id_1, "With doc")
    conv_without_doc_1 = create_conversation_with_document_id(None, "Without doc 1")
    conv_without_doc_2 = create_conversation_with_document_id(None, "Without doc 2")

    async with unit_of_work:
        await unit_of_work.conversations.save(conv_with_doc)
        await unit_of_work.conversations.save(conv_without_doc_1)
        await unit_of_work.conversations.save(conv_without_doc_2)
        await unit_of_work.commit()

    grouped, total = await query_conversation_repository.find_all(
        tenant_id=tenant_id,
        created_by=this_user["subject"],
        page=1,
        size=10,
    )

    assert total == 2
    assert doc_id_1 in grouped
    assert QueryConversationRepository.NO_DOCUMENT_KEY in grouped
    assert len(grouped[QueryConversationRepository.NO_DOCUMENT_KEY]) == 2
