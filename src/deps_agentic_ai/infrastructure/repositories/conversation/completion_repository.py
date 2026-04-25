from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from deps_agentic_ai.domain.model.conversation import Completion

from ..tables import completion_table
from .mappers.completion import CompletionMapper as CompletionMapper

__all__ = ["CompletionRepository"]


class CompletionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_all(self, conversation_id: str, completions: list[Completion]) -> None:
        insert_query = insert(completion_table)
        save_query = insert_query.on_conflict_do_update(
            constraint=completion_table.primary_key,
            set_=dict(insert_query.excluded),
        )
        raw_data = [CompletionMapper.to_dict(conversation_id, completion) for completion in completions]

        await self._session.execute(save_query, raw_data)

    async def delete_all(self, conversation_id: str) -> None:
        await self._session.execute(
            delete(completion_table).where(completion_table.c.conversation_id == conversation_id)
        )
