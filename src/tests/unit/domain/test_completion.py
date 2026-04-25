from datetime import datetime, timezone

import pytest

from deps_agentic_ai.domain.exceptions import InvariantViolation


def test_completion_add_answer__added_answer(test_completion_without_answer):
    expected_answer = "Test Answer"
    test_completion_without_answer.add_answer(expected_answer)

    assert test_completion_without_answer.answer.text == expected_answer
    assert test_completion_without_answer.answer.created_at is not None


def test_completion_add_answer__answer_already_exists_error(test_completion_with_answer):
    with pytest.raises(InvariantViolation) as e:
        test_completion_with_answer.add_answer("Test Answer")

    assert e.value.args[0] == "Answer cannot be added. Answer already exists."


def test_edit_question__edited(test_completion_with_answer):
    text = "New user question"
    created_at = datetime.now(timezone.utc)
    test_completion_with_answer.edit_question(text=text, created_at=created_at)

    assert test_completion_with_answer.question.text == text
    assert test_completion_with_answer.question.created_at == created_at
    assert test_completion_with_answer.execution_context == []
    assert test_completion_with_answer.answer is None
