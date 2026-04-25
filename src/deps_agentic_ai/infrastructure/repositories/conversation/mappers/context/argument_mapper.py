from typing import Any, Mapping

from deps_agentic_ai.domain.model.conversation import Argument


class ArgumentMapper:
    @staticmethod
    def from_mapping(arg: Mapping[str, Any]) -> Argument:
        return Argument(
            name=arg["name"],
            value=arg["value"],
        )

    @staticmethod
    def to_dict(arg: Argument) -> dict[str, Any]:
        return {
            "name": arg.name,
            "value": arg.value,
        }
