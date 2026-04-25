from datetime import datetime
from uuid import uuid4

import pytest

from deps_agentic_ai.domain.exceptions import CompletionNotFound, InvariantViolation
from deps_agentic_ai.domain.model.conversation import (
    AgentResponse,
    AgentResponseType,
    ArgumentData,
    Completion,
    Parameter,
    Question,
    Tool,
    ToolSet,
)


def test_add_question_builds_context_bundle_with_empty_history(
    test_conversation_1,
    test_agent_vendor_active,
    test_raw_arguments_1,
):
    agent_request = test_conversation_1.add_question(
        question="What is the weather?",
        arguments=test_raw_arguments_1,
        agent_vendor_base_url=test_agent_vendor_active.connection_parameters.base_url,
    )

    assert agent_request.context_bundle == {"conversationTrim": []}
    assert agent_request.conversation_id == test_conversation_1.id()
    assert agent_request.question == "What is the weather?"
    assert agent_request.completion_id is not None


def test_add_question_builds_context_bundle_with_history(
    test_conversation_1_with_completed_completions,
    test_agent_vendor_active,
    test_raw_arguments_1,
):
    agent_request = test_conversation_1_with_completed_completions.add_question(
        question="What is the weather?",
        arguments=test_raw_arguments_1,
        agent_vendor_base_url=test_agent_vendor_active.connection_parameters.base_url,
    )
    assert agent_request.context_bundle == {
        "conversationTrim": [
            {
                "question": comp.question.text,
                "answer": comp.answer.text,
            }
            for comp in test_conversation_1_with_completed_completions.completed_completions
        ]
    }
    assert agent_request.conversation_id == test_conversation_1_with_completed_completions.id()
    assert agent_request.question == "What is the weather?"
    assert agent_request.completion_id is not None


def test_add_question_builds_context_bundle_with_history_and_trim_limit(
    test_conversation_1_with_completed_completions, test_agent_vendor_active, test_raw_arguments_1
):
    agent_request = test_conversation_1_with_completed_completions.add_question(
        question="What is the weather?",
        arguments=test_raw_arguments_1,
        agent_vendor_base_url=test_agent_vendor_active.connection_parameters.base_url,
        completion_trim_size=2,
    )
    assert agent_request.context_bundle == {
        "conversationTrim": [
            {
                "question": comp.question.text,
                "answer": comp.answer.text,
            }
            for comp in test_conversation_1_with_completed_completions.completed_completions[-2:]
        ]
    }
    assert agent_request.conversation_id == test_conversation_1_with_completed_completions.id()
    assert agent_request.question == "What is the weather?"
    assert agent_request.completion_id is not None


def test_add_question_completion_not_completed__error(
    test_conversation_1_with_completed_completions, test_agent_vendor_active, test_raw_arguments_1
):
    test_conversation_1_with_completed_completions.completions.append(
        Completion(
            id_=uuid4().hex,
            question=Question(text="What is the weather?", created_at=datetime.now()),
            execution_context=[],
            answer=None,
        )
    )
    with pytest.raises(InvariantViolation) as e:
        test_conversation_1_with_completed_completions.add_question(
            question="What is the weather?",
            arguments=test_raw_arguments_1,
            agent_vendor_base_url=test_agent_vendor_active.connection_parameters.base_url,
        )
    assert e.value.args[0] == "Question cannot be added. Last completion has not completed yet."


def test_add_final_agent_response(
    test_conversation_1_with_completed_completions,
):
    test_conversation_1_with_completed_completions.completions.append(
        Completion(
            id_=uuid4().hex,
            question=Question(text="What is the weather?", created_at=datetime.now()),
            execution_context=[],
            answer=None,
        )
    )
    expected_answer = "It is sunny"
    test_conversation_1_with_completed_completions.add_agent_response(
        AgentResponse(
            type=AgentResponseType.FINAL,
            text=expected_answer,
        )
    )

    assert test_conversation_1_with_completed_completions.last_completion.answer.text == expected_answer
    assert test_conversation_1_with_completed_completions.last_completion.execution_context == []


