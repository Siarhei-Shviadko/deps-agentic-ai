import logging

from deps_message_flow.commands.consumer import (
    CommandDispatcher,
    CommandHandlersBuilder,
)
from deps_message_flow.events.subscriber import (
    DomainEventDispatcher,
    DomainEventHandlersBuilder,
)
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer

from deps_agentic_ai.constants import (
    AGENT_VENDOR_DESTINATION,
    COMMANDS_QUEUE,
    COMMANDS_REPLIES_CHANNEL,
    DOCUMENT_DESTINATION,
    DOCUMENT_TYPE_DESTINATION,
    EVENTS_QUEUE,
)
from deps_agentic_ai.domain.events import TestCommandReply
from deps_agentic_ai.domain.model import AgentVendorDeleted

from .events import DocumentDeleted, DocumentTypeDeleted

_logger = logging.getLogger(__name__)


def make_message_dispatcher(subscriber: IMessageConsumer, producer: IMessageProducer) -> IMessageConsumer:
    from deps_agentic_ai.messaging.handlers import (  # noqa: WPS433
        agent_vendor_deleted_handler,
        document_deleted_handler,
        document_type_deleted_handler,
        test_command_handler,
    )

    events_handlers = (
        DomainEventHandlersBuilder.for_aggregate_type(AGENT_VENDOR_DESTINATION)
        .on_event(AgentVendorDeleted, agent_vendor_deleted_handler)
        .and_for_aggregate_type(DOCUMENT_DESTINATION)
        .on_event(DocumentDeleted, document_deleted_handler)
        .and_for_aggregate_type(DOCUMENT_TYPE_DESTINATION)
        .on_event(DocumentTypeDeleted, document_type_deleted_handler)
        .for_queue(EVENTS_QUEUE)
        .build()
    )

    commands_handlers = (
        CommandHandlersBuilder.from_channel(COMMANDS_REPLIES_CHANNEL)
        .on_message(TestCommandReply, test_command_handler)
        .for_queue(COMMANDS_QUEUE)
        .build()
    )

    ded = DomainEventDispatcher(events_handlers, subscriber)
    ded.initialize()

    cd = CommandDispatcher(commands_handlers, subscriber, producer)
    cd.initialize()

    _logger.info("Start consuming....")

    return subscriber
