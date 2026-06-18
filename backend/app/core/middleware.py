import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to every response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: blob:; "
                "font-src 'self'; "
                "connect-src 'self';"
            )

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests and responses with timing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        # Attach request_id for tracing
        request.state.request_id = request_id

        # Skip health check spam
        if request.url.path in ("/health", "/metrics"):
            return await call_next(request)

        client_ip = _get_client_ip(request)

        logger.info(
            "→ {method} {path} | IP: {ip} | ID: {request_id}",
            method=request.method,
            path=request.url.path,
            ip=client_ip,
            request_id=request_id,
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "✗ {method} {path} | {duration:.1f}ms | ERROR: {error} | ID: {request_id}",
                method=request.method,
                path=request.url.path,
                duration=duration_ms,
                error=str(exc),
                request_id=request_id,
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        level = "info" if response.status_code < 400 else "warning"
        if response.status_code >= 500:
            level = "error"

        getattr(logger, level)(
            "← {status} {method} {path} | {duration:.1f}ms | ID: {request_id}",
            status=response.status_code,
            method=request.method,
            path=request.url.path,
            duration=duration_ms,
            request_id=request_id,
        )

        # Add timing and request-id to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

        return response


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """Inject X-Process-Time header."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time"] = f"{duration:.2f}ms"
        return response


def _get_client_ip(request: Request) -> str:
    """Extract real client IP, respecting forwarded headers."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


def setup_middlewares(app) -> None:
    """Register all middlewares on the FastAPI app."""
    # CORS (must be first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Request logging
    app.add_middleware(RequestLoggingMiddleware)

    # Process time
    app.add_middleware(ProcessTimeMiddleware)
