from datetime import datetime, timezone
from uuid import uuid4

from .tool import Tool
from .tool_data import ToolData
from .tool_set import ToolSet

__all__ = ["ToolSetFactory"]


class ToolSetFactory:
    @staticmethod
    def create(code: str, name: str, tools: list[ToolData]) -> ToolSet:
        id_ = uuid4().hex

        return ToolSet(
            id_=id_,
            name=name,
            code=code,
            tools=[Tool.from_data(t) for t in tools],
            created_at=datetime.now(timezone.utc),
            events=[],
        )
