from uuid import uuid4

from .agent_vendor import AgentVendor
from .connection_parameters import ConnectionParameters

__all__ = ["AgentVendorFactory"]


class AgentVendorFactory:
    @staticmethod
    def create(name: str, description: str, base_url: str, avatar_url: str | None = None) -> AgentVendor:
        return AgentVendor(
            id_=uuid4().hex,
            name=name,
            description=description,
            connection_parameters=ConnectionParameters(base_url),
            avatar_url=avatar_url,
        )
