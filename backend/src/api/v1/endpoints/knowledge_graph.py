"""Knowledge graph API endpoints."""
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.api.v1.endpoints.auth import get_current_user
from src.models.user import User
from src.knowledge_graph.service import knowledge_graph
from src.knowledge_graph.models import (
    GraphNode, GraphRelationship, NodeType, RelationType,
    KnowledgeGraphQuery, GraphPath
)

router = APIRouter()


class NodeCreateRequest(BaseModel):
    """Request model for creating a node."""
    type: NodeType
    properties: Dict[str, Any]


class RelationshipCreateRequest(BaseModel):
    """Request model for creating a relationship."""
    type: RelationType
    source_id: str
    target_id: str
    properties: Dict[str, Any] = {}


class SearchRequest(BaseModel):
    """Request model for searching the knowledge graph."""
    query_text: Optional[str] = None
    node_type: Optional[NodeType] = None
    relationship_type: Optional[RelationType] = None
    properties_filter: Dict[str, Any] = {}
    max_depth: int = 3


@router.post("/nodes")
async def create_node(
    node_request: NodeCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new node in the knowledge graph."""
    try:
        # Generate node ID based on type and properties
        if node_request.type == NodeType.DOCUMENT:
            node_id = f"document_{node_request.properties.get('document_id', 'unknown')}"
        elif node_request.type == NodeType.PROJECT:
            node_id = f"project_{node_request.properties.get('project_id', 'unknown')}"
        elif node_request.type == NodeType.USER:
            node_id = f"user_{node_request.properties.get('user_id', 'unknown')}"
        else:
            node_id = f"{node_request.type.lower()}_{id(node_request)}"
        
        node = GraphNode(
            id=node_id,
            type=node_request.type,
            properties=node_request.properties
        )
        
        success = knowledge_graph.create_node(node)
        
        if success:
            return {"message": "Node created successfully", "node_id": node_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to create node")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/relationships")
async def create_relationship(
    rel_request: RelationshipCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a relationship between nodes."""
    try:
        relationship = GraphRelationship(
            type=rel_request.type,
            source_id=rel_request.source_id,
            target_id=rel_request.target_id,
            properties=rel_request.properties
        )
        
        success = knowledge_graph.create_relationship(relationship)
        
        if success:
            return {"message": "Relationship created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create relationship")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodes/{node_id}")
async def get_node(
    node_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a node by ID."""
    node = knowledge_graph.get_node(node_id)
    
    if node:
        return node
    else:
        raise HTTPException(status_code=404, detail="Node not found")


@router.get("/nodes/{node_id}/relationships")
async def get_node_relationships(
    node_id: str,
    relationship_type: Optional[RelationType] = Query(None),
    direction: str = Query("both", regex="^(incoming|outgoing|both)$"),
    current_user: User = Depends(get_current_user)
):
    """Get relationships for a node."""
    try:
        relationships = knowledge_graph.get_node_relationships(
            node_id=node_id,
            relationship_type=relationship_type,
            direction=direction
        )
        
        return {"relationships": relationships}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodes/{node_id}/related")
async def get_related_nodes(
    node_id: str,
    max_depth: int = Query(2, ge=1, le=5),
    current_user: User = Depends(get_current_user)
):
    """Get all nodes related to a given node."""
    try:
        related_nodes = knowledge_graph.get_related_nodes(
            node_id=node_id,
            max_depth=max_depth
        )
        
        return {"related_nodes": related_nodes}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_knowledge_graph(
    search_request: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Search the knowledge graph."""
    try:
        results = []
        
        # Full-text search
        if search_request.query_text:
            results = knowledge_graph.full_text_search(
                query_text=search_request.query_text,
                node_type=search_request.node_type
            )
        
        # Property-based search
        elif search_request.properties_filter or search_request.node_type:
            query = KnowledgeGraphQuery(
                node_type=search_request.node_type,
                properties_filter=search_request.properties_filter,
                max_depth=search_request.max_depth
            )
            results = knowledge_graph.search_nodes(query)
        
        return {"results": results, "count": len(results)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/path/{start_id}/{end_id}")
async def find_path(
    start_id: str,
    end_id: str,
    max_depth: int = Query(5, ge=1, le=10),
    current_user: User = Depends(get_current_user)
):
    """Find shortest path between two nodes."""
    try:
        path = knowledge_graph.find_path(
            start_id=start_id,
            end_id=end_id,
            max_depth=max_depth
        )
        
        if path:
            return {
                "path": path.dict(),
                "length": path.length
            }
        else:
            return {"message": "No path found", "path": None}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def knowledge_graph_health():
    """Check Neo4j connection health."""
    try:
        is_connected = knowledge_graph.db.check_connection()
        
        return {
            "status": "healthy" if is_connected else "unhealthy",
            "neo4j_connected": is_connected
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "neo4j_connected": False,
            "error": str(e)
        }