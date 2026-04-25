from deps_agentic_ai.domain.model.tool_set import (
    ICommandToolSetRepository,
    ToolSet,
    ToolSetData,
)

__all__ = ["FakeCommandToolSetRepository"]


class FakeCommandToolSetRepository(ICommandToolSetRepository):
    def __init__(self, tool_sets: list[ToolSet] | None = None) -> None:
        self._db: dict[str, ToolSet] = {ts.code: ts for ts in tool_sets} if tool_sets else {}

    async def save(self, tool_set: ToolSet) -> None:
        self._db[tool_set.code] = tool_set

    async def tool_set_with_code(self, code: str) -> ToolSet | None:
        return self._db.get(code)

    async def tool_sets_of_ids_data(self, ids: list[str]) -> list[ToolSetData]:
        tool_sets_data = []

        for ts in self._db.values():
            if ts.id() in ids:
                tool_sets_data.append(ts.to_data())

        return tool_sets_data

    async def tool_sets_of_ids(self, ids: list[str]) -> list[ToolSet]:
        tool_sets = []

        for ts in self._db.values():
            if ts.id() in ids:
                tool_sets.append(ts)

        return tool_sets

    async def delete_all(self, tool_sets: list[ToolSet]) -> None:
        ids = {ts.id() for ts in tool_sets}

        for ts in self._db.values():
            if ts.id() in ids:
                del self._db[ts.code]
