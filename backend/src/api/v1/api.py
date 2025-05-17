"""API v1 router configuration."""
from fastapi import APIRouter

from src.api.v1.endpoints import auth, users, projects, experiments

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])