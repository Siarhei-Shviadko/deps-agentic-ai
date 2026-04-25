from .base import AlreadyExists, NotFound

__all__ = ["ModeAlreadyExists", "ModeNotFound"]


class ModeAlreadyExists(AlreadyExists):
    code = "mode_already_exists"

    def __init__(self, mode_code: str) -> None:
        super().__init__(f"Mode with code `{mode_code}` already exists.")


class ModeNotFound(NotFound):
    code = "mode_not_found"

    def __init__(self, mode_id: str) -> None:
        super().__init__(f"Mode with id `{mode_id}` not found.")
