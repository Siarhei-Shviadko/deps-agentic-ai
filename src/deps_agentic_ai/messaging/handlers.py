import asyncio
import logging

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.consumer.command_message import CommandMessage
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_agentic_ai.application import CommandConversationService
from deps_agentic_ai.containers import Containers

logger = logging.getLogger(__name__)


def test_command_handler(command_message: CommandMessage):
    pass


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)


@inject
def agent_vendor_deleted_handler(
    dee: DomainEventEnvelope,
    conversation_service: CommandConversationService = Provide[Containers.command_conversation_service],
):
    run_async(conversation_service.delete_with_agent_vendor(dee.event.id))


@inject
def document_deleted_handler(
    dee: DomainEventEnvelope,
    conversation_service: CommandConversationService = Provide[Containers.command_conversation_service],
):
    run_async(conversation_service.delete_with_document_relation(dee.event.document_id))


@inject
def document_type_deleted_handler(
    dee: DomainEventEnvelope,
    conversation_service: CommandConversationService = Provide[Containers.command_conversation_service],
):
    run_async(conversation_service.delete_with_document_type_relation(dee.event.document_type, dee.event.tenant))
