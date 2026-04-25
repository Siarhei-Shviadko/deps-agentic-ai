from .base import IllegalArgument, NotFound

__all__ = ["ToolSetNotFound", "ToolSetsNotFound", "ToolCodeIsNotUnique", "ParameterNameIsNotUnique"]


class ToolSetNotFound(NotFound):
    code = "tool_set_not_found"

    def __init__(self, tool_set_id: str | None = None, tool_set_code: str | None = None) -> None:
        if tool_set_id is not None:
            message = f"Tool set with id `{tool_set_id}` not found."
        elif tool_set_code is not None:
            message = f"Tool set with code `{tool_set_code}` not found."
        else:
            message = "Tool set not found."

        super().__init__(message)


class ToolSetsNotFound(NotFound):
    code = "tool_sets_not_found"

    def __init__(self, tool_set_ids: set[str]) -> None:
        super().__init__(f"Tool sets with ids `{tool_set_ids}` not found.")


class ToolCodeIsNotUnique(IllegalArgument):
    code = "tool_code_is_not_unique"

    def __init__(self, tool_code: str) -> None:
        super().__init__(f"Tool code `{tool_code}` is not unique within the tool set.")


class ParameterNameIsNotUnique(IllegalArgument):
    code = "parameter_name_is_not_unique"

    def __init__(self, parameter_name: str, tool_code: str) -> None:
        super().__init__(f"Parameter name `{parameter_name}` is not unique within the tool `{tool_code}`.")
