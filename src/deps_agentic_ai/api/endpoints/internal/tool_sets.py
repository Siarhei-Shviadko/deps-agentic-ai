from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from deps_agentic_ai.application import CommandToolSetService
from deps_agentic_ai.containers import Containers

from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers import RegisterToolSetRequest, RegisterToolSetResponse

__all__ = ["tool_sets_router"]


tool_sets_router = APIRouter(prefix="/tool-sets", tags=["Tool Sets"], route_class=MarkerRoute)


@tool_sets_router.put(
    "",
    status_code=status.HTTP_201_CREATED,
    openapi_extra={"visibility": Visibility.INTERNAL},
    response_model=RegisterToolSetResponse,
)
@inject
async def register_tool_set(
    request: RegisterToolSetRequest,
    service: CommandToolSetService = Depends(Provide[Containers.command_tool_set_service]),
):
    return RegisterToolSetResponse.from_domain(
        await service.register(
            code=request.code,
            name=request.name,
            tools=[t.to_domain() for t in request.tools],
        ),
    )
