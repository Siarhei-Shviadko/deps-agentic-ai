from typing import Any, TypedDict

__all__ = ["ArgumentData"]


class ArgumentData(TypedDict):
    parameter: str
    value: Any
