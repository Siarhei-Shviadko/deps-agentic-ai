import logging

from deps_message_flow.events.publisher import DomainEventPublisher

from deps_agentic_ai.constants import TOOL_SET_DESTINATION
from deps_agentic_ai.domain.model.tool_set import ToolData, ToolSet, ToolSetFactory
from deps_agentic_ai.infrastructure.unit_of_work import AbstractUnitOfWork

from ..retry_transaction import retry_on_transaction_error

__all__ = ["CommandToolSetService"]


class CommandToolSetService:
    def __init__(
        self,
        unit_of_work: AbstractUnitOfWork,
        domain_event_publisher: DomainEventPublisher,
    ) -> None:
        self._uow = unit_of_work
        self._domain_event_publisher = domain_event_publisher

        self._logger = logging.getLogger(self.__class__.__name__)

    @retry_on_transaction_error()
    async def register(self, code: str, name: str, tools: list[ToolData]) -> ToolSet:
        async with self._uow:
            if (tool_set := await self._uow.tool_sets.tool_set_with_code(code)) is None:
                tool_set = ToolSetFactory.create(code=code, name=name, tools=tools)

            else:
                tool_set.update(name=name, tools=tools)

            await self._uow.tool_sets.save(tool_set)

            self._publish_events(tool_set)

            await self._uow.commit()

        self._logger.info("Tool set with code `%s` registered. Id - `%s`.", code, tool_set.id())

        return tool_set

    @retry_on_transaction_error()
    async def delete(self, ids: list[str]) -> list[ToolSet]:
        async with self._uow:
            tool_sets = await self._uow.tool_sets.tool_sets_of_ids(ids)

            for tool_set in tool_sets:
                tool_set.delete()

            await self._uow.tool_sets.delete_all(tool_sets)

            for tool_set in tool_sets:
                self._publish_events(tool_set)

            await self._uow.commit()

        self._logger.info("Tool sets with ids `%s` deleted.", ids)

        return tool_sets

    def _publish_events(self, tool_set: ToolSet) -> None:
        self._domain_event_publisher.publish(
            aggregate_type=TOOL_SET_DESTINATION,
            aggregate_id=tool_set.id(),
            domain_events=tool_set.events,
        )
