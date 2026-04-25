from datetime import datetime

from ..shared import Entity, EntityId, Event, Guard, ImmutableCheck, LengthCheck
from ..tool_set import ToolSetData
from .mode_data import ModeData
from .mode_deleted import ModeDeleted
from .tool_set import ToolSet

__all__ = ["Mode", "MIN_MODE_TOOL_SETS_COUNT", "MIN_MODE_CODE_LENGTH"]


MIN_MODE_TOOL_SETS_COUNT = 0
MIN_MODE_CODE_LENGTH = 1


class Mode(metaclass=Entity):
    id = Guard[EntityId](EntityId, ImmutableCheck())
    code = Guard[str](str, LengthCheck(min_length=MIN_MODE_CODE_LENGTH))
    tool_sets = Guard[dict[str, ToolSet]](dict, ImmutableCheck(), LengthCheck(min_length=MIN_MODE_TOOL_SETS_COUNT))
    created_at = Guard[datetime](datetime, ImmutableCheck())

    def __init__(
        self,
        id_: str,
        code: str,
        tool_sets: list[ToolSet],
        created_at: datetime,
        *,
        events: list[Event] | None = None,
    ) -> None:
        self.id = EntityId(id_)
        self.code = code
        self.tool_sets = {ts.id(): ts for ts in tool_sets}
        self.created_at = created_at

        self.events = events or []

    @property
    def tool_set_ids(self) -> set[str]:
        return set(self.tool_sets.keys())

    def update_code(self, code: str) -> None:
        self.code = code

    def update_tool_sets(self, add: list[ToolSetData], remove: list[str]) -> None:
        self._remove_tool_sets(remove)
        self._add_tool_sets(add)

    def delete(self) -> None:
        self.events.append(ModeDeleted(id=self.id()))

    def to_data(self) -> ModeData:
        return ModeData(id=self.id(), code=self.code, tool_sets=[ts.to_data() for ts in self.tool_sets.values()])

    def _remove_tool_sets(self, ids: list[str]) -> None:
        for tool_set_id in ids:
            if tool_set_id in self.tool_sets:
                del self.tool_sets[tool_set_id]

    def _add_tool_sets(self, tool_sets: list[ToolSetData]) -> None:
        for tool_set in tool_sets:
            self.tool_sets[tool_set["id"]] = ToolSet.from_data(tool_set)
