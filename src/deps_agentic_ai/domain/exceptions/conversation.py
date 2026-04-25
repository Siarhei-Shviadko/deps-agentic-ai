from .base import AgenticAiException, NotFound

__all__ = ["ConversationContextError", "ConversationNotFound"]


class ConversationContextError(AgenticAiException):
    code = "conversation_context_error"


class ConversationNotFound(NotFound):
    code = "conversation_not_found"

    def __init__(self, id: str) -> None:
        super().__init__(f"Conversation with id `{id}` not found.")
