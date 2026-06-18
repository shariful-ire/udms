import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette.exceptions import HTTPException

from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.middleware import setup_middlewares
from app.db.session import engine

# ─── Logging Setup ────────────────────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - {message}",
    level="DEBUG" if settings.DEBUG else "INFO",
    colorize=True,
)
logger.add(
    "logs/app.log",
    rotation="50 MB",
    retention="30 days",
    compression="zip",
    format="{time} {level} {message}",
    level="INFO",
    serialize=True,
)


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"   Environment: {settings.ENVIRONMENT}")

    # Verify DB connection
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy", fromlist=["text"]).text("SELECT 1"))
        logger.info("✅ Database connection verified")
    except Exception as exc:
        logger.error(f"❌ Database connection failed: {exc}")

    # Verify Redis connection
    try:
        from app.api.v1.deps import get_redis
        redis = await get_redis()
        await redis.ping()
        logger.info("✅ Redis connection verified")
    except Exception as exc:
        logger.warning(f"⚠️  Redis connection failed: {exc}")

    yield

    logger.info("Shutting down application...")
    await engine.dispose()


# ─── App Factory ──────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="University Dining Management System — Production API",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Trusted hosts ─────────────────────────────────────────────────────────
    if settings.ENVIRONMENT == "production" and settings.ALLOWED_HOSTS != ["*"]:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

    # ── Middlewares ───────────────────────────────────────────────────────────
    setup_middlewares(app)

    # ── Static files ──────────────────────────────────────────────────────────
    import os
    os.makedirs("uploads/avatars", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(api_v1_router)

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "healthy", "version": settings.APP_VERSION}

    # ── Exception handlers ────────────────────────────────────────────────────
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", [])[1:])
            errors.append({"field": field, "message": error["msg"]})
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "message": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "errors": errors,
            },
        )

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        if isinstance(exc.detail, dict):
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": str(exc.detail),
                "error_code": "HTTP_ERROR",
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception on {request.method} {request.url}: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "An internal server error occurred",
                "error_code": "INTERNAL_ERROR",
            },
        )

    return app


app = create_app()
