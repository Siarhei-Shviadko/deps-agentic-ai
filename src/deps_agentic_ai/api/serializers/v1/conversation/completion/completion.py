from pydantic import Field

from deps_agentic_ai.domain.model.conversation import Completion, CompletionInfo

from ....configured_base_serializer import ConfiguredResponseSerializer
from .answer import AnswerSerializer
from .execution_context import ExecutionContextSerializer
from .question import QuestionSerializer

__all__ = ["CompletionSerializer"]


class CompletionSerializer(ConfiguredResponseSerializer):
    id: str
    question: QuestionSerializer
    execution_context: list[ExecutionContextSerializer] = Field(default_factory=list, alias="executionContext")
    answer: AnswerSerializer | None = None

    @classmethod
    def from_domain(cls, completion: Completion) -> "CompletionSerializer":
        return cls(
            id=completion.id(),
            question=QuestionSerializer.from_domain(completion.question),
            answer=AnswerSerializer.from_domain(completion.answer) if completion.answer else None,
            execution_context=[
                ExecutionContextSerializer(text=execution_context.text)
                for execution_context in completion.execution_context
            ],
        )

    @classmethod
    def from_info(cls, completion: CompletionInfo) -> "CompletionSerializer":
        return cls(
            id=completion["id"],
            question=QuestionSerializer.from_info(completion["question"]),
            execution_context=[
                ExecutionContextSerializer.from_info(execution_context)
                for execution_context in completion["execution_context"]
            ],
            answer=AnswerSerializer.from_info(completion["answer"]) if completion["answer"] else None,
        )
