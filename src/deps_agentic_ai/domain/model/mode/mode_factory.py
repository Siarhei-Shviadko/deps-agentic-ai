from datetime import datetime, timezone
from uuid import uuid4

from ..tool_set import ToolSetData
from .mode import Mode
from .tool_set import ToolSet

__all__ = ["ModeFactory"]


class ModeFactory:
    @staticmethod
    def create(code: str, tool_sets: list[ToolSetData]) -> Mode:
        id_ = uuid4().hex

        return Mode(
            id_=id_,
            code=code,
            tool_sets=[ToolSet.from_data(ts) for ts in tool_sets],
            created_at=datetime.now(timezone.utc),
            events=[],
        )
