"""
Dev Log Admin API - Main Application

FastAPI application with:
- v1 API: Legacy compatibility (no auth)
- v2 API: New endpoints with authentication
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import init_db, close_db
from app.api.v1.router import router as v1_router
from app.api.v2.router import router as v2_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    # Note: In production, use Alembic migrations instead of init_db
    # await init_db()
    yield
    # Shutdown
    await close_db()
    print("Application shutdown complete")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Development Log Administration API with multi-user support",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(v1_router)  # Legacy API at /api/*
    app.include_router(v2_router)  # New API at /api/v2/*

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs" if settings.DEBUG else "Disabled in production",
            "api": {
                "v1": "/api (legacy)",
                "v2": "/api/v2 (new, with auth)"
            }
        }

    # Health check (accessible without auth)
    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 60)
    print(f"Dev Log Admin Server v{settings.APP_VERSION}")
    print("=" * 60)
    print(f"Dashboard: http://localhost:{settings.PORT}")
    print(f"API Docs:  http://localhost:{settings.PORT}/docs")
    print(f"Legacy API: http://localhost:{settings.PORT}/api")
    print(f"New API:    http://localhost:{settings.PORT}/api/v2")
    print("=" * 60 + "\n")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
