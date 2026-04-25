from typing import Any, Mapping

from deps_agentic_ai.domain.model.conversation import Tool

from .parameter_mapper import ParameterMapper

__all__ = ["ToolMapper"]


class ToolMapper:
    @staticmethod
    def from_mapping(tool: Mapping[str, Any]) -> Tool:
        parameters = []
        if parameters_data := tool.get("parameters"):
            parameters = [ParameterMapper.from_mapping(param_data) for param_data in parameters_data]

        return Tool(code=tool["code"], name=tool["name"], parameters=parameters)
