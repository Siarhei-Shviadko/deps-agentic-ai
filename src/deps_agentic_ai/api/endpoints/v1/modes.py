from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, Query, Response, status

from deps_agentic_ai.application import CommandModeService, QueryModeService
from deps_agentic_ai.containers import Containers

from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers import (
    CreateModeRequest,
    CreateModeResponse,
    GetModesResponse,
    UpdateModeCodeRequest,
    UpdateModeToolSetsRequest,
)

__all__ = ["modes_router"]


modes_router = APIRouter(prefix="/modes", tags=["Modes"], route_class=MarkerRoute)


@modes_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    openapi_extra={"visibility": Visibility.INTERNAL},
    response_model=CreateModeResponse,
)
@inject
async def create_mode(
    request: CreateModeRequest,
    service: CommandModeService = Depends(Provide[Containers.command_mode_service]),
):
    return CreateModeResponse.from_domain(
        await service.create(
            code=request.code,
            tool_set_ids=request.tool_set_ids,
        ),
    )


@modes_router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
async def delete_modes(
    ids: list[str] = Query(..., alias="id"),
    service: CommandModeService = Depends(Provide[Containers.command_mode_service]),
):
    await service.delete(ids)


@modes_router.get(
    "",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.INTERNAL},
    response_model=GetModesResponse,
)
@inject
async def get_modes(
    service: QueryModeService = Depends(Provide[Containers.query_mode_service]),
    code: str | None = Query(None),
):
    return GetModesResponse.from_domain(
        await service.find_all(code=code),
    )


@modes_router.patch(
    "/{modeId}/code",
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
async def update_mode_code(
    request: UpdateModeCodeRequest,
    mode_id: str = Path(..., alias="modeId"),
    service: CommandModeService = Depends(Provide[Containers.command_mode_service]),
):
    await service.update_code(id_=mode_id, code=request.code)


@modes_router.patch(
    "/{modeId}/tool-sets",
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
async def update_mode_tool_sets(
    request: UpdateModeToolSetsRequest,
    mode_id: str = Path(..., alias="modeId"),
    service: CommandModeService = Depends(Provide[Containers.command_mode_service]),
):
    await service.update_tool_sets(
        id_=mode_id,
        tool_sets_to_add_ids=request.tool_sets_to_add_ids,
        tool_sets_to_remove_ids=request.tool_sets_to_remove_ids,
    )
