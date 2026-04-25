import logging
from typing import TypeAlias

from ....exceptions import ConversationContextError
from ...shared import Guard, ImmutableCheck, ToolCode, ToolSetCode, ValueObject
from ..types import ArgumentData
from .active_tool import ActiveTool
from .argument import Argument
from .context import Context
from .tool import Tool
from .tool_set import ToolSet

__all__ = ["Mode", "ContextArguments"]

ToolsDict: TypeAlias = dict[ToolCode, list[ArgumentData]]
ContextArguments: TypeAlias = dict[ToolSetCode, ToolsDict]


class Mode(metaclass=ValueObject):
    id = Guard[str](str, ImmutableCheck())
    code = Guard[str](str, ImmutableCheck())
    tool_sets = Guard[dict[ToolSetCode, ToolSet]](dict, ImmutableCheck())

    def __init__(self, id_: str, code: str, tool_sets: list[ToolSet]) -> None:
        self.id = id_
        self.code = code
        self.tool_sets = {ts.code: ts for ts in tool_sets}

    def has_tool_set(self, tool_set_code: str) -> bool:
        return tool_set_code in self.tool_sets

    def validate_arguments(self, arguments: ContextArguments) -> None:
        self._context_validator(self, arguments).validate()

    def create_context(self, arguments: ContextArguments) -> Context:
        self.validate_arguments(arguments)
        return self._mapping_to_context(arguments)

    def merge_context(self, existing_context: Context, new_arguments: ContextArguments) -> Context:
        self.validate_arguments(new_arguments)

        merged_tools = self._context_to_mapping(existing_context)

        for tool_set_code, tools_dict in new_arguments.items():
            if tool_set_code not in merged_tools:
                merged_tools[tool_set_code] = {}

            tool_set_dict = merged_tools[tool_set_code]

            for tool_code, new_args in tools_dict.items():
                if tool_code not in tool_set_dict:
                    tool_set_dict[tool_code] = new_args
                else:
                    existing_args = tool_set_dict[tool_code]
                    existing_params = {arg["parameter"]: arg for arg in existing_args}

                    for new_arg in new_args:
                        existing_params[new_arg["parameter"]] = new_arg  # noqa: WPS220

                    tool_set_dict[tool_code] = list(existing_params.values())

        return self._mapping_to_context(merged_tools)

    def sanitize_context(self, context: Context) -> Context:  # noqa: WPS231
        mapping = self._context_to_mapping(context)
        sanitized_mapping: ContextArguments = {}

        for tool_set_code, tools_dict in mapping.items():
            if not self.has_tool_set(tool_set_code):
                continue

            tool_set = self.tool_sets[tool_set_code]
            sanitized_mapping[tool_set_code] = {}

            for tool_code, arguments in tools_dict.items():
                if not tool_set.has_tool(tool_code):
                    continue

                tool = tool_set.tools[tool_code]

                valid_arguments = [arg for arg in arguments if tool.has_parameter(arg["parameter"])]

                if valid_arguments:
                    sanitized_mapping[tool_set_code][tool_code] = valid_arguments

        sanitized_mapping = {ts_code: td for ts_code, td in sanitized_mapping.items() if mapping.values()}

        if not sanitized_mapping:
            return Context(tools={})

        return self._mapping_to_context(sanitized_mapping)

    def _context_to_mapping(self, context: Context) -> ContextArguments:
        mapping: ContextArguments = {}

        for tool_set_code, active_tools in context.tools.items():
            mapping[tool_set_code] = {}
            for active_tool in active_tools:
                mapping[tool_set_code][active_tool.code] = [
                    ArgumentData(parameter=arg.name, value=arg.value) for arg in active_tool.arguments
                ]

        return mapping

    def _mapping_to_context(self, mapping: ContextArguments) -> Context:
        tools = {}
        for tool_set_code, tools_dict in mapping.items():
            active_tools = []
            for tool_code, args_data in tools_dict.items():
                arguments_list = [Argument.from_data(data) for data in args_data]
                active_tools.append(ActiveTool(code=tool_code, arguments=arguments_list))
            tools[tool_set_code] = active_tools

        return Context(tools=tools)

    class _context_validator:
        def __init__(self, mode: "Mode", arguments: ContextArguments) -> None:
            self._mode = mode
            self._arguments = arguments
            self._logger = logging.getLogger(self.__class__.__name__)

        def validate(self) -> None:
            for tool_set_code in self._arguments:
                self._validate_toolset(tool_set_code)
                self._validate_tools(tool_set_code, self._arguments[tool_set_code])

        def _validate_toolset(self, tool_set_code: str) -> None:
            if not self._mode.has_tool_set(tool_set_code):
                self._raise_error(f"Tool set {tool_set_code} not found in mode {self._mode.code}")

        def _validate_tools(self, tool_set_code: str, tools: ToolsDict) -> None:
            tool_set = self._mode.tool_sets[tool_set_code]

            for tool_code in tools:
                self._validate_tool(tool_set, tool_code)
                self._validate_parameters(tool_set.tools[tool_code], tools[tool_code])

        def _validate_tool(self, tool_set: ToolSet, tool_code: str) -> None:
            if not tool_set.has_tool(tool_code):
                self._raise_error(f"Tool {tool_code} not found in tool set {tool_set.code}")

        def _validate_parameters(self, tool: Tool, parameters: list[ArgumentData]) -> None:
            for parameter in parameters:
                parameter_name = parameter["parameter"]
                if not tool.has_parameter(parameter_name):
                    self._raise_error(f"Parameter {parameter_name} not found in tool {tool.code}")

        def _raise_error(self, message: str) -> None:
            self._logger.error("Cannot create conversation context: %s", message)
            raise ConversationContextError(message)
