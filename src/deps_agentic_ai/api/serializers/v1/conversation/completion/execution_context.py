from deps_agentic_ai.domain.model.conversation import ExecutionContextInfo

from ....configured_base_serializer import ConfiguredResponseSerializer

__all__ = ["ExecutionContextSerializer"]


class ExecutionContextSerializer(ConfiguredResponseSerializer):
    text: str

    @classmethod
    def from_info(cls, execution_context: ExecutionContextInfo) -> "ExecutionContextSerializer":
        return cls(text=execution_context["text"])
