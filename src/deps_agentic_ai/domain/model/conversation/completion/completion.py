import logging
from datetime import datetime, timezone
from typing import TypeAlias

from ....exceptions import InvariantViolation
from ...shared import Entity, EntityId, Guard, ImmutableCheck, LengthCheck
from .answer import Answer
from .execution_context import ExecutionContext
from .question import Question

__all__ = ["Completion", "MIN_COMPLETION_EXECUTION_CONTEXT_COUNT"]

CompletionId: TypeAlias = EntityId

MIN_COMPLETION_EXECUTION_CONTEXT_COUNT = 0


class Completion(metaclass=Entity):
    id = Guard[CompletionId](CompletionId, ImmutableCheck())
    question = Guard[Question](Question)
    execution_context = Guard[list[ExecutionContext]](
        list,
        LengthCheck(min_length=MIN_COMPLETION_EXECUTION_CONTEXT_COUNT),
    )
    answer = Guard[Answer](Answer)

    def __init__(
        self,
        id_: str,
        question: Question,
        execution_context: list[ExecutionContext],
        answer: Answer | None = None,
    ) -> None:
        self.id = CompletionId(id_)
        self.question = question
        self.execution_context = execution_context

        if answer:
            self.answer = answer

        self._logger = logging.getLogger(self.__class__.__name__)

    def is_completed(self) -> bool:
        return self.answer is not None

    def edit_question(self, text: str, created_at: datetime) -> None:
        self.question = Question(text=text, created_at=created_at)
        self.execution_context = []
        del self.answer

    def add_execution_context(self, execution_context: str) -> None:
        self.execution_context.append(ExecutionContext(text=execution_context))

    def add_answer(self, answer: str) -> None:
        if self.answer:
            raise InvariantViolation("Answer cannot be added. Answer already exists.")

        self.answer = Answer(text=answer, created_at=datetime.now(timezone.utc))

    @classmethod
    def from_question(cls, question: str) -> "Completion":
        raise NotImplementedError()
