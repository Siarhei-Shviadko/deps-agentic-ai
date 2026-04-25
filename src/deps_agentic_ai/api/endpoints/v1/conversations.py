import json
from typing import Annotated, Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, Query, Response, status
from sse_starlette.sse import EventSourceResponse

from deps_agentic_ai.api.serializers.paginated_metadata import (
    PaginatedMetadataSerializer,
)
from deps_agentic_ai.api.sse_utils import format_sse_error, format_sse_message
from deps_agentic_ai.application import (
    CommandConversationService,
    QueryConversationService,
)
from deps_agentic_ai.containers import Containers
from deps_agentic_ai.domain.model.conversation import RelationData
from deps_agentic_ai.infrastructure.proxies import SSEEventType

from ...constants import (
    PAGINATION_DEFAULT_PAGE,
    PAGINATION_DEFAULT_PER_PAGE,
    PAGINATION_MIN_PAGE,
    PAGINATION_MIN_PER_PAGE,
)
from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers import (
    ChatRequest,
    CompletionSerializer,
    CompletionsResponse,
    CreateConversationRequest,
    GetConversationResponse,
    GetConversationsQuery,
    GetConversationsResponse,
    ShortConversationResponse,
    SSEEventSerializer,
    UpdateConversationRequest,
)

__all__ = ["conversations_router"]


conversations_router = APIRouter(prefix="/conversations", tags=["Conversations"], route_class=MarkerRoute)


@conversations_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=ShortConversationResponse,
)
@inject
async def create_conversation(
    request: CreateConversationRequest,
    current_user: dict[str, Any] = Depends(Provide[Containers.current_user]),
    service: CommandConversationService = Depends(Provide[Containers.command_conversation_service]),
):
    return ShortConversationResponse.from_domain(
        await service.create(
            tenant_id=current_user["organisation"],
            agent_vendor_id=request.agent_vendor_id,
            mode_id=request.mode_id,
            title=request.title,
            arguments={
                tool_set_code: {tool_code: [arg.to_data() for arg in args] for tool_code, args in tool_set_args.items()}
                for tool_set_code, tool_set_args in request.arguments.items()
            },
            relation_data=RelationData(details=request.relation) if request.relation else None,
            user_id=current_user["subject"],
        ),
    )


@conversations_router.get(
    "/{ConversationId}",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=GetConversationResponse,
)
@inject
async def get_conversation(
    conversation_id: str = Path(..., alias="ConversationId"),
    current_user: dict[str, Any] = Depends(Provide[Containers.current_user]),
    service: CommandConversationService = Depends(Provide[Containers.command_conversation_service]),
):
    return GetConversationResponse.from_domain(
        await service.conversation_of_id(
            id_=conversation_id, user_id=current_user["subject"], tenant_id=current_user["organisation"]
        ),
    )


@conversations_router.get(
    "/{conversationId}/completions",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=CompletionsResponse,
)
@inject
async def get_conversation_completions(
    conversation_id: str = Path(..., alias="conversationId"),
    page: int = Query(default=PAGINATION_DEFAULT_PAGE, ge=PAGINATION_MIN_PAGE),
    per_page: int = Query(default=PAGINATION_DEFAULT_PER_PAGE, alias="perPage", ge=PAGINATION_MIN_PER_PAGE),
    current_user: dict[str, Any] = Depends(Provide[Containers.current_user]),
    service: QueryConversationService = Depends(Provide[Containers.query_conversation_service]),
):
    completions, pagination_metadata = await service.get_conversation_completions(
        conversation_id=conversation_id,
        user_id=current_user["subject"],
        tenant_id=current_user["organisation"],
        page=page,
        per_page=per_page,
    )
    return CompletionsResponse(
        completions=[CompletionSerializer.from_info(completion) for completion in completions],
        metadata=PaginatedMetadataSerializer(
            size=pagination_metadata["result_set"]["count"],
            total=pagination_metadata["result_set"]["total"],
        ),
    )


