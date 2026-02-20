"""FastAPI main application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings
from app.utils.logger import setup_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Teslas.ai API starting up...")
    setup_logging()
    logger.info(f"Configuration: {settings}")
    yield
    # Shutdown
    logger.info("Teslas.ai API shutting down...")


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="Teslas.ai - Scientific Assistant API",
        description="Multi-agent scientific research platform",
        version="0.2.0",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(router, prefix="/api", tags=["research"])
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "Teslas.ai",
            "version": "0.2.0",
            "description": "Multi-agent scientific assistant",
            "endpoints": [
                "/api/health",
                "/api/research",
                "/api/search",
                "/api/agents",
                "/api/ingest",
            ],
        }
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )
