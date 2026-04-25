from fastapi import APIRouter

from .agent_vendors import *
from .conversations import *
from .modes import *
from .tool_sets import *

__all__ = ["v1_router"]


v1_router = APIRouter(prefix="/v1")

v1_router.include_router(tool_sets_router)
v1_router.include_router(modes_router)
v1_router.include_router(agent_vendors_router)
v1_router.include_router(conversations_router)
