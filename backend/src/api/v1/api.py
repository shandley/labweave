"""API v1 router configuration."""
from fastapi import APIRouter

from src.api.v1.endpoints import (
    auth, users, projects, experiments, health, protocols, samples, documents, 
    test, simple_documents, documents_noauth, knowledge_graph
)

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
api_router.include_router(test.router, prefix="/test", tags=["test"])
api_router.include_router(simple_documents.router, prefix="/simple_documents", tags=["simple_documents"])
api_router.include_router(documents_noauth.router, prefix="/documents_noauth", tags=["documents_noauth"])
api_router.include_router(knowledge_graph.router, prefix="/knowledge-graph", tags=["knowledge_graph"])