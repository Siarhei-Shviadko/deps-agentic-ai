from datetime import datetime
from typing import Any, Mapping

from deps_agentic_ai.domain.model.conversation import Answer

__all__ = ["AnswerMapper"]


class AnswerMapper:
    @staticmethod
    def from_mapping(answer: Mapping[str, Any]) -> Answer:
        return Answer(
            text=answer["text"],
            created_at=datetime.fromisoformat(answer["created_at"]),
        )

    @staticmethod
    def to_dict(answer: Answer) -> dict[str, Any]:
        return {
            "text": answer.text,
            "created_at": answer.created_at.isoformat(),
        }
