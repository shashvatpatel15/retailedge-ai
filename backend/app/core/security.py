import os
from fastapi import Request, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import EDGE_API_KEY

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds OWASP-recommended security headers to all responses.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


async def verify_edge_api_key(request: Request):
    """
    Validates the API key if EDGE_API_KEY is configured.
    If EDGE_API_KEY is empty, permits open access (e.g. local lab dev).
    """
    if not EDGE_API_KEY:
        return True

    client_key = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
    auth_header = request.headers.get("Authorization", "")

    if not client_key and auth_header.startswith("Bearer "):
        client_key = auth_header.split(" ", 1)[1]

    if not client_key or client_key != EDGE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing edge API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return True
