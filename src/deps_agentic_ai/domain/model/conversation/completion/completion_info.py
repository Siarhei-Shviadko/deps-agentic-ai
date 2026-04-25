from datetime import datetime
from typing import TypedDict

__all__ = [
    "QuestionInfo",
    "ExecutionContextInfo",
    "AnswerInfo",
    "CompletionInfo",
]


class QuestionInfo(TypedDict):
    text: str
    created_at: datetime


class ExecutionContextInfo(TypedDict):
    text: str


class AnswerInfo(TypedDict):
    text: str
    created_at: datetime


class CompletionInfo(TypedDict):
    id: str
    question: QuestionInfo
    execution_context: list[ExecutionContextInfo]
    answer: AnswerInfo | None
