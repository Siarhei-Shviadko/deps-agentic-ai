import pytest

from deps_agentic_ai.domain.exceptions import (
    ParameterNameIsNotUnique,
    ToolCodeIsNotUnique,
)
from deps_agentic_ai.domain.model.tool_set import (
    ParameterData,
    Tool,
    ToolData,
    ToolSetFactory,
)


def test_create():
    name = "TS"
    code = "ts"
    tools = [
        ToolData(
            code="t1",
            name="T1",
            parameters=[
                ParameterData(name="p11"),
                ParameterData(name="p12"),
            ],
        ),
        ToolData(
            code="t2",
            name="T2",
            parameters=[
                ParameterData(name="p21"),
                ParameterData(name="p22"),
            ],
        ),
    ]

    tool_set = ToolSetFactory.create(
        code=code,
        name=name,
        tools=tools,
    )

    assert tool_set.code == code
    assert tool_set.name == name
    assert tool_set.tools == [Tool.from_data(td) for td in tools]


def test_create__tool_code_is_not_unique():
    name = "TS"
    code = "ts"
    tools = [
        ToolData(
            code="t1",
            name="T1",
            parameters=[
                ParameterData(name="p11"),
                ParameterData(name="p12"),
            ],
        ),
        ToolData(
            code="t1",
            name="T2",
            parameters=[
                ParameterData(name="p21"),
                ParameterData(name="p22"),
            ],
        ),
    ]

    with pytest.raises(ToolCodeIsNotUnique):
        ToolSetFactory.create(
            code=code,
            name=name,
            tools=tools,
        )


def test_create__parameter_name_is_not_unique():
    name = "TS"
    code = "ts"
    tools = [
        ToolData(
            code="t1",
            name="T1",
            parameters=[
                ParameterData(name="p11"),
                ParameterData(name="p11"),
            ],
        ),
        ToolData(
            code="t2",
            name="T2",
            parameters=[
                ParameterData(name="p21"),
                ParameterData(name="p22"),
            ],
        ),
    ]

    with pytest.raises(ParameterNameIsNotUnique):
        ToolSetFactory.create(
            code=code,
            name=name,
            tools=tools,
        )
