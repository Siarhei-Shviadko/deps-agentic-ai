from deps_agentic_ai.domain.exceptions import AgenticAiException

__all__ = ["RestClientError", "AgentVendorProxyError"]


class RestClientError(AgenticAiException):
    code = "rest_client_error"


class AgentVendorProxyError(RestClientError):
    code = "agent_vendor_proxy_error"
