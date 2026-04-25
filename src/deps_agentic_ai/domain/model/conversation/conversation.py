from datetime import datetime, timezone
from typing import TypeAlias
from uuid import uuid4

from ...exceptions import CompletionNotFound, InvariantViolation
from ..agent_vendor.agent_vendor_id import AgentVendorId
from ..shared import Entity, EntityId, Event, Guard, ImmutableCheck, TenantId, UserId
from .agent_request import AgentRequest
from .agent_response import AgentResponse
from .completion import Completion, Question
from .conversation_deleted import ConversationDeleted
from .mode import Context, ContextArguments, Mode
from .relation import Relation

__all__ = ["Conversation"]

ConversationId: TypeAlias = EntityId

DEFAULT_COMPLETION_TRIM_SIZE = 10


class Conversation(metaclass=Entity):  # noqa: WPS230, WPS214
    id = Guard[EntityId](EntityId, ImmutableCheck())
    tenant_id = Guard[TenantId](TenantId, ImmutableCheck())
    agent_vendor_id = Guard[AgentVendorId](AgentVendorId, ImmutableCheck())
    mode = Guard[Mode](Mode, ImmutableCheck())
    context = Guard[Context](Context)
    relation = Guard[Relation](Relation, ImmutableCheck())
    title = Guard[str](str)
    completions = Guard[list[Completion]](list)
    created_by = Guard[UserId](UserId, ImmutableCheck())
    created_at = Guard[datetime](datetime, ImmutableCheck())
    updated_at = Guard[datetime](datetime)

    def __init__(
        self,
        id_: EntityId,
        tenant_id: TenantId,
        agent_vendor_id: AgentVendorId,
        mode: Mode,
        context: Context,
        relation: Relation | None,
        title: str,
        completions: list[Completion],
        created_by: str,
        created_at: datetime,
        updated_at: datetime,
        *,
        events: list[Event] | None = None,
    ) -> None:
        self.id = id_
        self.tenant_id = tenant_id
        self.agent_vendor_id = agent_vendor_id
        self.mode = mode
        self.context = self.mode.sanitize_context(context)
        self.title = title
        self.completions = completions
        self.created_by = created_by
        self.created_at = created_at
        self.updated_at = updated_at

        if relation:
            self.relation = relation

        self.events = events or []

    @property
    def last_completion(self) -> Completion | None:
        return self.completions[-1] if self.completions else None

    @property
    def completed_completions(self) -> list[Completion]:
        completed_completions = []

        for completion in self.completions:
            if completion.is_completed():
                completed_completions.append(completion)
            else:
                return completed_completions

        return completed_completions

    def add_question(
        self,
        question: str,
        agent_vendor_base_url: str,
        arguments: ContextArguments | None = None,
        completion_trim_size: int = DEFAULT_COMPLETION_TRIM_SIZE,
    ) -> AgentRequest:
        self._ensure_can_add_question()
        context = self.mode.merge_context(self.context, arguments) if arguments else self.context

        self.updated_at = datetime.now(timezone.utc)
        completion = self._create_completion(question, self.updated_at)

        return self._build_agent_request(
            completion=completion,
            question=question,
            agent_vendor_base_url=agent_vendor_base_url,
            context=context,
            trim_size=completion_trim_size,
        )

    def add_agent_response(self, response: AgentResponse) -> None:
        self._agent_response_can_be_added()

        if response.is_execution_context():
            self.last_completion.add_execution_context(response.text)
        else:
            self.last_completion.add_answer(response.text)

        self.updated_at = datetime.now(timezone.utc)

    def edit_question(
        self,
        completion_id: str,
        new_text: str,
        agent_vendor_base_url: str,
        new_arguments: ContextArguments | None = None,
        completion_trim_size: int = DEFAULT_COMPLETION_TRIM_SIZE,
    ) -> AgentRequest:
        context = self.mode.merge_context(self.context, new_arguments) if new_arguments else self.context

        self.updated_at = datetime.now(timezone.utc)

        for completion in reversed(self.completions):
            if completion.id() == completion_id:
                completion.edit_question(new_text, self.updated_at)
                new_completion = completion
                break
            else:
                self.completions.remove(completion)
        else:
            raise CompletionNotFound(completion_id)

        return self._build_agent_request(
            completion=new_completion,
            question=new_text,
            agent_vendor_base_url=agent_vendor_base_url,
            context=context,
            trim_size=completion_trim_size,
        )

    def change_title(self, title: str) -> None:
        self.title = title
        self.updated_at = datetime.now(timezone.utc)

    def delete(self):
        self.events.append(ConversationDeleted(id=self.id()))

    def _ensure_can_add_question(self) -> None:
        if self.completions and not self.last_completion.is_completed():
            raise InvariantViolation("Question cannot be added. Last completion has not completed yet.")

    def _create_completion(self, question: str, timestamp: datetime) -> Completion:
        completion = Completion(
            id_=uuid4().hex,
            question=Question(text=question, created_at=timestamp),
            execution_context=[],
            answer=None,
        )
        self.completions.append(completion)
        return completion

    def _build_agent_request(
        self,
        completion: Completion,
        question: str,
        agent_vendor_base_url: str,
        context: Context,
        trim_size: int,
    ) -> AgentRequest:
        return AgentRequest(
            conversation_id=self.id(),
            question=question,
            completion_id=completion.id(),
            agent_vendor_base_url=agent_vendor_base_url,
            context=context.to_data(),
            active_tool_sets=set(self.mode.tool_sets.keys()),
            context_bundle={
                "conversationTrim": [
                    {
                        "question": comp.question.text,
                        "answer": comp.answer.text,
                    }
                    for comp in self.completed_completions[-trim_size:]
                ]
            },
        )

    def _agent_response_can_be_added(self) -> None:
        if self.last_completion is None:
            raise InvariantViolation("Agent response cannot be added. Completion is not exists.")

        elif self.last_completion.is_completed():
            raise InvariantViolation("Agent response cannot be added. Last completion is completed.")
