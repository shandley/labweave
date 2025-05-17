"""Main FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.config import settings
from src.api.v1.api import api_router
from src.db.neo4j import neo4j_db, init_neo4j_indexes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LabWeave API",
    description="Research operations platform for omics research",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=True,  # Enable debug mode to see more info
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to LabWeave API",
        "version": "0.1.0",
        "docs": "/docs",
    }


# Application lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        # Initialize Neo4j indexes
        logger.info("Initializing Neo4j indexes...")
        init_neo4j_indexes()
        logger.info("Neo4j initialization complete")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Don't fail startup if Neo4j is not available
        logger.warning("Continuing without Neo4j connection")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    try:
        # Close Neo4j connection
        neo4j_db.close()
        logger.info("Neo4j connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")