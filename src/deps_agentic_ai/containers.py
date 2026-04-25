from typing import Any, Dict, Optional, Type, Union

from dependency_injector import containers, providers, resources
from deps_asb import ASBClient, ASBConsumer, ASBProducer
from deps_kafka import KafkaClient, KafkaConsumer, KafkaProducer
from deps_message_flow import MessagingDriverEnum
from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer
from deps_rabbitmq import RabbitMQClient, RabbitMQConsumer, RabbitMQProducer

from deps_agentic_ai.application import (
    CommandAgentVendorService,
    CommandConversationService,
    CommandModeService,
    CommandToolSetService,
    QueryAgentVendorService,
    QueryConversationService,
    QueryModeService,
    QueryToolSetService,
)
from deps_agentic_ai.constants import PROJECT_NAME
from deps_agentic_ai.domain.model.agent_vendor import IQueryAgentVendorRepository
from deps_agentic_ai.domain.model.conversation import IQueryConversationRepository
from deps_agentic_ai.domain.model.mode import IQueryModeRepository
from deps_agentic_ai.domain.model.tool_set import IQueryToolSetRepository
from deps_agentic_ai.extras import AsyncDatabaseSession
from deps_agentic_ai.infrastructure.access_management import user
from deps_agentic_ai.infrastructure.proxies import AgentVendorProxy
from deps_agentic_ai.infrastructure.repositories import (
    QueryAgentVendorRepository,
    QueryConversationRepository,
    QueryModeRepository,
    QueryToolSetRepository,
)
from deps_agentic_ai.infrastructure.unit_of_work import (
    AbstractUnitOfWork,
    SqlAlchemyUnitOfWork,
)
from deps_agentic_ai.messaging.dispatcher import make_message_dispatcher

MessagingClient = Union[ASBClient, KafkaClient, RabbitMQClient]


class MessageBrokerResource(resources.Resource):
    def init(
        self,
        driver_type: str,
        expected_driver: str,
        client: Type[MessagingClient],
        message_connection_string: str,
        **kwargs: Dict[str, Any],
    ) -> Optional[MessagingClient]:
        return client(message_connection_string, **kwargs) if driver_type == expected_driver else None

    def shutdown(self, resource: Optional[MessagingClient]) -> None:
        if resource:
            resource.close()


class MessageBrokers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    broker_client: providers.Provider[MessagingClient] = providers.Selector(
        config.messaging_driver,
        asb=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.ASB.value,
            expected_driver=config.messaging_driver,
            client=ASBClient,
            message_connection_string=config.message_broker_connection_string,
            asb_settings=messaging_driver_settings,
        ),
        kafka=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.KAFKA.value,
            expected_driver=config.messaging_driver,
            client=KafkaClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
        rabbitmq=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.RABBITMQ.value,
            expected_driver=config.messaging_driver,
            client=RabbitMQClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
    )


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()
    message_brokers = providers.DependenciesContainer()

    producer: providers.Provider[IMessageProducer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBProducer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
        ),
        kafka=providers.Singleton(
            KafkaProducer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQProducer,
            client=message_brokers.broker_client,
        ),
    )
    consumer: providers.Provider[IMessageConsumer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBConsumer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
            custom_subscription_name=PROJECT_NAME,
        ),
        kafka=providers.Singleton(
            KafkaConsumer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQConsumer,
            client=message_brokers.broker_client,
        ),
    )


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
    build_info: providers.Provider[Dict] = providers.Dict(
        {
            "build_tag": config.info.tag,
            "build_date": config.info.date,
            "commit_hash": config.info.hash,
        },
    )


class Datasources(containers.DeclarativeContainer):
    config = providers.Configuration()

    postgres_session: providers.Provider[AsyncDatabaseSession] = providers.Singleton(AsyncDatabaseSession)


class Repositories(containers.DeclarativeContainer):
    config = providers.Configuration()
    datasources = providers.DependenciesContainer()

    query_tool_set: providers.Singleton[IQueryToolSetRepository] = providers.Singleton(
        QueryToolSetRepository,
        database=datasources.postgres_session,
    )

    query_mode: providers.Singleton[IQueryModeRepository] = providers.Singleton(
        QueryModeRepository,
        database=datasources.postgres_session,
    )
    query_agent_vendor: providers.Singleton[IQueryAgentVendorRepository] = providers.Singleton(
        QueryAgentVendorRepository,
        database=datasources.postgres_session,
    )

    query_conversation: providers.Singleton[IQueryConversationRepository] = providers.Singleton(
        QueryConversationRepository,
        database=datasources.postgres_session,
    )


class Containers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)
    current_user = providers.Callable(lambda: user.get())

    datasources: providers.Container[Datasources] = providers.Container(
        Datasources,
        config=config.database,
    )

    repositories: providers.Container[Repositories] = providers.Container(
        Repositories,
        config=config,
        datasources=datasources,
    )

    core: providers.Container[Core] = providers.Container(Core, config=config)
    message_brokers: providers.Container[MessageBrokers] = providers.Container(
        MessageBrokers,
        config=config,
        messaging_driver_settings=messaging_driver_settings,
    )

    messaging: providers.Container[Messaging] = providers.Container(
        Messaging,
        config=config,
        message_brokers=message_brokers,
    )

    command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        CommandProducer,
        messaging.producer,
    )

    domain_event_publisher: providers.Singleton[DomainEventPublisher] = providers.Singleton(
        DomainEventPublisher,
        messaging.producer,
    )

    message_dispatcher: providers.Singleton[IMessageConsumer] = providers.Singleton(
        make_message_dispatcher,
        messaging.consumer,
        messaging.producer,
    )

    unit_of_work: providers.Singleton[AbstractUnitOfWork] = providers.Singleton(
        SqlAlchemyUnitOfWork,
        database_session=datasources.postgres_session,
    )

    query_tool_set_service: providers.Singleton[QueryToolSetService] = providers.Singleton(
        QueryToolSetService,
        query_tool_set_repository=repositories.query_tool_set,
    )

    command_tool_set_service: providers.Singleton[CommandToolSetService] = providers.Singleton(
        CommandToolSetService,
        unit_of_work=unit_of_work,
        domain_event_publisher=domain_event_publisher,
    )

    query_mode_service: providers.Singleton[QueryModeService] = providers.Singleton(
        QueryModeService,
        query_mode_repository=repositories.query_mode,
    )

    command_mode_service: providers.Singleton[CommandModeService] = providers.Singleton(
        CommandModeService,
        unit_of_work=unit_of_work,
        domain_event_publisher=domain_event_publisher,
    )

    command_agent_vendor_service: providers.Singleton[CommandAgentVendorService] = providers.Singleton(
        CommandAgentVendorService,
        unit_of_work=unit_of_work,
        domain_event_publisher=domain_event_publisher,
    )

    query_agent_vendor_service: providers.Singleton[QueryAgentVendorService] = providers.Singleton(
        QueryAgentVendorService,
        query_agent_vendor_repository=repositories.query_agent_vendor,
    )

    agent_vendor_proxy: providers.Singleton[AgentVendorProxy] = providers.Singleton(
        AgentVendorProxy,
        user_context=providers.Object(user),
    )

    command_conversation_service: providers.Singleton[CommandConversationService] = providers.Singleton(
        CommandConversationService,
        unit_of_work=unit_of_work,
        domain_event_publisher=domain_event_publisher,
        agent_vendor_proxy=agent_vendor_proxy,
    )

    query_conversation_service: providers.Singleton[QueryConversationService] = providers.Singleton(
        QueryConversationService,
        query_conversation_repository=repositories.query_conversation,
    )
