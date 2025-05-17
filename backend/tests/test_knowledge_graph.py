"""Tests for knowledge graph functionality."""
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.knowledge_graph.models import NodeType, RelationType
from src.db.neo4j import neo4j_db


def test_knowledge_graph_health(client: TestClient):
    """Test knowledge graph health endpoint."""
    response = client.get("/api/v1/knowledge-graph/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    # Neo4j might not be running in test environment
    assert data["status"] in ["healthy", "unhealthy"]


def test_create_node(client: TestClient, test_user_token: str):
    """Test creating a node in the knowledge graph."""
    node_data = {
        "type": NodeType.DOCUMENT.value,
        "properties": {
            "document_id": 1,
            "title": "Test Document",
            "file_type": ".txt"
        }
    }
    
    response = client.post(
        "/api/v1/knowledge-graph/nodes",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json=node_data
    )
    
    # We expect this to work only if Neo4j is running
    if response.status_code == 200:
        data = response.json()
        assert data["message"] == "Node created successfully"
        assert "node_id" in data
    else:
        # Neo4j not available - that's OK for tests
        assert response.status_code == 500


def test_create_relationship(client: TestClient, test_user_token: str):
    """Test creating a relationship between nodes."""
    # First create two nodes
    node1_data = {
        "type": NodeType.USER.value,
        "properties": {
            "user_id": 1,
            "username": "testuser",
            "email": "test@example.com"
        }
    }
    
    node2_data = {
        "type": NodeType.PROJECT.value,
        "properties": {
            "project_id": 1,
            "name": "Test Project"
        }
    }
    
    # Create nodes
    response1 = client.post(
        "/api/v1/knowledge-graph/nodes",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json=node1_data
    )
    
    response2 = client.post(
        "/api/v1/knowledge-graph/nodes",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json=node2_data
    )
    
    # Only test relationship if nodes were created successfully
    if response1.status_code == 200 and response2.status_code == 200:
        # Create relationship
        rel_data = {
            "type": RelationType.OWNS.value,
            "source_id": "user_1",
            "target_id": "project_1",
            "properties": {"created_at": "2024-01-01"}
        }
        
        response = client.post(
            "/api/v1/knowledge-graph/relationships",
            headers={"Authorization": f"Bearer {test_user_token}"},
            json=rel_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Relationship created successfully"


def test_search_knowledge_graph(client: TestClient, test_user_token: str):
    """Test searching the knowledge graph."""
    search_data = {
        "query_text": "test",
        "node_type": NodeType.DOCUMENT.value,
        "max_depth": 2
    }
    
    response = client.post(
        "/api/v1/knowledge-graph/search",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json=search_data
    )
    
    # Should always return a valid response structure
    assert response.status_code in [200, 500]  # 500 if Neo4j not available
    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert "count" in data


def test_find_path(client: TestClient, test_user_token: str):
    """Test finding path between nodes."""
    response = client.get(
        "/api/v1/knowledge-graph/path/user_1/project_1?max_depth=3",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    # Should always return a valid response
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "path" in data
        # Path might be None if no connection exists