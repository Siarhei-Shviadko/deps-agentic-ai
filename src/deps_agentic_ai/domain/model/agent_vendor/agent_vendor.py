from ..conversation import (
    ContextArguments,
    Conversation,
    ConversationFactory,
    RelationData,
)
from ..mode import ModeData
from ..shared import Entity, Event, Guard, ImmutableCheck, LengthCheck
from .agent_vendor_deleted import AgentVendorDeleted
from .agent_vendor_id import AgentVendorId
from .connection_parameters import ConnectionParameters

__all__ = ["AgentVendor", "MIN_NAME_LENGTH", "AgentVendorId"]


MIN_NAME_LENGTH = 1


class AgentVendor(metaclass=Entity):  # noqa: WPS230
    id = Guard[AgentVendorId](AgentVendorId, ImmutableCheck())
    name = Guard[str](str, LengthCheck(min_length=MIN_NAME_LENGTH))
    description = Guard[str](str)
    connection_parameters = Guard[ConnectionParameters](ConnectionParameters)
    active = Guard[bool](bool)
    avatar_url = Guard[str](str)

    def __init__(
        self,
        id_: str,
        name: str,
        description: str,
        connection_parameters: ConnectionParameters,
        active: bool = False,
        avatar_url: str | None = None,
        *,
        events: list[Event] | None = None,
    ) -> None:
        self.id = AgentVendorId(id_)
        self.name = name
        self.description = description
        self.connection_parameters = connection_parameters
        self.active = active

        if avatar_url:
            self.avatar_url = avatar_url

        self.events = events or []

    def activate(self) -> None:
        self.active = True

    def deactivate(self) -> None:
        self.active = False

    def update_info(self, name: str, description: str, avatar_url: str | None) -> None:
        self.name = name
        self.description = description
        if avatar_url is not None:
            self.avatar_url = avatar_url

    def update_connection_parameters(self, base_url: str) -> None:
        self.connection_parameters = ConnectionParameters(base_url)

    def create_conversation(
        self,
        tenant_id: str,
        mode_data: ModeData,
        title: str,
        arguments: ContextArguments,
        user_id: str,
        relation: RelationData | None,
    ) -> Conversation:
        return ConversationFactory.create(
            tenant_id=tenant_id,
            agent_provider_id=self.id,
            mode=mode_data,
            relation=relation,
            title=title,
            arguments=arguments,
            user_id=user_id,
        )

    def delete(self) -> None:
        self.events.append(AgentVendorDeleted(id=self.id()))
