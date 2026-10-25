import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

from app.config import settings
from app.database import init_db
from app.logger import setup_logging
from app.routers import students_router, payments_router, debtors_router

setup_logging()
logger = logging.getLogger("app.main")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware logging HTTP request progress, status codes, and execution duration."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        client_host = request.client.host if request.client else "unknown"
        logger.info("--> Incoming %s %s from %s", request.method, request.url.path, client_host)

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info("<-- Finished %s %s [%d] in %.2f ms", request.method, request.url.path, response.status_code, duration_ms)
            return response
        except Exception as error:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.exception("<-- Failed %s %s with unhandled error after %.2f ms: %s", request.method, request.url.path, duration_ms, error)
            raise


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle."""
    logger.info("Application starting up: Initializing database tables...")
    try:
        await init_db()
        logger.info("Application startup completed successfully.")
    except Exception as error:
        logger.exception("Application startup failed during database initialization: %s", error)
        raise

    yield

    logger.info("Application shutting down cleanly.")


app = FastAPI(
    title="Education Center Payment-Tracking API",
    description="REST API for managing students, recording payments, and monitoring monthly debtor balances.",
    version="1.0.0",
    docs_url="/api",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(students_router)
app.include_router(payments_router)
app.include_router(debtors_router)


@app.get("/", include_in_schema=False)
async def root_redirect() -> RedirectResponse:
    """Redirect root path to interactive Swagger documentation."""
    return RedirectResponse(url="/api")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
    )
