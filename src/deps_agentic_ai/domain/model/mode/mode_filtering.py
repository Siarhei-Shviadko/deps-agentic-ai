from dataclasses import dataclass

__all__ = ["ModeFiltering"]


@dataclass
class ModeFiltering:
    code: str | None = None
