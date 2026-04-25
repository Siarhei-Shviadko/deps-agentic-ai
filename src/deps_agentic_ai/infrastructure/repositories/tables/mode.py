from sqlalchemy import Column, DateTime, String, Table
from sqlalchemy.dialects.postgresql import JSONB

from deps_agentic_ai.extras import metadata

__all__ = ["mode_table"]


mode_table = Table(
    "mode",
    metadata,
    Column("mode_id", String, primary_key=True),
    Column("code", String, nullable=False),
    Column("tool_set_ids", JSONB, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)
