from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Table
from sqlalchemy.dialects.postgresql import JSONB

from deps_agentic_ai.extras import metadata

__all__ = ["completion_table"]

completion_table = Table(
    "completion",
    metadata,
    Column("id", String(150), primary_key=True),
    Column("question", JSONB, nullable=False),
    Column("execution_context", JSONB, nullable=False),
    Column("answer", JSONB, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("conversation_id", String(150), ForeignKey("conversation.id", ondelete="CASCADE"), nullable=False),
    Index("idx_completion_conversation_id", "conversation_id"),
    Index("idx_completion_created_at", "created_at"),
)
