from datetime import datetime

from pydantic import Field

from deps_agentic_ai.domain.model.conversation import Question, QuestionInfo

from ....configured_base_serializer import ConfiguredResponseSerializer

__all__ = ["QuestionSerializer"]


class QuestionSerializer(ConfiguredResponseSerializer):
    text: str
    created_at: datetime = Field(..., alias="createdAt")

    @classmethod
    def from_domain(cls, question: Question) -> "QuestionSerializer":
        return cls(text=question.text, created_at=question.created_at)

    @classmethod
    def from_info(cls, question: QuestionInfo) -> "QuestionSerializer":
        return cls(
            text=question["text"],
            created_at=question["created_at"],
        )
