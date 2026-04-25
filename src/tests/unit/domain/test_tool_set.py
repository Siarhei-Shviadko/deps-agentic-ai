import pytest

from deps_agentic_ai.domain.exceptions import (
    ParameterNameIsNotUnique,
    ToolCodeIsNotUnique,
)
from deps_agentic_ai.domain.model.tool_set import ParameterData, Tool, ToolData


def test_update(test_tool_set_1):
    new_name = "NEW TS"
    new_tools = [
        ToolData(
            code="new_t1",
            name="new_T1",
            parameters=[
                ParameterData(name="new_p11"),
                ParameterData(name="new_p12"),
            ],
        ),
        ToolData(
            code="new_t2",
            name="new_T2",
            parameters=[
                ParameterData(name="new_p21"),
                ParameterData(name="new_p22"),
            ],
        ),
    ]

    test_tool_set_1.update(
        name=new_name,
        tools=new_tools,
    )

    assert test_tool_set_1.name == new_name
    assert test_tool_set_1.tools == [Tool.from_data(td) for td in new_tools]


def test_update__tool_code_is_not_unique(test_tool_set_1):
    new_name = "NEW TS"
    new_tools = [
        ToolData(
            code="new_t1",
            name="new_T1",
            parameters=[
                ParameterData(name="new_p11"),
                ParameterData(name="new_p12"),
            ],
        ),
        ToolData(
            code="new_t1",
            name="new_T2",
            parameters=[
                ParameterData(name="new_p21"),
                ParameterData(name="new_p22"),
            ],
        ),
    ]

    with pytest.raises(ToolCodeIsNotUnique):
        test_tool_set_1.update(
            name=new_name,
            tools=new_tools,
        )


def test_update__parameter_name_is_not_unique(test_tool_set_1):
    new_name = "NEW TS"
    new_tools = [
        ToolData(
            code="new_t1",
            name="new_T1",
            parameters=[
                ParameterData(name="new_p11"),
                ParameterData(name="new_p12"),
            ],
        ),
        ToolData(
            code="new_t2",
            name="new_T2",
            parameters=[
                ParameterData(name="new_p21"),
                ParameterData(name="new_p21"),
            ],
        ),
    ]

    with pytest.raises(ParameterNameIsNotUnique):
        test_tool_set_1.update(
            name=new_name,
            tools=new_tools,
        )
