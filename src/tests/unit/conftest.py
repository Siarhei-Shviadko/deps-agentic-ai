from uuid import uuid4

import pytest
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_agentic_ai.application import CommandConversationService
from tests.fakes import (
    FakeCommandAgentVendorRepository,
    FakeCommandConversationRepository,
    FakeCommandModeRepository,
    FakeCommandToolSetRepository,
    FakeUnitOfWork,
)


@pytest.fixture
def postgres_session_mock(mocker, containers):
    mock = mocker.Mock(containers.datasources.postgres_session())
    containers.datasources.postgres_session.override(mock)

    yield mock

    containers.datasources.postgres_session.reset_override()


@pytest.fixture(autouse=True, scope="session")
def unit_of_work(
    containers,
):
    fuow = FakeUnitOfWork(
        tool_sets=FakeCommandToolSetRepository(),
        modes=FakeCommandModeRepository(),
        agent_vendors=FakeCommandAgentVendorRepository(),
        conversations=FakeCommandConversationRepository(),
    )

    containers.unit_of_work.override(fuow)

    yield fuow

    containers.unit_of_work.reset_override()


@pytest.fixture
def mock_command_conversation_service(mocker, containers) -> CommandConversationService:  # type: ignore
    containers.reset_singletons()
    with containers.command_conversation_service.override(mocker.Mock(containers.command_conversation_service.cls)):
        yield containers.command_conversation_service()


@pytest.fixture
def agent_vendor_deleted_event(mocker) -> DomainEventEnvelope:
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event.id = uuid4().hex
    return dee


@pytest.fixture
def mode_deleted_event(mocker) -> DomainEventEnvelope:
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event.id = uuid4().hex
    return dee


@pytest.fixture
def document_deleted_event(mocker) -> DomainEventEnvelope:
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event.document_id = uuid4().hex
    return dee


@pytest.fixture
def document_type_deleted_event(mocker) -> DomainEventEnvelope:
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event.document_type = uuid4().hex
    dee.event.tenant = uuid4().hex
    return dee
