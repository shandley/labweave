"""Knowledge graph node and relationship models."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Types of nodes in the knowledge graph."""
    USER = "User"
    PROJECT = "Project"
    EXPERIMENT = "Experiment"
    SAMPLE = "Sample"
    PROTOCOL = "Protocol"
    DOCUMENT = "Document"
    PAPER = "Paper"
    GENE = "Gene"
    PROTEIN = "Protein"
    ORGANISM = "Organism"
    CHEMICAL = "Chemical"
    METHOD = "Method"
    DATASET = "Dataset"


class RelationType(str, Enum):
    """Types of relationships in the knowledge graph."""
    CREATED_BY = "CREATED_BY"
    OWNS = "OWNS"
    PARTICIPATES_IN = "PARTICIPATES_IN"
    CONTAINS = "CONTAINS"
    BELONGS_TO = "BELONGS_TO"
    USES = "USES"
    REFERENCES = "REFERENCES"
    CITES = "CITES"
    DERIVED_FROM = "DERIVED_FROM"
    ANALYZES = "ANALYZES"
    PRODUCES = "PRODUCES"
    RELATED_TO = "RELATED_TO"
    VERSION_OF = "VERSION_OF"
    TAGGED_WITH = "TAGGED_WITH"
    ANNOTATES = "ANNOTATES"
    DESCRIBES = "DESCRIBES"


class GraphNode(BaseModel):
    """Base model for knowledge graph nodes."""
    id: str
    type: NodeType
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class GraphRelationship(BaseModel):
    """Base model for knowledge graph relationships."""
    id: Optional[str] = None
    type: RelationType
    source_id: str
    target_id: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class ProjectNode(GraphNode):
    """Project node in the knowledge graph."""
    type: NodeType = NodeType.PROJECT
    
    def __init__(self, project_id: int, name: str, description: Optional[str] = None, **kwargs):
        properties = {
            "project_id": project_id,
            "name": name,
            "description": description,
            **kwargs
        }
        super().__init__(id=f"project_{project_id}", properties=properties)


class DocumentNode(GraphNode):
    """Document node in the knowledge graph."""
    type: NodeType = NodeType.DOCUMENT
    
    def __init__(self, document_id: int, title: str, file_type: str, 
                 document_type: Optional[str] = None, **kwargs):
        properties = {
            "document_id": document_id,
            "title": title,
            "file_type": file_type,
            "document_type": document_type,
            **kwargs
        }
        super().__init__(id=f"document_{document_id}", properties=properties)


class ExperimentNode(GraphNode):
    """Experiment node in the knowledge graph."""
    type: NodeType = NodeType.EXPERIMENT
    
    def __init__(self, experiment_id: int, name: str, 
                 experiment_type: Optional[str] = None, **kwargs):
        properties = {
            "experiment_id": experiment_id,
            "name": name,
            "experiment_type": experiment_type,
            **kwargs
        }
        super().__init__(id=f"experiment_{experiment_id}", properties=properties)


class SampleNode(GraphNode):
    """Sample node in the knowledge graph."""
    type: NodeType = NodeType.SAMPLE
    
    def __init__(self, sample_id: int, name: str, sample_type: str, **kwargs):
        properties = {
            "sample_id": sample_id,
            "name": name,
            "sample_type": sample_type,
            **kwargs
        }
        super().__init__(id=f"sample_{sample_id}", properties=properties)


class UserNode(GraphNode):
    """User node in the knowledge graph."""
    type: NodeType = NodeType.USER
    
    def __init__(self, user_id: int, username: str, email: str, **kwargs):
        properties = {
            "user_id": user_id,
            "username": username,
            "email": email,
            **kwargs
        }
        super().__init__(id=f"user_{user_id}", properties=properties)


class KnowledgeGraphQuery(BaseModel):
    """Query model for knowledge graph searches."""
    start_node_id: Optional[str] = None
    end_node_id: Optional[str] = None
    node_type: Optional[NodeType] = None
    relationship_type: Optional[RelationType] = None
    max_depth: int = Field(default=3, ge=1, le=10)
    properties_filter: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True


class GraphPath(BaseModel):
    """Represents a path in the knowledge graph."""
    nodes: List[GraphNode]
    relationships: List[GraphRelationship]
    length: int
    
    class Config:
        use_enum_values = True