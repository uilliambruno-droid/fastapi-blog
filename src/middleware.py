"""Application middleware for logging, tracing, and security."""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Logs incoming requests and outgoing responses with timing and unique IDs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request, measure latency, and log details."""
        # Generate unique request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Capture request details
        method = request.method
        path = request.url.path
        query_string = request.url.query
        client_host = request.client.host if request.client else "unknown"

        # Log request start
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_string": query_string,
                "client": client_host,
            },
        )

        start_time = time.perf_counter()

        try:
            # Call the next middleware/endpoint
            response = await call_next(request)
            elapsed_seconds = time.perf_counter() - start_time

            # Log response success
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "elapsed_seconds": elapsed_seconds,
                },
            )

            # Attach request ID to response headers for client tracing
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            elapsed_seconds = time.perf_counter() - start_time
            logger.error(
                "Request failed with exception",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "elapsed_seconds": elapsed_seconds,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                },
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Enable XSS protection (legacy, but good for backward compatibility)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        return response


def setup_cors(app) -> None:
    """Configure CORS middleware with sensible defaults."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:8000",
            "http://localhost:8080",
            "https://fastapi-blog-jrf4.onrender.com",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
        max_age=3600,  # 1 hour
    )
