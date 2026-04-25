import asyncio
from datetime import datetime
from random import choice, randint
from unittest.mock import Mock
from uuid import uuid4

import pytest
import pytest_asyncio
from async_asgi_testclient import TestClient
from fastapi import FastAPI

from deps_agentic_ai import api
from deps_agentic_ai.application import (
    CommandAgentVendorService,
    CommandConversationService,
    QueryAgentVendorService,
)
from deps_agentic_ai.domain.model.agent_vendor import AgentVendor, AgentVendorFactory
from deps_agentic_ai.domain.model.conversation import (
    Answer,
    ArgumentData,
    Completion,
    Conversation,
    ConversationFactory,
    ExecutionContext,
    Question,
    RelationData,
)
from deps_agentic_ai.domain.model.mode import Mode, ModeData, ModeFactory
from deps_agentic_ai.domain.model.shared import ToolCode, ToolSetCode
from deps_agentic_ai.domain.model.tool_set import (
    ParameterData,
    ToolData,
    ToolSet,
    ToolSetFactory,
)
from deps_agentic_ai.entrypoint import create_fastapi
from deps_agentic_ai.infrastructure.access_management import user


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    yield loop

    loop.close()


@pytest.fixture(scope="session")
def app() -> FastAPI:
    fastapi_app = create_fastapi()
    yield fastapi_app


@pytest_asyncio.fixture
async def client(app):
    async with TestClient(app) as client:
        yield client


@pytest.fixture
def tenant_id():
    return uuid4().hex


@pytest.fixture
def this_user(tenant_id):
    return dict(
        subject="Test",
        groups=[tenant_id],
        token="token",
        roles=[],
        organisation=tenant_id,
    )


@pytest.fixture(autouse=True)
def set_this_user(this_user):
    user.set(this_user)


@pytest.fixture(autouse=True)
def mocked_middleware(monkeypatch, mocker):
    monkeypatch.setattr(api.auth, "set_user_from_token", mocker.Mock({}))


@pytest.fixture(scope="session")
def containers(app):
    return app.containers


@pytest.fixture(autouse=True, scope="session")
def domain_event_publisher_session_mock(containers):
    mock = Mock(containers.domain_event_publisher())
    containers.domain_event_publisher.override(mock)

    yield mock

    containers.domain_event_publisher.reset_override()


@pytest.fixture(autouse=True)
def domain_event_publisher_mock(domain_event_publisher_session_mock):
    domain_event_publisher_session_mock.reset_mock()

    yield domain_event_publisher_session_mock


@pytest.fixture
def repositories(containers):
    return containers.repositories


@pytest.fixture
def query_tool_set_service(containers):
    return containers.query_tool_set_service()


@pytest.fixture
def command_tool_set_service(containers):
    return containers.command_tool_set_service()


@pytest.fixture
def query_mode_service(containers):
    return containers.query_mode_service()


@pytest.fixture
def command_mode_service(containers):
    return containers.command_mode_service()


@pytest.fixture
def command_agent_vendor_service(containers) -> CommandAgentVendorService:
    return containers.command_agent_vendor_service()


@pytest.fixture
def query_agent_vendor_service(containers) -> QueryAgentVendorService:
    return containers.query_agent_vendor_service()


@pytest.fixture
def command_conversation_service(containers) -> CommandConversationService:
    return containers.command_conversation_service()


@pytest.fixture
def query_conversation_service(containers):
    return containers.query_conversation_service()


@pytest.fixture
def test_tool_set_1_code() -> str:
    return "ts_1_code"


@pytest.fixture
def test_tool_set_1(test_tool_set_1_code) -> ToolSet:
    tool_set = ToolSetFactory.create(
        code=test_tool_set_1_code,
        name="TS1",
        tools=[
            ToolData(
                code="t1",
                name="T1",
                parameters=[
                    ParameterData(name="p11"),
                    ParameterData(name="p12"),
                ],
            ),
            ToolData(
                code="t2",
                name="T2",
                parameters=[
                    ParameterData(name="p21"),
                    ParameterData(name="p22"),
                ],
            ),
        ],
    )
    tool_set.events.clear()

    return tool_set


@pytest.fixture
def test_tool_set_2_code() -> str:
    return "ts_2_code"


