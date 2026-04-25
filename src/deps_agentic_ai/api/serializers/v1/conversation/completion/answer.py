from datetime import datetime

from pydantic import Field

from deps_agentic_ai.domain.model.conversation import Answer, AnswerInfo

from ....configured_base_serializer import ConfiguredResponseSerializer

__all__ = ["AnswerSerializer"]


class AnswerSerializer(ConfiguredResponseSerializer):
    text: str
    created_at: datetime = Field(..., alias="createdAt")

    @classmethod
    def from_domain(cls, answer: Answer) -> "AnswerSerializer":
        return cls(text=answer.text, createdAt=answer.created_at)

    @classmethod
    def from_info(cls, answer: AnswerInfo) -> "AnswerSerializer":
        return cls(text=answer["text"], createdAt=answer["created_at"])
