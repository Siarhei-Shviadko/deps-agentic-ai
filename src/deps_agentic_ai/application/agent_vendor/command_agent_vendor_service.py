import logging

from deps_message_flow.events.publisher import DomainEventPublisher

from deps_agentic_ai.constants import AGENT_VENDOR_DESTINATION
from deps_agentic_ai.domain.exceptions import (
    AgentVendorAlreadyExists,
    AgentVendorNotFound,
)
from deps_agentic_ai.domain.model.agent_vendor import AgentVendor, AgentVendorFactory
from deps_agentic_ai.infrastructure.unit_of_work import AbstractUnitOfWork

from ..retry_transaction import retry_on_transaction_error

__all__ = ["CommandAgentVendorService"]


class CommandAgentVendorService:
    def __init__(
        self,
        unit_of_work: AbstractUnitOfWork,
        domain_event_publisher: DomainEventPublisher,
    ) -> None:
        self._uow = unit_of_work
        self._domain_event_publisher = domain_event_publisher

        self._logger = logging.getLogger(self.__class__.__name__)

    @retry_on_transaction_error()
    async def create(self, name: str, description: str, base_url: str, avatar_url: str | None = None) -> AgentVendor:
        async with self._uow:
            if await self._uow.agent_vendors.has_agent_vendor_with_name(name):
                raise AgentVendorAlreadyExists(name)

            agent_vendor = AgentVendorFactory.create(
                name=name, description=description, base_url=base_url, avatar_url=avatar_url
            )

            await self._uow.agent_vendors.save(agent_vendor)

            self._publish_events(agent_vendor)

            await self._uow.commit()

        self._logger.info("AgentVendor with name `%s` created. Id - `%s`.", name, agent_vendor.id())

        return agent_vendor

    @retry_on_transaction_error()
    async def activate(self, id_: str) -> AgentVendor:
        async with self._uow:
            if not (target_agent_vendor := await self._uow.agent_vendors.agent_vendor_of_id(id_)):
                raise AgentVendorNotFound(id_)

            if target_agent_vendor.active:
                self._logger.info("AgentVendor with ID `%s` is already active", id_)
                return target_agent_vendor

            if active_agent_vendor := await self._uow.agent_vendors.active_agent_vendor():
                self._logger.info("Deactivating currently active AgentVendor with ID `%s`.", active_agent_vendor.id())
                active_agent_vendor.deactivate()

            target_agent_vendor.activate()

            await self._uow.agent_vendors.save_all(
                [agent_vendor for agent_vendor in (active_agent_vendor, target_agent_vendor) if agent_vendor]
            )
            await self._uow.commit()

        self._logger.info("AgentVendor with ID `%s` has been activated.", id_)
        self._publish_events(target_agent_vendor)

        return target_agent_vendor

    @retry_on_transaction_error()
    async def update_info(self, id_: str, name: str, description: str, avatar_url: str | None) -> AgentVendor:
        async with self._uow:
            if not (agent_vendor := await self._uow.agent_vendors.agent_vendor_of_id(id_)):
                raise AgentVendorNotFound(id_)

            if agent_vendor.name != name and await self._uow.agent_vendors.has_agent_vendor_with_name(name):
                raise AgentVendorAlreadyExists(name)

            agent_vendor.update_info(name=name, description=description, avatar_url=avatar_url)

            await self._uow.agent_vendors.save(agent_vendor)
            await self._uow.commit()

        self._logger.info("AgentVendor with ID `%s` info has been updated.", id_)
        self._publish_events(agent_vendor)

        return agent_vendor

    @retry_on_transaction_error()
    async def update_connection_parameters(self, id_: str, base_url: str) -> AgentVendor:
        async with self._uow:
            if not (agent_vendor := await self._uow.agent_vendors.agent_vendor_of_id(id_)):
                raise AgentVendorNotFound(id_)

            agent_vendor.update_connection_parameters(base_url=base_url)

            await self._uow.agent_vendors.save(agent_vendor)
            await self._uow.commit()

        self._publish_events(agent_vendor)
        self._logger.info("AgentVendor with ID `%s` connection parameters have been updated.", id_)

        return agent_vendor

    @retry_on_transaction_error()
    async def delete(self, id_: str) -> None:
        async with self._uow:
            if not (target_agent_vendor := await self._uow.agent_vendors.agent_vendor_of_id(id_)):
                raise AgentVendorNotFound(id_)

            target_agent_vendor.delete()

            await self._uow.agent_vendors.delete(target_agent_vendor)

            self._publish_events(target_agent_vendor)

            await self._uow.commit()

            self._logger.info("AgentVendor with ID `%s` has been deleted.", id_)

    def _publish_events(self, agent_vendor: AgentVendor) -> None:
        self._domain_event_publisher.publish(
            aggregate_type=AGENT_VENDOR_DESTINATION,
            aggregate_id=agent_vendor.id(),
            domain_events=agent_vendor.events,
        )
