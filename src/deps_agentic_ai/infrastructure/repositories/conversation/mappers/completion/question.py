from datetime import datetime
from typing import Any, Mapping

from deps_agentic_ai.domain.model.conversation import Question

__all__ = ["QuestionMapper"]


class QuestionMapper:
    @staticmethod
    def from_mapping(question: Mapping[str, Any]) -> Question:
        return Question(
            text=question["text"],
            created_at=datetime.fromisoformat(question["created_at"]),
        )

    @staticmethod
    def to_dict(question: Question) -> dict[str, Any]:
        return {
            "text": question.text,
            "created_at": question.created_at.isoformat(),
        }
