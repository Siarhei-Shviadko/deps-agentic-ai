from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, Response, status

from deps_agentic_ai.application import (
    CommandAgentVendorService,
    QueryAgentVendorService,
)
from deps_agentic_ai.containers import Containers

from ...endpoint_marker import MarkerRoute
from ...endpoint_visibility import Visibility
from ...serializers import (
    GetAgentVendorsResponse,
    UpdateAgentVendorConnectionParametersRequest,
    UpdateAgentVendorInfoRequest,
)

__all__ = ["agent_vendors_router"]


agent_vendors_router = APIRouter(prefix="/agent-vendors", tags=["Agent Vendors"], route_class=MarkerRoute)


@agent_vendors_router.get(
    "",
    status_code=status.HTTP_200_OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_model=GetAgentVendorsResponse,
)
@inject
async def get_agent_vendors(
    service: QueryAgentVendorService = Depends(Provide[Containers.query_agent_vendor_service]),
):
    return GetAgentVendorsResponse.from_domain(
        await service.find_all(),
    )


@agent_vendors_router.patch(
    "/{agentVendorId}/activate",
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_class=Response,
)
@inject
async def activate_agent_vendor(
    agent_vendor_id: str = Path(..., alias="agentVendorId"),
    service: CommandAgentVendorService = Depends(Provide[Containers.command_agent_vendor_service]),
):
    await service.activate(agent_vendor_id)


@agent_vendors_router.patch(
    "/{agentVendorId}/info",
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_class=Response,
)
@inject
async def update_agent_vendor_info(
    request: UpdateAgentVendorInfoRequest,
    agent_vendor_id: str = Path(..., alias="agentVendorId"),
    service: CommandAgentVendorService = Depends(Provide[Containers.command_agent_vendor_service]),
):
    await service.update_info(
        id_=agent_vendor_id,
        name=request.name,
        description=request.description,
        avatar_url=request.avatar_url,
    )


@agent_vendors_router.patch(
    "/{agentVendorId}/connection-parameters",
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_class=Response,
)
@inject
async def update_agent_vendor_connection_parameters(
    request: UpdateAgentVendorConnectionParametersRequest,
    agent_vendor_id: str = Path(..., alias="agentVendorId"),
    service: CommandAgentVendorService = Depends(Provide[Containers.command_agent_vendor_service]),
):
    await service.update_connection_parameters(
        id_=agent_vendor_id,
        base_url=request.base_url,
    )


@agent_vendors_router.delete(
    "/{agentVendorId}",
    status_code=status.HTTP_204_NO_CONTENT,
    openapi_extra={"visibility": Visibility.PUBLIC},
    response_class=Response,
)
@inject
async def delete_agent_vendor(
    agent_vendor_id: str = Path(..., alias="agentVendorId"),
    service: CommandAgentVendorService = Depends(Provide[Containers.command_agent_vendor_service]),
):
    await service.delete(agent_vendor_id)
