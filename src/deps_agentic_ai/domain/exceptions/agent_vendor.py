from .base import AgenticAiException, AlreadyExists, NotFound

__all__ = ["AgentVendorAlreadyExists", "AgentVendorNotFound", "InactiveAgentVendor"]


class AgentVendorAlreadyExists(AlreadyExists):
    code = "agent_vendor_already_exists"

    def __init__(self, name: str) -> None:
        super().__init__(f"AgentVendor with name `{name}` already exists.")


class AgentVendorNotFound(NotFound):
    code = "agent_vendor_not_found"

    def __init__(self, id: str) -> None:
        super().__init__(f"AgentVendor with id `{id}` not found.")


class InactiveAgentVendor(AgenticAiException):
    code = "inactive_agent_vendor"
