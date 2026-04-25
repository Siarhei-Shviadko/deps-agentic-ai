from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from deps_agentic_ai.application import CommandToolSetService, QueryToolSetService
from deps_agentic_ai.containers import Containers

from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers import GetToolSetsResponse

__all__ = ["tool_sets_router"]


tool_sets_router = APIRouter(prefix="/tool-sets", tags=["Tool Sets"], route_class=MarkerRoute)


@tool_sets_router.get(
    "",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.INTERNAL},
    response_model=GetToolSetsResponse,
)
@inject
async def get_tool_sets(
    service: QueryToolSetService = Depends(Provide[Containers.query_tool_set_service]),
):
    return GetToolSetsResponse.from_domain(
        await service.find_all(),
    )


@tool_sets_router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
async def delete_tool_sets(
    ids: list[str] = Query(..., alias="id"),
    service: CommandToolSetService = Depends(Provide[Containers.command_tool_set_service]),
):
    await service.delete(ids)
