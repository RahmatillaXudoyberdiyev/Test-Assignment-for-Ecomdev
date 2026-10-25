from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn

from app.config import settings
from app.database import init_db
from app.routers import students_router, payments_router, debtors_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle."""
    print("[Lifecycle] Starting up application: Initializing database tables...")
    await init_db()
    yield
    print("[Lifecycle] Application shutting down cleanly.")


app = FastAPI(
    title="Education Center Payment-Tracking API",
    description="REST API for managing students, recording payments, and monitoring monthly debtor balances.",
    version="1.0.0",
    docs_url="/api",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

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
