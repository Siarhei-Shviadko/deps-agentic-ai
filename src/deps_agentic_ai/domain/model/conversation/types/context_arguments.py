from typing import TypeAlias

from ...shared import ToolCode, ToolSetCode
from .argument_data import ArgumentData

__all__ = ["ContextArguments", "ToolsDict"]

ToolsDict: TypeAlias = dict[ToolCode, list[ArgumentData]]
ContextArguments: TypeAlias = dict[ToolSetCode, ToolsDict]
