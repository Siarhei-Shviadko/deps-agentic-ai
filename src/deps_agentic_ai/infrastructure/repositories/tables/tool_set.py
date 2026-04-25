from sqlalchemy import Column, DateTime, String, Table
from sqlalchemy.dialects.postgresql import JSONB

from deps_agentic_ai.extras import metadata

__all__ = ["tool_set_table"]


tool_set_table = Table(
    "tool_set",
    metadata,
    Column("tool_set_id", String, primary_key=True),
    Column("code", String, nullable=False),
    Column("name", String, nullable=False),
    Column("tools", JSONB, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)
