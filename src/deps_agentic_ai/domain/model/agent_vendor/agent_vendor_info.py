from typing import TypedDict

__all__ = ["AgentVendorsInfo", "AgentVendorInfo", "ConnectionParametersInfo"]


class ConnectionParametersInfo(TypedDict):
    base_url: str


class AgentVendorInfo(TypedDict):
    id: str
    name: str
    description: str
    active: bool
    avatar_url: str | None
    connection_parameters: ConnectionParametersInfo


class AgentVendorsInfo(TypedDict):
    agent_vendors: list[AgentVendorInfo]
