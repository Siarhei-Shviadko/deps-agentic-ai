import pytest


@pytest.mark.asyncio
async def test_save_conversation__saved(unit_of_work, test_conversation_1_with_completions, add_modes, add_tool_sets):
    test_conversation_1 = test_conversation_1_with_completions
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1)
        await unit_of_work.commit()

    async with unit_of_work:
        retrieved_conversation = await unit_of_work.conversations.conversation_of_id(
            test_conversation_1.id(), test_conversation_1.created_by, test_conversation_1.tenant_id()
        )
        assert retrieved_conversation is not None
        assert retrieved_conversation.id() == test_conversation_1.id()
        assert retrieved_conversation.title == test_conversation_1.title
        assert retrieved_conversation.mode.id == test_conversation_1.mode.id
        assert retrieved_conversation.mode.code == test_conversation_1.mode.code
        assert len(retrieved_conversation.mode.tool_sets) == len(test_conversation_1.mode.tool_sets)
        assert retrieved_conversation.relation is test_conversation_1.relation
        assert retrieved_conversation.context == test_conversation_1.context
        assert sorted(retrieved_conversation.completions, key=lambda completion: completion.id()) == sorted(
            test_conversation_1.completions, key=lambda completion: completion.id()
        )
        assert retrieved_conversation.created_by == test_conversation_1.created_by
        assert retrieved_conversation.created_at == test_conversation_1.created_at
        assert retrieved_conversation.updated_at == test_conversation_1.updated_at


@pytest.mark.asyncio
async def test_update_conversation__completions_updated(
    unit_of_work, test_conversation_1_with_completions, add_modes, add_tool_sets
):
    completions_number = len(test_conversation_1_with_completions.completions)

    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_1_with_completions)
        await unit_of_work.commit()

    removed_completion = test_conversation_1_with_completions.completions.pop()

    async with unit_of_work:
        await unit_of_work.conversations.update(test_conversation_1_with_completions)
        await unit_of_work.commit()

    async with unit_of_work:
        retrieved_conversation = await unit_of_work.conversations.conversation_of_id(
            test_conversation_1_with_completions.id(),
            test_conversation_1_with_completions.created_by,
            test_conversation_1_with_completions.tenant_id(),
        )

        assert len(retrieved_conversation.completions) == completions_number - 1
        assert not removed_completion in retrieved_conversation.completions


@pytest.mark.asyncio
async def test_conversations_of_ids(
    unit_of_work,
    test_conversations,
    test_conversation_1,
    test_conversation_2,
    add_agent_vendors,
    add_modes,
    add_conversations,
):
    async with unit_of_work:
        conversations = await unit_of_work.conversations.conversations_of_ids(
            ids=[test_conversation_1.id(), test_conversation_2.id()],
            user_id=test_conversation_1.created_by,
            tenant_id=test_conversation_1.tenant_id(),
        )
        await unit_of_work.commit()

    assert conversations == test_conversations


@pytest.mark.asyncio
async def test_conversations_with_mode(
    unit_of_work,
    test_conversation_1,
    add_agent_vendors,
    add_modes,
    add_conversations,
):
    async with unit_of_work:
        conversations = await unit_of_work.conversations.conversations_with_mode(test_conversation_1.mode.id)
        await unit_of_work.commit()

    assert conversations == [test_conversation_1]


@pytest.mark.asyncio
async def test_conversations_with_modes(
    unit_of_work,
    test_conversation_1,
    test_conversation_2,
    test_mode_1,
    test_mode_2,
    add_agent_vendors,
    add_modes,
    add_conversations,
):
    async with unit_of_work:
        conversations = await unit_of_work.conversations.conversations_with_modes([test_mode_1.id(), test_mode_2.id()])
        await unit_of_work.commit()

    assert conversations == [test_conversation_1, test_conversation_2]


@pytest.mark.asyncio
async def test_conversations_with_agent_vendor(
    unit_of_work,
    test_conversation_1,
    add_agent_vendors,
    add_modes,
    add_conversations,
):
    async with unit_of_work:
        conversations = await unit_of_work.conversations.conversations_with_agent_vendor(
            test_conversation_1.agent_vendor_id()
        )
        await unit_of_work.commit()

    assert conversations == [test_conversation_1]


@pytest.mark.asyncio
async def test_delete_all__deleted(
    unit_of_work,
    test_conversation_1,
    add_agent_vendors,
    add_modes,
    add_conversations,
):
    async with unit_of_work:
        await unit_of_work.conversations.delete_all([test_conversation_1])
        await unit_of_work.commit()

    async with unit_of_work:
        conversation_exists = await unit_of_work.conversations.conversation_of_id(
            id_=test_conversation_1.id(),
            user_id=test_conversation_1.created_by,
            tenant_id=test_conversation_1.tenant_id(),
        )
        await unit_of_work.commit()

        assert conversation_exists is None


async def test_save_conversation__completions_order_preserved(
    unit_of_work, test_conversation_1_with_completions, add_modes, add_tool_sets
):
    test_conversation = test_conversation_1_with_completions
    original_completion_ids = [c.id() for c in test_conversation.completions]

    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation)
        await unit_of_work.commit()

    async with unit_of_work:
        retrieved_conversation = await unit_of_work.conversations.conversation_of_id(
            test_conversation.id(), test_conversation.created_by, test_conversation.tenant_id()
        )

        assert retrieved_conversation is not None
        assert len(retrieved_conversation.completions) == len(original_completion_ids)

        retrieved_completion_ids = [c.id() for c in retrieved_conversation.completions]
        assert retrieved_completion_ids == original_completion_ids


@pytest.mark.asyncio
async def test_conversations_with_document_relation(
    unit_of_work,
    test_conversation_with_document_relation,
    add_conversations_with_relations,
    add_agent_vendors,
    add_modes,
    add_conversations,
):
    async with unit_of_work:
        conversations = await unit_of_work.conversations.conversations_with_document_relation(
            document_id=test_conversation_with_document_relation.relation.details["documentId"]
        )
        await unit_of_work.commit()

    assert conversations == [test_conversation_with_document_relation]


@pytest.mark.asyncio
async def test_conversations_with_document_type_relation(
    unit_of_work,
    test_conversation_with_document_type_relation,
    add_conversations_with_relations,
    add_agent_vendors,
    add_modes,
    add_conversations,
):
    async with unit_of_work:
        conversations = await unit_of_work.conversations.conversations_with_document_type_relation(
            document_type_id=test_conversation_with_document_type_relation.relation.details["documentTypeId"],
            tenant_id=test_conversation_with_document_type_relation.tenant_id(),
        )
        await unit_of_work.commit()

    assert conversations == [test_conversation_with_document_type_relation]
