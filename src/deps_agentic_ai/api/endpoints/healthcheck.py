from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from deps_agentic_ai.api.endpoint_marker import MarkerRoute
from deps_agentic_ai.api.endpoint_visibility import Visibility
from deps_agentic_ai.containers import Datasources
from deps_agentic_ai.extras import AsyncDatabaseSession

__all__ = ["healthcheck_router"]

healthcheck_router = APIRouter(route_class=MarkerRoute)


@healthcheck_router.get(
    "/healthcheck",
    tags=["Debug"],
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
async def service_healthcheck(datasource: AsyncDatabaseSession = Depends(Provide[Datasources.postgres_session])):
    """Check connection to database."""
    try:
        await datasource.healthcheck()
    except Exception:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"status": "unavailable"})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})
