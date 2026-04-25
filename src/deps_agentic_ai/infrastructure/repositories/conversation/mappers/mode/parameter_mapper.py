from typing import Any, Mapping

from deps_agentic_ai.domain.model.conversation import Parameter

__all__ = ["ParameterMapper"]


class ParameterMapper:
    @staticmethod
    def from_mapping(parameter: Mapping[str, Any]) -> Parameter:
        return Parameter(name=parameter["name"])
