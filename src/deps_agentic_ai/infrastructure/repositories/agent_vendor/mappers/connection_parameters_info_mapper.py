from typing import Any, Mapping

from deps_agentic_ai.domain.model.agent_vendor import ConnectionParametersInfo

__all__ = ["ConnectionParametersInfoMapper"]


class ConnectionParametersInfoMapper:
    @staticmethod
    def from_mappings(connection_parameters: Mapping[str, Any]) -> ConnectionParametersInfo:
        return ConnectionParametersInfo(base_url=connection_parameters["base_url"])
