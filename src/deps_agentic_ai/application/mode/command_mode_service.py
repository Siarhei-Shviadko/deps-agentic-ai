import logging

from deps_message_flow.events.publisher import DomainEventPublisher

from deps_agentic_ai.constants import CONVERSATION_DESTINATION, MODE_DESTINATION
from deps_agentic_ai.domain.exceptions import (
    ModeAlreadyExists,
    ModeNotFound,
    ToolSetsNotFound,
)
from deps_agentic_ai.domain.model.conversation import Conversation
from deps_agentic_ai.domain.model.mode import Mode, ModeFactory
from deps_agentic_ai.domain.model.tool_set import ToolSetData
from deps_agentic_ai.infrastructure.unit_of_work import AbstractUnitOfWork

from ..retry_transaction import retry_on_transaction_error

__all__ = ["CommandModeService"]


class CommandModeService:
    def __init__(
        self,
        unit_of_work: AbstractUnitOfWork,
        domain_event_publisher: DomainEventPublisher,
    ) -> None:
        self._uow = unit_of_work
        self._domain_event_publisher = domain_event_publisher

        self._logger = logging.getLogger(self.__class__.__name__)

    @retry_on_transaction_error()
    async def create(self, code: str, tool_set_ids: list[str]) -> Mode:
        async with self._uow:
            if await self._uow.modes.has_mode_with_code(code):
                raise ModeAlreadyExists(code)

            tool_sets = await self._get_tool_sets(tool_set_ids)
            mode = ModeFactory.create(code, tool_sets)

            await self._uow.modes.save(mode)

            self._publish_events(mode)

            await self._uow.commit()

        self._logger.info("Mode with code `%s` created. Id - `%s`.", code, mode.id())

        return mode

    @retry_on_transaction_error()
    async def update_code(self, id_: str, code: str) -> Mode:
        async with self._uow:
            mode = await self._get_mode(id_)

            if mode.code == code:
                return mode

            if await self._uow.modes.has_mode_with_code(code):
                raise ModeAlreadyExists(code)

            mode.update_code(code)

            await self._uow.modes.save(mode)

            self._publish_events(mode)

            await self._uow.commit()

        self._logger.info("Mode with id `%s` updated. New code - `%s`.", mode.id(), code)

        return mode

    @retry_on_transaction_error()
    async def update_tool_sets(
        self, id_: str, tool_sets_to_add_ids: list[str], tool_sets_to_remove_ids: list[str]
    ) -> Mode:
        async with self._uow:
            mode = await self._get_mode(id_)
            tool_sets_to_add = await self._get_tool_sets(tool_sets_to_add_ids)

            mode.update_tool_sets(add=tool_sets_to_add, remove=tool_sets_to_remove_ids)

            await self._uow.modes.save(mode)

            self._publish_events(mode)

            await self._uow.commit()

        self._logger.info(
            "Mode with id `%s` updated. Removed tool sets - `%s`. Added tool sets - `%s`.",
            mode.id(),
            tool_sets_to_remove_ids,
            tool_sets_to_add_ids,
        )

        return mode

    @retry_on_transaction_error()
    async def delete(self, ids: list[str]) -> list[Mode]:
        async with self._uow:
            modes = await self._uow.modes.modes_of_ids(ids)
            conversations_with_modes = await self._uow.conversations.conversations_with_modes(ids)

            for conversation in conversations_with_modes:
                conversation.delete()

            await self._uow.conversations.delete_all(conversations_with_modes)

            for mode in modes:
                mode.delete()

            await self._uow.modes.delete_all(modes)

            await self._uow.commit()

        for conversation in conversations_with_modes:
            self._publish_events_conversations(conversation)

        for mode in modes:
            self._publish_events(mode)

        self._logger.info("Modes with ids `%s` deleted.", ids)
        self._logger.info("Conversations with ids `%s` deleted.", [conv.id() for conv in conversations_with_modes])

        return modes

    async def _get_tool_sets(self, tool_set_ids: list[str]) -> list[ToolSetData]:
        tool_sets = await self._uow.tool_sets.tool_sets_of_ids_data(tool_set_ids)

        if len(tool_sets) < len(set(tool_set_ids)):
            raise ToolSetsNotFound(set(tool_set_ids) - {ts["id"] for ts in tool_sets})

        return tool_sets

    async def _get_mode(self, mode_id: str) -> Mode:
        if not (mode := await self._uow.modes.mode_of_id(mode_id)):
            raise ModeNotFound(mode_id)

        return mode

    def _publish_events(self, mode: Mode) -> None:
        self._domain_event_publisher.publish(
            aggregate_type=MODE_DESTINATION,
            aggregate_id=mode.id(),
            domain_events=mode.events,
        )

    def _publish_events_conversations(self, conversation: Conversation) -> None:
        self._domain_event_publisher.publish(
            aggregate_type=CONVERSATION_DESTINATION,
            aggregate_id=conversation.id(),
            domain_events=conversation.events,
        )
