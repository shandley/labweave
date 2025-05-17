"""API v1 router configuration."""
from fastapi import APIRouter

from src.api.v1.endpoints import auth, users, projects, experiments, health, protocols, samples, documents

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
api_router.include_router(protocols.router, prefix="/protocols", tags=["protocols"])
api_router.include_router(samples.router, prefix="/samples", tags=["samples"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])