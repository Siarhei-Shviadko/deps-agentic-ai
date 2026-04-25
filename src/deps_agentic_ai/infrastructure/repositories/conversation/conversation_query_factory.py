from sqlalchemy import (
    Delete,
    Select,
    asc,
    cast,
    delete,
    func,
    literal,
    literal_column,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB, Insert, aggregate_order_by, insert
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql.selectable import NamedFromClause, TableValuedAlias

from ..tables import completion_table, conversation_table, mode_table, tool_set_table

__all__ = ["ConversationQueryFactory"]


class ConversationQueryFactory:
    @classmethod
    def save_query(cls) -> Insert:
        insert_query = insert(conversation_table)
        return insert_query.on_conflict_do_update(
            constraint=conversation_table.primary_key,
            set_=dict(insert_query.excluded),
        )

    @classmethod
    def find_by_id_query(cls, id_: str, user_id: str, tenant_id: str) -> Select:
        return cls._find_query().where(
            conversation_table.c.id == id_,
            conversation_table.c.tenant_id == tenant_id,
            conversation_table.c.created_by == user_id,
        )

    @classmethod
    def conversation_exists_query(cls, id_: str, user_id: str, tenant_id: str) -> Select:
        return select(conversation_table.c.id).where(
            conversation_table.c.id == id_,
            conversation_table.c.created_by == user_id,
            conversation_table.c.tenant_id == tenant_id,
        )

    @classmethod
    def find_by_ids_query(cls, ids: list[str], user_id: str, tenant_id: str) -> Select:
        return cls._find_query().where(
            conversation_table.c.id.in_(ids),
            conversation_table.c.tenant_id == tenant_id,
            conversation_table.c.created_by == user_id,
        )

    @classmethod
    def find_by_mode_id_query(cls, mode_id: str) -> Select:
        return cls._find_query().where(mode_table.c.mode_id == mode_id)

    @classmethod
    def find_by_mode_ids_query(cls, mode_ids: list[str]) -> Select:
        return cls._find_query().where(mode_table.c.mode_id.in_(mode_ids))

    @classmethod
    def find_by_agent_vendor_id_query(cls, agent_vendor_id: str) -> Select:
        return cls._find_query().where(conversation_table.c.agent_vendor_id == agent_vendor_id)

    @classmethod
    def find_by_document_relation_query(cls, document_id: str) -> Select:
        return cls._find_query().where(cast(conversation_table.c.relation, JSONB)["documentId"].astext == document_id)

    @classmethod
    def find_by_document_type_relation_query(cls, document_type_id: str, tenant_id: str) -> Select:
        return cls._find_query().where(
            cast(conversation_table.c.relation, JSONB)["documentTypeId"].astext == document_type_id,
            conversation_table.c.tenant_id == tenant_id,
        )

    @classmethod
    def delete_all_query(cls, ids: list[str]) -> Delete:
        return delete(conversation_table).where(conversation_table.c.id.in_(ids))

    @classmethod
    def _find_query(cls) -> Select:
        tool_set_elements = (
            func.jsonb_array_elements_text(coalesce(mode_table.c.tool_set_ids, literal("[]").cast(JSONB)))
            .table_valued("value")
            .alias("tool_set_elems")
        )
        ts_lateral = cls._build_tool_set_lateral(tool_set_elements)
        cmp_lateral = cls._build_completions_lateral()
        query = select(
            conversation_table,
            mode_table.c.mode_id,
            mode_table.c.code.label("mode_code"),
            mode_table.c.created_at.label("mode_created_at"),
            ts_lateral.c.tool_sets,
            cmp_lateral.c.completions,
        ).select_from(
            conversation_table.outerjoin(mode_table, conversation_table.c.mode_id == mode_table.c.mode_id)
            .outerjoin(ts_lateral, literal_column("true"))
            .outerjoin(cmp_lateral, literal_column("true"))
        )
        return query

    @classmethod
    def _build_tool_set_lateral(cls, tool_set_elements: TableValuedAlias) -> NamedFromClause:
        return (
            select(
                coalesce(
                    cast(
                        func.json_agg(
                            aggregate_order_by(
                                func.json_build_object(
                                    "tool_set_id",
                                    tool_set_table.c.tool_set_id,
                                    "code",
                                    tool_set_table.c.code,
                                    "name",
                                    tool_set_table.c.name,
                                    "tools",
                                    tool_set_table.c.tools,
                                    "created_at",
                                    tool_set_table.c.created_at,
                                ),
                                asc(tool_set_table.c.created_at),
                            )
                        ).filter(tool_set_table.c.tool_set_id.isnot(None)),
                        JSONB,
                    ),
                    literal("[]").cast(JSONB),
                ).label("tool_sets")
            )
            .select_from(
                tool_set_elements.outerjoin(tool_set_table, tool_set_table.c.tool_set_id == tool_set_elements.c.value)
            )
            .lateral()
        )

    @classmethod
    def _build_completions_lateral(cls) -> NamedFromClause:
        return (
            select(
                coalesce(
                    cast(
                        func.json_agg(
                            aggregate_order_by(
                                func.json_build_object(
                                    "id",
                                    completion_table.c.id,
                                    "question",
                                    completion_table.c.question,
                                    "execution_context",
                                    completion_table.c.execution_context,
                                    "answer",
                                    completion_table.c.answer,
                                ),
                                asc(completion_table.c.created_at),
                            )
                        ).filter(completion_table.c.id.isnot(None)),
                        JSONB,
                    ),
                    literal("[]").cast(JSONB),
                ).label("completions")
            )
            .where(completion_table.c.conversation_id == conversation_table.c.id)
            .lateral()
        )
