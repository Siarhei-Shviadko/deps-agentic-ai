from fastapi import APIRouter

from .agent_vendor import *
from .tool_sets import *

__all__ = ["internal_router"]


internal_router = APIRouter(prefix="/internal")

internal_router.include_router(tool_sets_router)
internal_router.include_router(agent_vendors_router)
