from datetime import datetime
from uuid import uuid4

import pytest

from deps_agentic_ai.domain.model.conversation import Answer, Completion, Question


@pytest.fixture
def test_completion_without_answer():
    return Completion(
        id_=uuid4().hex,
        question=Question(text="Test Question", created_at=datetime.now()),
        execution_context=[],
        answer=None,
    )


@pytest.fixture
def test_completion_with_answer():
    return Completion(
        id_=uuid4().hex,
        question=Question(text="Test Question", created_at=datetime.now()),
        execution_context=[],
        answer=Answer(text="Test Answer", created_at=datetime.now()),
    )