@pytest.fixture
def test_tool_set_2(test_tool_set_2_code) -> ToolSet:
    tool_set = ToolSetFactory.create(
        code=test_tool_set_2_code,
        name="TS2",
        tools=[
            ToolData(
                code="t3",
                name="T3",
                parameters=[
                    ParameterData(name="p31"),
                    ParameterData(name="p32"),
                ],
            ),
            ToolData(
                code="t4",
                name="T4",
                parameters=[
                    ParameterData(name="p41"),
                    ParameterData(name="p42"),
                ],
            ),
        ],
    )
    tool_set.events.clear()

    return tool_set


@pytest.fixture
def test_tool_set_3_code() -> str:
    return "ts_3_code"


@pytest.fixture
def test_tool_set_3(test_tool_set_3_code) -> ToolSet:
    tool_set = ToolSetFactory.create(
        code=test_tool_set_3_code,
        name="TS3",
        tools=[
            ToolData(
                code="t3",
                name="T3",
                parameters=[
                    ParameterData(name="p31"),
                    ParameterData(name="p32"),
                ],
            ),
            ToolData(
                code="t4",
                name="T4",
                parameters=[
                    ParameterData(name="p41"),
                    ParameterData(name="p42"),
                ],
            ),
        ],
    )
    tool_set.events.clear()

    return tool_set


@pytest.fixture
def test_tool_sets(test_tool_set_1, test_tool_set_2, test_tool_set_3):
    return [
        test_tool_set_1,
        test_tool_set_2,
        test_tool_set_3,
    ]


@pytest.fixture
def test_mode_1(test_tool_set_1, test_tool_set_2) -> Mode:
    return ModeFactory.create(code="m1", tool_sets=[test_tool_set_1.to_data(), test_tool_set_2.to_data()])


@pytest.fixture
def test_mode_2(test_tool_set_1, test_tool_set_3) -> Mode:
    return ModeFactory.create(code="m2", tool_sets=[test_tool_set_1.to_data(), test_tool_set_3.to_data()])


@pytest.fixture
def test_mode_3(test_tool_set_2, test_tool_set_3) -> Mode:
    return ModeFactory.create(code="m3", tool_sets=[test_tool_set_2.to_data(), test_tool_set_3.to_data()])


@pytest.fixture
def test_modes(test_mode_1, test_mode_2, test_mode_3) -> list[Mode]:
    return [test_mode_1, test_mode_2, test_mode_3]


@pytest.fixture
def test_agent_vendor_active() -> AgentVendor:
    agent_vendor = AgentVendorFactory.create(
        name="agent_vendor_1", description="description_1", base_url="http://base_url_1", avatar_url=None
    )
    agent_vendor.activate()
    return agent_vendor


@pytest.fixture
def test_agent_vendor_2() -> AgentVendor:
    return AgentVendorFactory.create(
        name="agent_vendor_2", description="description_2", base_url="http://base_url_2", avatar_url=None
    )


@pytest.fixture
def test_inactive_agent_vendor() -> AgentVendor:
    return AgentVendorFactory.create(
        name="agent_vendor_3", description="description_3", base_url="http://base_url_3", avatar_url=None
    )


@pytest.fixture
def test_agent_vendors(test_agent_vendor_active, test_agent_vendor_2) -> list[AgentVendor]:
    return [test_agent_vendor_active, test_agent_vendor_2]


@pytest.fixture
def test_inactive_agent_vendors(test_agent_vendor_2, test_inactive_agent_vendor) -> list[AgentVendor]:
    return [test_agent_vendor_2, test_inactive_agent_vendor]


@pytest.fixture
def test_conversation_1(
    tenant_id, test_agent_vendor_active, test_mode_data_1, test_raw_arguments_1, this_user
) -> Conversation:
    conversation = ConversationFactory.create(
        tenant_id=tenant_id,
        agent_provider_id=test_agent_vendor_active.id,
        mode=test_mode_data_1,
        relation=None,
        arguments=test_raw_arguments_1,
        title="Test Conversation 1",
        user_id=this_user["subject"],
    )
    conversation.events.clear()
    return conversation


@pytest.fixture
def test_conversation_with_inactive_agent_vendor(
    tenant_id, test_inactive_agent_vendor, test_mode_data_1, test_raw_arguments_1, this_user
) -> Conversation:
    conversation = ConversationFactory.create(
        tenant_id=tenant_id,
        agent_provider_id=test_inactive_agent_vendor.id,
        mode=test_mode_data_1,
        relation=None,
        arguments=test_raw_arguments_1,
        title="Test Conversation 1",
        user_id=this_user["subject"],
    )
    conversation.events.clear()
    return conversation


