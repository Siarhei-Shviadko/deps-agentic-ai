from .base import NotFound

__all__ = ["CompletionNotFound"]


class CompletionNotFound(NotFound):
    code = "completion_not_found"

    def __init__(self, id: str) -> None:
        super().__init__(f"Completion with id `{id}` not found.")
