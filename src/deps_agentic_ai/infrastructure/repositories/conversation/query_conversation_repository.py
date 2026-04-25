from collections import defaultdict

from sqlalchemy import Select, and_, asc, cast, desc, func, join, literal, select
from sqlalchemy.dialects.postgresql import JSONB

from deps_agentic_ai.domain.model.conversation import (
    CompletionInfo,
    ConversationInfo,
    ConversationSortField,
    ConversationSortOrder,
    GroupedConversationsResult,
    IQueryConversationRepository,
)
from deps_agentic_ai.domain.model.shared import Pagination
from deps_agentic_ai.extras import AsyncDatabaseSession

from ..tables import completion_table, conversation_table, mode_table
from .mappers import CompletionInfoMapper, ConversationInfoMapper

__all__ = ["QueryConversationRepository"]


class QueryConversationRepository(IQueryConversationRepository):
    NO_DOCUMENT_KEY = "_no_document"

    def __init__(self, database: AsyncDatabaseSession) -> None:
        self._db = database

    async def conversation_completions(
        self, conversation_id: str, pagination: Pagination | None = None
    ) -> tuple[list[CompletionInfo], int]:
        query = select(
            completion_table,
            func.count(completion_table.c.id).over().label("total"),
        ).where(completion_table.c.conversation_id == conversation_id)

        query = self._apply_filtering(query=query, pagination=pagination)

        async with self._db.connection() as conn:
            rows = await conn.execute(query)

        mappings = rows.mappings().fetchall()

        completions = [CompletionInfoMapper.from_mapping(row) for row in mappings]
        total = mappings[0]["total"] if mappings else 0
        return completions, total

    async def conversation_exists(self, id_: str, user_id: str, tenant_id: str) -> bool:
        query = select(conversation_table.c.id).where(
            conversation_table.c.id == id_,
            conversation_table.c.created_by == user_id,
            conversation_table.c.tenant_id == tenant_id,
        )
        async with self._db.connection() as conn:
            rows = await conn.execute(query)

        return bool(rows.mappings().first())

    async def find_all(
        self,
        tenant_id: str,
        created_by: str,
        page: int,
        size: int,
        mode: str | None = None,
        title: str | None = None,
        agent_vendor_id: str | None = None,
        document_ids: list[str] | None = None,
        sort_by: ConversationSortField = ConversationSortField.CREATED_AT,
        sort_order: ConversationSortOrder = ConversationSortOrder.DESC,
    ) -> GroupedConversationsResult:
        base_join = join(
            conversation_table,
            mode_table,
            conversation_table.c.mode_id == mode_table.c.mode_id,
        )

        conditions = self._build_conditions(
            tenant_id=tenant_id,
            created_by=created_by,
            mode=mode,
            title=title,
            agent_vendor_id=agent_vendor_id,
            document_ids=document_ids,
        )
        order_func = desc if sort_order == ConversationSortOrder.DESC else asc
        sort_column = self._get_sort_column(sort_by)

        relation_jsonb = cast(conversation_table.c.relation, JSONB)
        document_id_expr = func.coalesce(relation_jsonb.op("->>")("documentId"), literal(self.NO_DOCUMENT_KEY))

        ranked_docs_cte = (
            select(
                document_id_expr.label("doc_id"),
                sort_column.label("sort_value"),
            )
            .select_from(base_join)
            .where(and_(*conditions))
            .distinct(document_id_expr)
            .order_by(document_id_expr, order_func(sort_column))
            .cte("ranked_docs")
        )

        paginated_docs_cte = (
            select(
                ranked_docs_cte.c.doc_id,
                func.count(ranked_docs_cte.c.doc_id).over().label("total_groups"),
            )
            .select_from(ranked_docs_cte)
            .order_by(order_func(ranked_docs_cte.c.sort_value))
            .limit(size)
            .offset((page - 1) * size)
            .cte("paginated_docs")
        )

        data_stmt = (
            select(
                conversation_table.c.id,
                conversation_table.c.tenant_id,
                conversation_table.c.agent_vendor_id,
                conversation_table.c.context,
                conversation_table.c.relation,
                conversation_table.c.title,
                conversation_table.c.created_by,
                conversation_table.c.created_at,
                conversation_table.c.updated_at,
                mode_table.c.mode_id.label("mode_id"),
                mode_table.c.code.label("mode_code"),
                document_id_expr.label("extracted_document_id"),
                paginated_docs_cte.c.total_groups.label("total"),
            )
            .select_from(base_join)
            .join(paginated_docs_cte, document_id_expr == paginated_docs_cte.c.doc_id)
            .where(and_(*conditions))
            .order_by(order_func(sort_column))
        )

        async with self._db.connection() as conn:
            rows = await conn.execute(data_stmt)
            mappings = rows.mappings().fetchall()

        return self._group_by_document_id(mappings)

    def _build_conditions(
        self,
        tenant_id: str,
        created_by: str,
        mode: str | None,
        title: str | None,
        agent_vendor_id: str | None,
        document_ids: list[str] | None = None,
    ) -> list:
        conditions = [conversation_table.c.tenant_id == tenant_id, conversation_table.c.created_by == created_by]
        if mode:
            conditions.append(mode_table.c.code == mode)
        if title:
            conditions.append(conversation_table.c.title.ilike(f"%{title}%"))
        if agent_vendor_id:
            conditions.append(conversation_table.c.agent_vendor_id == agent_vendor_id)
        if document_ids:
            relation_jsonb = cast(conversation_table.c.relation, JSONB)
            document_id_expr = relation_jsonb.op("->>")("documentId")
            conditions.append(document_id_expr.in_(document_ids))
        return conditions

    def _get_sort_column(self, sort_by: ConversationSortField):
        columns = {
            ConversationSortField.TITLE: conversation_table.c.title,
            ConversationSortField.CREATED_AT: conversation_table.c.created_at,
            ConversationSortField.UPDATED_AT: conversation_table.c.updated_at,
            ConversationSortField.AGENT_VENDOR_ID: conversation_table.c.agent_vendor_id,
        }
        return columns[sort_by]

    def _group_by_document_id(self, mappings: list) -> GroupedConversationsResult:
        total = mappings[0]["total"] if mappings else 0
        grouped: dict[str, list[ConversationInfo]] = defaultdict(list)

        for row in mappings:
            doc_id = row["extracted_document_id"] or self.NO_DOCUMENT_KEY
            grouped[doc_id].append(ConversationInfoMapper.from_mapping(row))

        return dict(grouped), total

    @staticmethod
    def _apply_filtering(query: Select, pagination: Pagination | None) -> Select:
        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)

        query = query.order_by(completion_table.c.created_at.asc())

        return query