@pytest.fixture
def test_conversation_1_with_completions(test_conversation_1) -> Conversation:
    completions = []
    for i in range(1, randint(6, 10)):
        completions.append(
            Completion(
                id_=uuid4().hex,
                question=Question(text=f"Test Question {i}", created_at=datetime.now()),
                execution_context=[ExecutionContext(text=f"Test Execution Context {i}")],
                answer=choice([Answer(text=f"Test Answer {i}", created_at=datetime.now()), None]),
            )
        )
    test_conversation_1.completions = completions

    return test_conversation_1


@pytest.fixture
def test_conversation_1_with_completed_completions(test_conversation_1_with_completions) -> Conversation:
    for completion in test_conversation_1_with_completions.completions:
        if not completion.is_completed():
            completion.add_answer(uuid4().hex)

    return test_conversation_1_with_completions


@pytest.fixture
def test_conversation_2(
    tenant_id, test_agent_vendor_2, test_mode_data_2, test_raw_arguments_2, this_user
) -> Conversation:
    conversation = ConversationFactory.create(
        tenant_id=tenant_id,
        agent_provider_id=test_agent_vendor_2.id,
        mode=test_mode_data_2,
        relation=RelationData(details={"documentId": uuid4().hex}),
        arguments=test_raw_arguments_2,
        title="Test Conversation 2",
        user_id=this_user["subject"],
    )
    conversation.events.clear()
    return conversation


@pytest.fixture
def test_other_user_conversation_1(
    tenant_id,
    test_agent_vendor_active,
    test_mode_data_1,
    test_raw_arguments_1,
) -> Conversation:
    conversation = ConversationFactory.create(
        tenant_id=tenant_id,
        agent_provider_id=test_agent_vendor_active.id,
        mode=test_mode_data_1,
        relation=None,
        arguments=test_raw_arguments_1,
        title="Test Other User Conversation 1",
        user_id="other_user",
    )
    conversation.events.clear()
    return conversation


@pytest.fixture
def test_other_user_conversation_1_with_completions(test_other_user_conversation_1) -> Conversation:
    completion_1 = Completion(
        id_=uuid4().hex,
        question=Question(text="Test Question 1", created_at=datetime.now()),
        execution_context=[ExecutionContext(text="Test Execution Context 1")],
        answer=Answer(text="Test Answer 1", created_at=datetime.now()),
    )
    test_other_user_conversation_1.completions = [completion_1]

    return test_other_user_conversation_1


@pytest.fixture
def test_conversation_2_with_completions(test_conversation_2) -> Conversation:
    completion_1 = Completion(
        id_=uuid4().hex,
        question=Question(text="Test Question 1", created_at=datetime.now()),
        execution_context=[ExecutionContext(text="Test Execution Context 1")],
        answer=Answer(text="Test Answer 1", created_at=datetime.now()),
    )
    test_conversation_2.completions = [completion_1]

    return test_conversation_2


@pytest.fixture
def test_conversations(test_conversation_1, test_conversation_2) -> list[Conversation]:
    return [test_conversation_1, test_conversation_2]


@pytest.fixture
def test_conversations_with_completions(
    test_conversation_1_with_completions, test_conversation_2_with_completions
) -> list[Conversation]:
    return [test_conversation_1_with_completions, test_conversation_2_with_completions]


@pytest.fixture
def test_other_user_conversations_with_completions(
    test_other_user_conversation_1_with_completions,
) -> list[Conversation]:
    return [test_other_user_conversation_1_with_completions]


@pytest.fixture
def test_conversation_with_document_relation(
    tenant_id, test_agent_vendor_active, test_mode_data_1, test_raw_arguments_1, this_user
) -> Conversation:
    conversation = ConversationFactory.create(
        tenant_id=tenant_id,
        agent_provider_id=test_agent_vendor_active.id,
        mode=test_mode_data_1,
        relation=RelationData(details={"documentId": uuid4().hex}),
        arguments=test_raw_arguments_1,
        title="Test Conversation Document Relation",
        user_id=this_user["subject"],
    )
    conversation.events.clear()
    return conversation


@pytest.fixture
def test_conversation_with_document_type_relation(
    tenant_id, test_agent_vendor_active, test_mode_data_1, test_raw_arguments_1, this_user
) -> Conversation:
    conversation = ConversationFactory.create(
        tenant_id=tenant_id,
        agent_provider_id=test_agent_vendor_active.id,
        mode=test_mode_data_1,
        relation=RelationData(details={"documentTypeId": uuid4().hex}),
        arguments=test_raw_arguments_1,
        title="Test Conversation Document Type Relation",
        user_id=this_user["subject"],
    )
    conversation.events.clear()
    return conversation


