import logging
from typing import AsyncGenerator

from deps_message_flow.events.publisher import DomainEventPublisher

from deps_agentic_ai.constants import CONVERSATION_DESTINATION
from deps_agentic_ai.domain.exceptions import (
    AgentVendorNotFound,
    ConversationNotFound,
    InactiveAgentVendor,
    ModeNotFound,
)
from deps_agentic_ai.domain.model.agent_vendor import AgentVendor
from deps_agentic_ai.domain.model.conversation import (
    AgentRequest,
    AgentResponse,
    AgentResponseType,
    ContextArguments,
    Conversation,
    RelationData,
)
from deps_agentic_ai.domain.model.mode import ModeData
from deps_agentic_ai.infrastructure.unit_of_work import AbstractUnitOfWork

from ..retry_transaction import retry_on_transaction_error
from .stream_proxy_protocol import SSEEvent, StreamProxyProtocol

__all__ = ["CommandConversationService"]


class CommandConversationService:  # noqa: WPS214
    def __init__(
        self,
        unit_of_work: AbstractUnitOfWork,
        domain_event_publisher: DomainEventPublisher,
        agent_vendor_proxy: StreamProxyProtocol,
    ) -> None:
        self._uow = unit_of_work
        self._domain_event_publisher = domain_event_publisher
        self._agent_vendor_proxy = agent_vendor_proxy

        self._logger = logging.getLogger(self.__class__.__name__)

    @retry_on_transaction_error()
    async def create(
        self,
        tenant_id: str,
        agent_vendor_id: str,
        mode_id: str,
        title: str,
        arguments: ContextArguments,
        user_id: str,
        relation_data: RelationData | None,
    ) -> Conversation:
        async with self._uow:
            agent_vendor = await self._uow.agent_vendors.agent_vendor_of_id(agent_vendor_id)
            mode_data = await self._uow.modes.mode_of_id_data(mode_id)

            self._validate_agent_vendor_and_mode(
                agent_vendor_id=agent_vendor_id, agent_vendor=agent_vendor, mode_id=mode_id, mode_data=mode_data
            )

            conversation = agent_vendor.create_conversation(
                tenant_id=tenant_id,
                mode_data=mode_data,
                title=title,
                arguments=arguments,
                user_id=user_id,
                relation=relation_data,
            )

            await self._uow.conversations.save(conversation)

            self._publish_events(conversation)

            await self._uow.commit()

        self._logger.debug(
            "Conversation with id `%s` for user `%s` and tenant `%s` created.", conversation.id(), user_id, tenant_id
        )

        return conversation

    async def conversation_of_id(self, id_: str, user_id: str, tenant_id: str) -> Conversation:
        async with self._uow:
            conversation = await self._uow.conversations.conversation_of_id(
                id_=id_, user_id=user_id, tenant_id=tenant_id
            )
            if not conversation:
                raise ConversationNotFound(id_)
        return conversation

    @retry_on_transaction_error()
    async def update(self, id_: str, user_id: str, tenant_id: str, title: str) -> Conversation:
        conversation = await self.conversation_of_id(id_=id_, user_id=user_id, tenant_id=tenant_id)
        async with self._uow:
            conversation.change_title(title=title)

            await self._uow.conversations.save(conversation)

            self._publish_events(conversation)

            await self._uow.commit()

        self._logger.debug(
            "Conversation with id `%s` for user `%s` and tenant `%s` updated.", conversation.id(), user_id, tenant_id
        )

        return conversation

    @retry_on_transaction_error()
    async def delete_conversations(self, ids: list[str], user_id: str, tenant_id: str) -> None:
        async with self._uow:
            conversations = await self._uow.conversations.conversations_of_ids(
                ids=ids, user_id=user_id, tenant_id=tenant_id
            )

            for conversation in conversations:
                conversation.delete()

            await self._uow.conversations.delete_all(conversations)

            for conversation in conversations:
                self._publish_events(conversation)

            await self._uow.commit()

        self._logger.info("Conversations with ids `%s` deleted.", [conv.id() for conv in conversations])

    @retry_on_transaction_error()
    async def delete_with_agent_vendor(self, agent_vendor_id: str) -> None:
        async with self._uow:
            conversations = await self._uow.conversations.conversations_with_agent_vendor(agent_vendor_id)

            for conversation in conversations:
                conversation.delete()

            await self._uow.conversations.delete_all(conversations)

            for conversation in conversations:
                self._publish_events(conversation)

            await self._uow.commit()

        self._logger.info("Conversations with ids `%s` deleted.", [conv.id() for conv in conversations])

    @retry_on_transaction_error()
    async def delete_with_document_relation(self, document_id: str) -> None:
        async with self._uow:
            conversations = await self._uow.conversations.conversations_with_document_relation(document_id)

            for conversation in conversations:
                conversation.delete()

            await self._uow.conversations.delete_all(conversations)

            await self._uow.commit()

        for conversation in conversations:
            self._publish_events(conversation)

        self._logger.info("Conversations with ids `%s` deleted.", [conv.id() for conv in conversations])

    @retry_on_transaction_error()
    async def delete_with_document_type_relation(self, document_type_id: str, tenant_id: str) -> None:
        async with self._uow:
            conversations = await self._uow.conversations.conversations_with_document_type_relation(
                document_type_id, tenant_id
            )

            for conversation in conversations:
                conversation.delete()

            await self._uow.conversations.delete_all(conversations)

            await self._uow.commit()

        for conversation in conversations:
            self._publish_events(conversation)

        self._logger.info("Conversations with ids `%s` deleted.", [conv.id() for conv in conversations])

    async def validate_chat_preconditions(
        self, conversation_id: str, user_id: str, tenant_id: str
    ) -> tuple[Conversation, AgentVendor]:
        conversation = await self.conversation_of_id(id_=conversation_id, user_id=user_id, tenant_id=tenant_id)

        async with self._uow:
            agent_vendor = await self._uow.agent_vendors.agent_vendor_of_id(conversation.agent_vendor_id())
            if not agent_vendor:
                raise AgentVendorNotFound(conversation.agent_vendor_id())

            elif not agent_vendor.active:
                raise InactiveAgentVendor(f"Agent vendor {conversation.agent_vendor_id()} is not active")

        return conversation, agent_vendor

    async def chat(
        self,
        conversation: Conversation,
        agent_vendor: AgentVendor,
        user_question: str,
        arguments: ContextArguments | None = None,
    ) -> AsyncGenerator[SSEEvent, None]:
        async with self._uow:
            agent_request = conversation.add_question(
                question=user_question,
                agent_vendor_base_url=agent_vendor.connection_parameters.base_url,
                arguments=arguments,
            )

            await self._uow.conversations.save(conversation)
            self._publish_events(conversation)
            await self._uow.commit()

        async for event in self._stream_agent_vendor_sse(
            conversation,
            agent_request,
        ):
            yield event

    async def edit_question(
        self,
        conversation: Conversation,
        agent_vendor: AgentVendor,
        completion_id: str,
        user_question: str,
        arguments: ContextArguments | None = None,
    ) -> AsyncGenerator[SSEEvent, None]:
        async with self._uow:
            agent_request = conversation.edit_question(
                completion_id=completion_id,
                new_text=user_question,
                agent_vendor_base_url=agent_vendor.connection_parameters.base_url,
                new_arguments=arguments,
            )

            await self._uow.conversations.update(conversation)
            self._publish_events(conversation)
            await self._uow.commit()

        async for event in self._stream_agent_vendor_sse(
            conversation,
            agent_request,
        ):
            yield event

    def _validate_agent_vendor_and_mode(
        self,
        agent_vendor_id: str,
        agent_vendor: AgentVendor | None,
        mode_id: str,
        mode_data: ModeData | None,
    ) -> None:
        if not agent_vendor or not mode_data:
            agent_vendor_detail = f"Agent vendor `{agent_vendor_id}` not found" if not agent_vendor else ""
            mode_detail = f"Mode `{mode_id}` not found" if not mode_data else ""

            self._logger.error(
                "Conversation cannot be created. Reason: %s", ", ".join([agent_vendor_detail, mode_detail])
            )

            raise AgentVendorNotFound(agent_vendor_id) if not agent_vendor else ModeNotFound(mode_id)

    async def _stream_agent_vendor_sse(
        self,
        conversation: Conversation,
        agent_request: AgentRequest,
    ) -> AsyncGenerator[SSEEvent, None]:
        try:  # noqa: WPS501
            async for event in self._agent_vendor_proxy.stream_chat(agent_request, agent_request.agent_vendor_base_url):
                response = AgentResponse(type=AgentResponseType(event.type), text=event.text)
                conversation.add_agent_response(response)
                await self._save_conversation(conversation)
                yield event
        finally:
            await self._save_conversation(conversation)

    async def _save_conversation(
        self,
        conversation: Conversation,
    ) -> None:
        async with self._uow:
            await self._uow.conversations.save(conversation)
            self._publish_events(conversation)
            await self._uow.commit()

    def _publish_events(self, conversation: Conversation) -> None:
        self._domain_event_publisher.publish(
            aggregate_type=CONVERSATION_DESTINATION,
            aggregate_id=conversation.id(),
            domain_events=conversation.events,
        )
