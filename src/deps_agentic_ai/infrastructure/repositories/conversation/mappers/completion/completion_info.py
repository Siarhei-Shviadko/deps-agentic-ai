from datetime import datetime
from typing import Any

from deps_agentic_ai.domain.model.conversation import (
    AnswerInfo,
    CompletionInfo,
    ExecutionContextInfo,
    QuestionInfo,
)

__all__ = ["CompletionInfoMapper"]


class CompletionInfoMapper:
    @staticmethod
    def from_mapping(row: Any) -> CompletionInfo:
        question = row["question"]
        answer = row.get("answer")
        return CompletionInfo(
            id=row["id"],
            question=QuestionInfo(
                text=question["text"],
                created_at=datetime.fromisoformat(question["created_at"]),
            ),
            execution_context=[ExecutionContextInfo(text=ctx["text"]) for ctx in row["execution_context"]],
            answer=(
                AnswerInfo(
                    text=answer["text"],
                    created_at=datetime.fromisoformat(answer["created_at"]),
                )
                if answer is not None
                else None
            ),
        )