@pytest.mark.parametrize(
    "agent_response_type",
    [AgentResponseType.TOOL_CALL, AgentResponseType.REASONING, AgentResponseType.TOOL_CALL_RESPONSE],
)
def test_add_execution_context_agent_response(
    agent_response_type,
    test_conversation_1_with_completed_completions,
):
    test_conversation_1_with_completed_completions.completions.append(
        Completion(
            id_=uuid4().hex,
            question=Question(text="What is the weather?", created_at=datetime.now()),
            execution_context=[],
            answer=None,
        )
    )
    expected_answer = uuid4().hex
    test_conversation_1_with_completed_completions.add_agent_response(
        AgentResponse(
            type=agent_response_type,
            text=expected_answer,
        )
    )

    assert test_conversation_1_with_completed_completions.last_completion.answer is None
    assert test_conversation_1_with_completed_completions.last_completion.execution_context[-1].text == expected_answer


@pytest.mark.parametrize(
    "agent_response_type",
    [AgentResponseType.TOOL_CALL, AgentResponseType.REASONING, AgentResponseType.TOOL_CALL_RESPONSE],
)
def test_add_agent_response_all_completions_completed__error(
    agent_response_type,
    test_conversation_1_with_completed_completions,
):
    with pytest.raises(InvariantViolation) as e:
        test_conversation_1_with_completed_completions.add_agent_response(
            AgentResponse(
                type=agent_response_type,
                text=uuid4().hex,
            )
        )
    assert e.value.args[0] == "Agent response cannot be added. Last completion is completed."


@pytest.mark.parametrize(
    "agent_response_type",
    [AgentResponseType.TOOL_CALL, AgentResponseType.REASONING, AgentResponseType.TOOL_CALL_RESPONSE],
)
def test_add_agent_response_no_completion__error(agent_response_type, test_conversation_1):
    with pytest.raises(InvariantViolation) as e:
        test_conversation_1.add_agent_response(
            AgentResponse(
                type=agent_response_type,
                text=uuid4().hex,
            )
        )
    assert e.value.args[0] == "Agent response cannot be added. Completion is not exists."


def test_add_question_with_new_tool_set__context_merged(
    test_conversation_1, test_agent_vendor_active, test_tool_set_3, test_tool_set_3_code
):
    assert test_tool_set_3_code not in test_conversation_1.context.tools
    test_conversation_1.mode.tool_sets[test_tool_set_3.code] = ToolSet(
        id_=test_tool_set_3.id(),
        code=test_tool_set_3.code,
        name=test_tool_set_3.name,
        tools=[
            Tool(code=tool.code, name=tool.name, parameters=[Parameter(name=param.name) for param in tool.parameters])
            for tool in test_tool_set_3.tools
        ],
    )

    raw_arguments = {
        test_tool_set_3_code: {
            tool.code: [ArgumentData(parameter=param.name, value=uuid4().hex) for param in tool.parameters]
            for tool in test_tool_set_3.tools
        }
    }
    agent_request = test_conversation_1.add_question(
        question="What is the weather?",
        arguments=raw_arguments,
        agent_vendor_base_url=test_agent_vendor_active.connection_parameters.base_url,
    )
    assert test_tool_set_3_code in agent_request.context["tools"]


def test_add_question_with_new_tool__context_merged(
    test_conversation_1, test_agent_vendor_active, test_tool_set_2_code
):
    new_param = Parameter(name="new_param")
    new_tool = Tool(code="new_tool", name="NewTool", parameters=[new_param])

    test_conversation_1.mode.tool_sets[test_tool_set_2_code].tools[new_tool.code] = new_tool

    raw_arguments = {test_tool_set_2_code: {new_tool.code: [ArgumentData(parameter=new_param.name, value=uuid4().hex)]}}
    agent_request = test_conversation_1.add_question(
        question="What is the weather?",
        arguments=raw_arguments,
        agent_vendor_base_url=test_agent_vendor_active.connection_parameters.base_url,
    )

    assert new_tool.code in [tool["code"] for tool in agent_request.context["tools"][test_tool_set_2_code]]


def test_add_question_with_new_parameter__context_merged(
    test_conversation_1, test_agent_vendor_active, test_tool_set_2_code
):
    new_param = Parameter(name="new_param")

    expected_tool_code = list(test_conversation_1.mode.tool_sets[test_tool_set_2_code].tools.keys())[0]

    test_conversation_1.mode.tool_sets[test_tool_set_2_code].tools[expected_tool_code].parameters.append(new_param)
    test_conversation_1.mode.tool_sets[test_tool_set_2_code].tools[expected_tool_code].parameter_names.add(
        new_param.name
    )

    raw_arguments = {
        test_tool_set_2_code: {expected_tool_code: [ArgumentData(parameter=new_param.name, value=uuid4().hex)]}
    }
    agent_request = test_conversation_1.add_question(
        question="What is the weather?",
        arguments=raw_arguments,
        agent_vendor_base_url=test_agent_vendor_active.connection_parameters.base_url,
    )
    needed_tool = next(
        filter(lambda tool: tool["code"] == expected_tool_code, agent_request.context["tools"][test_tool_set_2_code])
    )
    assert new_param.name in [param["parameter"] for param in needed_tool["arguments"]]


