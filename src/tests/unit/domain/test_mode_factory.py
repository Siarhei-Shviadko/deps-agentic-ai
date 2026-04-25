from deps_agentic_ai.domain.model.mode import ModeFactory


def test_create(test_tool_set_1, test_tool_set_2):
    code = "M"
    tool_sets = [test_tool_set_1.to_data(), test_tool_set_2.to_data()]

    mode = ModeFactory.create(code, tool_sets)

    assert mode.code == code
    assert len(mode.tool_sets) == len(tool_sets)

    for tool_set, tool_set_data in zip(mode.tool_sets.values(), tool_sets):
        assert tool_set.to_data() == tool_set_data
