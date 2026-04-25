import json
import logging
from http import HTTPStatus
from typing import Any, Dict

from fastapi import Request

from deps_agentic_ai.constants import INTERNAL_API_PREFIX
from deps_agentic_ai.domain.exceptions import AuthError
from deps_agentic_ai.infrastructure.access_management import user

__all__ = ["set_user_from_token"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PUBLIC_ENDPOINTS = (
    "/api/agentic-ai/v1/docs",
    "/api/agentic-ai/v1/openapi.json",
    "/api/agentic-ai/debug/500",
    "/api/agentic-ai/healthcheck",
    "/api/agentic-ai/service-info/version",
    "/favicon.ico",
)

PUBLIC_PATHS = (("/api/agentic-ai/internal/agent-vendors", "POST"),)


def set_user_from_token(
    request: Request,
) -> None:
    if (
        request.url.path in PUBLIC_ENDPOINTS
        or INTERNAL_API_PREFIX in request.url.path
        or (request.url.path, request.method) in PUBLIC_PATHS
    ):
        return

    try:
        deps_token = json.loads(request.headers["deps-token"])
        _validate_deps_token(deps_token)
        user.set(deps_token)

    except KeyError:
        raise AuthError("Deps-token doesn't provided.")

    except TypeError:
        raise AuthError("Provided deps-token isn't correct.")


def _validate_deps_token(deps_token: Dict[str, Any]) -> None:
    if not deps_token:
        raise AuthError("Deps-token validation fails. Deps-token is invalid.")
    elif not deps_token.get("organisation"):
        raise AuthError(
            detail="User without organisation.",
            status_code=HTTPStatus.FORBIDDEN,
        )