def test_sanitize_context__tool_set_not_changed__no_changes(
    test_conversation_1,
):
    initial_context = test_conversation_1.context
    sanitized_context = test_conversation_1.mode.sanitize_context(initial_context)

    assert sanitized_context == initial_context


def test_sanitize_context__tool_set_removed__context_changed(test_conversation_1, test_tool_set_2_code):
    initial_context = test_conversation_1.context
    assert test_tool_set_2_code in initial_context.tools

    test_conversation_1.mode.tool_sets.pop(test_tool_set_2_code)

    sanitized_context = test_conversation_1.mode.sanitize_context(initial_context)

    assert test_tool_set_2_code not in sanitized_context.tools


def test_sanitize_context__tool_removed__context_changed(test_conversation_1, test_tool_set_2_code):
    initial_context = test_conversation_1.context
    removed_tool_code = list(test_conversation_1.mode.tool_sets[test_tool_set_2_code].tools.keys())[0]
    assert removed_tool_code in (active_tool.code for active_tool in initial_context.tools[test_tool_set_2_code])

    test_conversation_1.mode.tool_sets[test_tool_set_2_code].tools.pop(removed_tool_code)

    sanitized_context = test_conversation_1.mode.sanitize_context(initial_context)

    assert removed_tool_code not in (active_tool.code for active_tool in sanitized_context.tools[test_tool_set_2_code])


def test_sanitize_context__parameter_removed__context_changed(test_conversation_1, test_tool_set_2_code):
    initial_context = test_conversation_1.context
    target_tool_code = list(test_conversation_1.mode.tool_sets[test_tool_set_2_code].tools.keys())[0]
    removed_argument_name = (
        test_conversation_1.mode.tool_sets[test_tool_set_2_code].tools[target_tool_code].parameters[0].name
    )
    assert removed_argument_name in (
        active_tool.arguments[0].name for active_tool in initial_context.tools[test_tool_set_2_code]
    )

    test_conversation_1.mode.tool_sets[test_tool_set_2_code].tools[target_tool_code].parameters.pop(0)
    test_conversation_1.mode.tool_sets[test_tool_set_2_code].tools[target_tool_code].__dict__.pop("parameter_names")
    sanitized_context = test_conversation_1.mode.sanitize_context(initial_context)

    assert removed_argument_name not in [
        active_tool.arguments[0].name for active_tool in sanitized_context.tools[test_tool_set_2_code]
    ]


def test_edit_question__question_edited_and_all_further_completions_removed(
    test_conversation_1_with_completions, test_agent_vendor_active
):
    initial_completions_number = len(test_conversation_1_with_completions.completions)
    completion_to_edit_question_id = test_conversation_1_with_completions.completions[-3].id()
    completions_to_remove = [
        test_conversation_1_with_completions.completions[-1],
        test_conversation_1_with_completions.completions[-2],
    ]
    new_question = "New question"

    test_conversation_1_with_completions.edit_question(
        completion_id=completion_to_edit_question_id,
        new_text=new_question,
        new_arguments={},
        agent_vendor_base_url=test_agent_vendor_active.connection_parameters.base_url,
    )

    assert len(test_conversation_1_with_completions.completions) == initial_completions_number - 2
    assert test_conversation_1_with_completions.completions[-1].id() == completion_to_edit_question_id
    assert test_conversation_1_with_completions.completions[-1].question.text == new_question
    assert (
        test_conversation_1_with_completions.completions[-1].question.created_at
        == test_conversation_1_with_completions.updated_at
    )


def test_edit_question__completion_doesnt_exist__raise_error(
    test_conversation_1_with_completions, test_agent_vendor_active
):
    with pytest.raises(CompletionNotFound):
        test_conversation_1_with_completions.edit_question(
            completion_id="non_existing_completion_id",
            new_text="New question",
            new_arguments={},
            agent_vendor_base_url=test_agent_vendor_active.connection_parameters.base_url,
        )
