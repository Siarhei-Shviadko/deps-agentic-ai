from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from deps_agentic_ai.application import CommandAgentVendorService
from deps_agentic_ai.containers import Containers

from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers import CreateAgentVendorRequest, CreateAgentVendorResponse

__all__ = ["agent_vendors_router"]


agent_vendors_router = APIRouter(prefix="/agent-vendors", tags=["Agent Vendors"], route_class=MarkerRoute)


@agent_vendors_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=CreateAgentVendorResponse,
)
@inject
async def create_agent_vendor(
    request: CreateAgentVendorRequest,
    service: CommandAgentVendorService = Depends(Provide[Containers.command_agent_vendor_service]),
):
    return CreateAgentVendorResponse.from_domain(
        await service.create(
            name=request.name,
            description=request.description,
            base_url=request.base_url,
            avatar_url=request.avatar_url,
        ),
    )
