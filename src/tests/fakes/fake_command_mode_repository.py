from deps_agentic_ai.domain.model.mode import ICommandModeRepository, Mode, ModeData

__all__ = ["FakeCommandModeRepository"]


class FakeCommandModeRepository(ICommandModeRepository):
    def __init__(self, modes: list[Mode] | None = None) -> None:
        self._db = {m.id(): m for m in modes} if modes else {}

    async def has_mode_with_code(self, code: str) -> bool:
        for m in self._db.values():
            if m.code == code:
                return True

        return False

    async def save(self, mode: Mode) -> None:
        self._db[mode.id()] = mode

    async def mode_of_id_data(self, id_: str) -> ModeData | None:
        mode = self._db.get(id_)

        return mode.to_data() if mode else None

    async def modes_of_ids(self, ids: list[str]) -> list[Mode]:
        modes = []

        for id_ in ids:
            if mode := self._db.get(id_):
                modes.append(mode)

        return modes

    async def mode_of_id(self, id_: str) -> Mode | None:
        return self._db.get(id_)

    async def delete_all(self, modes: list[Mode]) -> None:
        for m in modes:
            if m.id() in self._db:
                del self._db[m.id()]

    async def erase_all(self) -> None:
        self._db.clear()
