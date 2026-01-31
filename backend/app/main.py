"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import sessions, simulation, personas, providers, export, objectives, objective_presets

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    logger.info("Starting Red Team Actor Simulator...")
    await init_db()
    logger.info("Database initialized")
    logger.info(f"Available providers: {settings.get_available_providers()}")

    yield

    # Shutdown
    logger.info("Shutting down Red Team Actor Simulator...")


app = FastAPI(
    title="Red Team Actor Simulator",
    description="""
    A framework for testing AI model safety/robustness through simulated adversarial scenarios.

    ## Features
    - **Configurable Personas**: Skill level, resources, and background dimensions
    - **Multi-Provider Support**: OpenAI, Anthropic, Google, Ollama
    - **Objective Chaining**: Sequential harm journey simulation
    - **Sneaky Mode**: Enhanced actor capabilities for harder probing
    - **Comprehensive Reports**: Markdown and PDF output
    """,
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(personas.router, prefix="/api/personas", tags=["Personas"])
app.include_router(providers.router, prefix="/api/providers", tags=["Providers"])
app.include_router(objectives.router, prefix="/api/objectives", tags=["Objectives"])
app.include_router(objective_presets.router, prefix="/api/objective-presets", tags=["Objective Presets"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Red Team Actor Simulator",
        "version": "0.1.0",
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "providers": settings.get_available_providers(),
        "database": "connected",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
