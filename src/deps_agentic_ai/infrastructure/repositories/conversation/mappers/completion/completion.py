from typing import Any, Mapping

from deps_agentic_ai.domain.model.conversation import Completion, ExecutionContext

from .answer import AnswerMapper
from .question import QuestionMapper

__all__ = ["CompletionMapper"]


class CompletionMapper:
    @staticmethod
    def from_mapping(completion: Mapping[str, Any]) -> Completion:
        return Completion(
            id_=completion["id"],
            question=QuestionMapper.from_mapping(completion["question"]),
            execution_context=[
                ExecutionContext(text=exc_context["text"]) for exc_context in completion["execution_context"]
            ],
            answer=AnswerMapper.from_mapping(completion["answer"]) if completion["answer"] is not None else None,
        )

    @staticmethod
    def to_dict(conversation_id: str, completion: Completion) -> dict[str, Any]:
        return {
            "conversation_id": conversation_id,
            "id": completion.id(),
            "question": QuestionMapper.to_dict(completion.question),
            "execution_context": [{"text": exc_context.text} for exc_context in completion.execution_context],
            "answer": AnswerMapper.to_dict(completion.answer) if completion.answer else None,
            "created_at": completion.question.created_at,
        }
