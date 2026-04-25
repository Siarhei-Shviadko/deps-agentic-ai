from sqlalchemy import Boolean, Column, String, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from deps_agentic_ai.extras import metadata

__all__ = ["agent_vendor_table"]


agent_vendor_table = Table(
    "agent_vendor",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("description", String, nullable=False),
    Column("connection_parameters", JSONB, nullable=False),
    Column("active", Boolean, nullable=False),
    Column("avatar_url", String, nullable=True),
    UniqueConstraint("name", name="agent_vendor_name_uk"),
)
