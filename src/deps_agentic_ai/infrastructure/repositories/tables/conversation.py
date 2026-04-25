from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB

from deps_agentic_ai.extras import metadata

__all__ = ["conversation_table"]


conversation_table = Table(
    "conversation",
    metadata,
    Column("id", String(150), primary_key=True),
    Column("tenant_id", String(150), nullable=False),
    Column("agent_vendor_id", String(150), nullable=False),
    Column("context", JSONB, nullable=False),
    Column("relation", Text, nullable=True),
    Column("title", String(250), nullable=False),
    Column("created_by", String(250), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Column("mode_id", String(150), ForeignKey("mode.mode_id", ondelete="CASCADE"), nullable=False),
    Index("idx_conversation_relation", "relation"),
)
