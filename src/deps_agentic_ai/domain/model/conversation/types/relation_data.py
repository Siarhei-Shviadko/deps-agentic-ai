from typing import Any, TypedDict

__all__ = ["RelationData"]


class RelationData(TypedDict):
    details: dict[str, Any]