@conversations_router.patch(
    "/{conversationId}/completions/{completionId}",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
async def edit_question(  # noqa: WPS231
    request: ChatRequest = Depends(ChatRequest.from_query_params),
    conversation_id: str = Path(..., alias="conversationId"),
    completion_id: str = Path(..., alias="completionId"),
    current_user: dict[str, Any] = Depends(Provide[Containers.current_user]),
    service: CommandConversationService = Depends(Provide[Containers.command_conversation_service]),
):
    conversation, agent_vendor = await service.validate_chat_preconditions(
        conversation_id=conversation_id,
        user_id=current_user["subject"],
        tenant_id=current_user["organisation"],
    )

    async def event_generator():  # noqa: WPS430
        try:
            async for event in service.edit_question(
                conversation=conversation,
                agent_vendor=agent_vendor,
                completion_id=completion_id,
                user_question=request.user_question,
                arguments=request.to_context_arguments(),
            ):
                event_type = event.type if isinstance(event.type, SSEEventType) else SSEEventType(event.type)
                event_serializer = SSEEventSerializer(type=event_type, text=event.text)
                event_json = json.dumps(event_serializer.model_dump())
                yield format_sse_message(event_json)

                if event_type == SSEEventType.FINAL:
                    break

        except Exception as e:
            error_event = {"type": "Error", "text": str(e)}
            error_json = json.dumps(error_event)
            yield format_sse_error(error_json)

    return EventSourceResponse(event_generator(), media_type="text/event-stream")


@conversations_router.patch(
    "/{conversationId}",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=ShortConversationResponse,
)
@inject
async def update_conversation(
    data_request: UpdateConversationRequest,
    conversation_id: str = Path(..., alias="conversationId"),
    current_user: dict[str, Any] = Depends(Provide[Containers.current_user]),
    service: CommandConversationService = Depends(Provide[Containers.command_conversation_service]),
):
    return ShortConversationResponse.from_domain(
        await service.update(
            id_=conversation_id,
            user_id=current_user["subject"],
            tenant_id=current_user["organisation"],
            title=data_request.title,
        ),
    )


@conversations_router.get(
    "",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=GetConversationsResponse,
)
@inject
async def get_conversations(
    query: Annotated[GetConversationsQuery, Query()],
    current_user: dict[str, Any] = Depends(Provide[Containers.current_user]),
    service: QueryConversationService = Depends(Provide[Containers.query_conversation_service]),
):
    grouped, total = await service.find_all(
        tenant_id=current_user["organisation"],
        created_by=current_user["subject"],
        page=query.page,
        size=query.size,
        sort_by=query.sort_by,
        sort_order=query.sort_order,
        mode=query.mode,
        title=query.title,
        agent_vendor_id=query.agent_vendor_id,
        document_ids=query.document_id,
    )

    return GetConversationsResponse.from_domain(grouped, total=total)


@conversations_router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
async def delete_conversations(
    ids: set[str] = Query(..., alias="id", min_length=1),
    current_user: dict[str, Any] = Depends(Provide[Containers.current_user]),
    service: CommandConversationService = Depends(Provide[Containers.command_conversation_service]),
):
    return await service.delete_conversations(
        ids=list(ids),
        user_id=current_user["subject"],
        tenant_id=current_user["organisation"],
    )


@conversations_router.get(
    "/{conversationId}/chat",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
async def chat(  # noqa: WPS231
    request: ChatRequest = Depends(ChatRequest.from_query_params),
    conversation_id: str = Path(..., alias="conversationId"),
    current_user: dict[str, Any] = Depends(Provide[Containers.current_user]),
    service: CommandConversationService = Depends(Provide[Containers.command_conversation_service]),
):
    conversation, agent_vendor = await service.validate_chat_preconditions(
        conversation_id=conversation_id,
        user_id=current_user["subject"],
        tenant_id=current_user["organisation"],
    )

    async def event_generator():  # noqa: WPS430
        try:
            async for event in service.chat(
                conversation=conversation,
                agent_vendor=agent_vendor,
                user_question=request.user_question,
                arguments=request.to_context_arguments(),
            ):
                event_type = event.type if isinstance(event.type, SSEEventType) else SSEEventType(event.type)
                event_serializer = SSEEventSerializer(type=event_type, text=event.text)
                event_json = json.dumps(event_serializer.model_dump())
                yield format_sse_message(event_json)

                if event_type == SSEEventType.FINAL:
                    break

        except Exception as e:
            error_event = {"type": "Error", "text": str(e)}
            error_json = json.dumps(error_event)
            yield format_sse_error(error_json)

    return EventSourceResponse(event_generator(), media_type="text/event-stream")