@pytest.fixture
def unit_of_work(containers):
    uow = containers.unit_of_work()

    yield uow


@pytest_asyncio.fixture(autouse=True)
async def empty_unit_of_work(unit_of_work):
    async with unit_of_work:
        await unit_of_work.tool_sets.erase_all()
        await unit_of_work.modes.erase_all()
        await unit_of_work.agent_vendors._erase_all()
        await unit_of_work.conversations._erase_all()
        await unit_of_work.commit()


@pytest_asyncio.fixture
async def add_tool_sets(unit_of_work, test_tool_sets):
    async with unit_of_work:
        for tool_set in test_tool_sets:
            await unit_of_work.tool_sets.save(tool_set)

        await unit_of_work.commit()

    yield


@pytest_asyncio.fixture
async def add_modes(unit_of_work, test_modes):
    async with unit_of_work:
        for mode in test_modes:
            await unit_of_work.modes.save(mode)

        await unit_of_work.commit()

    yield


@pytest_asyncio.fixture
async def add_agent_vendors(unit_of_work, test_agent_vendors):
    async with unit_of_work:
        await unit_of_work.agent_vendors.save_all(test_agent_vendors)

        await unit_of_work.commit()

    yield


@pytest_asyncio.fixture
async def add_incative_agent_vendors(unit_of_work, test_inactive_agent_vendors):
    async with unit_of_work:
        await unit_of_work.agent_vendors.save_all(test_inactive_agent_vendors)

        await unit_of_work.commit()

    yield


@pytest_asyncio.fixture
async def add_conversations(unit_of_work, test_conversations):
    async with unit_of_work:
        for conversation in test_conversations:
            await unit_of_work.conversations.save(conversation)

        await unit_of_work.commit()

    yield


@pytest_asyncio.fixture
async def add_conversations_with_completions(unit_of_work, test_conversations_with_completions):
    async with unit_of_work:
        for conversation in test_conversations_with_completions:
            await unit_of_work.conversations.save(conversation)

        await unit_of_work.commit()

    yield


@pytest_asyncio.fixture
async def add_other_user_conversations_with_completions(unit_of_work, test_other_user_conversations_with_completions):
    async with unit_of_work:
        for conversation in test_other_user_conversations_with_completions:
            await unit_of_work.conversations.save(conversation)

        await unit_of_work.commit()

    yield


@pytest_asyncio.fixture
async def add_conversations_with_relations(
    unit_of_work,
    test_conversation_with_document_relation,
    test_conversation_with_document_type_relation,
):
    async with unit_of_work:
        await unit_of_work.conversations.save(test_conversation_with_document_relation)
        await unit_of_work.conversations.save(test_conversation_with_document_type_relation)

        await unit_of_work.commit()

    yield


@pytest.fixture
def test_mode_data_1(test_mode_1) -> ModeData:
    return test_mode_1.to_data()


@pytest.fixture
def test_mode_data_2(test_mode_2) -> ModeData:
    return test_mode_2.to_data()


@pytest.fixture
def test_relation_data() -> RelationData:
    return RelationData(details={"document": "123"})


@pytest.fixture
def test_raw_arguments_1(test_mode_data_1) -> dict[ToolSetCode, dict[ToolCode, list[ArgumentData]]]:
    res = {
        tool_set["code"]: {
            tool["code"]: [ArgumentData(parameter=param["name"], value=uuid4().hex) for param in tool["parameters"]]
            for tool in tool_set["tools"]
        }
        for tool_set in test_mode_data_1["tool_sets"]
    }
    return res


@pytest.fixture
def test_raw_arguments_2(test_mode_data_2) -> dict[ToolSetCode, dict[ToolCode, list[ArgumentData]]]:
    res = {
        tool_set["code"]: {
            tool["code"]: [ArgumentData(parameter=param["name"], value=uuid4().hex) for param in tool["parameters"]]
            for tool in tool_set["tools"]
        }
        for tool_set in test_mode_data_2["tool_sets"]
    }
    return res


@pytest.fixture
def test_raw_arguments(
    test_raw_arguments_1, test_raw_arguments_2
) -> list[dict[ToolSetCode, dict[ToolCode, list[ArgumentData]]]]:
    return [test_raw_arguments_1, test_raw_arguments_2]


@pytest.fixture
def test_empty_raw_arguments() -> dict[ToolSetCode, dict[ToolCode, list[ArgumentData]]]:
    return {}
