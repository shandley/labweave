"""Knowledge graph service for managing graph operations."""
import json
import logging
from typing import List, Dict, Any, Optional

from neo4j.exceptions import Neo4jError

from src.db.neo4j import neo4j_db
from src.knowledge_graph.models import (
    GraphNode, GraphRelationship, NodeType, RelationType,
    ProjectNode, DocumentNode, ExperimentNode, SampleNode, UserNode,
    KnowledgeGraphQuery, GraphPath
)

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """Service for knowledge graph operations."""
    
    def __init__(self):
        """Initialize the knowledge graph service."""
        self.db = neo4j_db
    
    def create_node(self, node: GraphNode) -> bool:
        """Create a node in the knowledge graph."""
        with self.db.get_session() as session:
            try:
                query = """
                MERGE (n:{type} {{id: $id}})
                SET n += $properties
                SET n.created_at = datetime($created_at)
                SET n.updated_at = datetime()
                RETURN n
                """.format(type=node.type)
                
                result = session.run(
                    query,
                    id=node.id,
                    properties=node.properties,
                    created_at=node.created_at.isoformat()
                )
                
                return result.single() is not None
                
            except Neo4jError as e:
                logger.error(f"Error creating node: {e}")
                raise
    
    def create_relationship(self, relationship: GraphRelationship) -> bool:
        """Create a relationship between nodes."""
        with self.db.get_session() as session:
            try:
                query = """
                MATCH (source {{id: $source_id}})
                MATCH (target {{id: $target_id}})
                MERGE (source)-[r:{type}]->(target)
                SET r += $properties
                SET r.created_at = datetime($created_at)
                RETURN r
                """.format(type=relationship.type)
                
                result = session.run(
                    query,
                    source_id=relationship.source_id,
                    target_id=relationship.target_id,
                    properties=relationship.properties,
                    created_at=relationship.created_at.isoformat()
                )
                
                return result.single() is not None
                
            except Neo4jError as e:
                logger.error(f"Error creating relationship: {e}")
                raise
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID."""
        with self.db.get_session() as session:
            try:
                query = """
                MATCH (n {{id: $id}})
                RETURN n
                """
                
                result = session.run(query, id=node_id)
                record = result.single()
                
                if record:
                    return dict(record["n"])
                return None
                
            except Neo4jError as e:
                logger.error(f"Error getting node: {e}")
                raise
    
    def get_node_relationships(self, node_id: str, 
                             relationship_type: Optional[str] = None,
                             direction: str = "both") -> List[Dict[str, Any]]:
        """Get relationships for a node."""
        with self.db.get_session() as session:
            try:
                if direction == "outgoing":
                    pattern = "(n)-[r]->(target)"
                elif direction == "incoming":
                    pattern = "(source)-[r]->(n)"
                else:
                    pattern = "(n)-[r]-(connected)"
                
                if relationship_type:
                    pattern = pattern.replace("[r]", f"[r:{relationship_type}]")
                
                query = f"""
                MATCH {{n {{id: $id}}}}
                MATCH {pattern}
                RETURN r, 
                       CASE 
                           WHEN exists(target) THEN target
                           WHEN exists(source) THEN source
                           ELSE connected
                       END as other_node
                """
                
                result = session.run(query, id=node_id)
                
                relationships = []
                for record in result:
                    rel = dict(record["r"])
                    rel["other_node"] = dict(record["other_node"])
                    relationships.append(rel)
                
                return relationships
                
            except Neo4jError as e:
                logger.error(f"Error getting relationships: {e}")
                raise
    
    def find_path(self, start_id: str, end_id: str, 
                  max_depth: int = 5) -> Optional[GraphPath]:
        """Find shortest path between two nodes."""
        with self.db.get_session() as session:
            try:
                query = """
                MATCH path = shortestPath((start {{id: $start_id}})-[*..{max_depth}]-(end {{id: $end_id}}))
                RETURN path
                """.format(max_depth=max_depth)
                
                result = session.run(query, start_id=start_id, end_id=end_id)
                record = result.single()
                
                if record:
                    path = record["path"]
                    nodes = [GraphNode(
                        id=node["id"],
                        type=list(node.labels)[0],
                        properties=dict(node)
                    ) for node in path.nodes]
                    
                    relationships = [GraphRelationship(
                        type=rel.type,
                        source_id=rel.start_node["id"],
                        target_id=rel.end_node["id"],
                        properties=dict(rel)
                    ) for rel in path.relationships]
                    
                    return GraphPath(
                        nodes=nodes,
                        relationships=relationships,
                        length=len(path)
                    )
                
                return None
                
            except Neo4jError as e:
                logger.error(f"Error finding path: {e}")
                raise
    
    def search_nodes(self, query: KnowledgeGraphQuery) -> List[Dict[str, Any]]:
        """Search for nodes based on criteria."""
        with self.db.get_session() as session:
            try:
                cypher_query = "MATCH (n"
                params = {}
                
                if query.node_type:
                    cypher_query += f":{query.node_type}"
                
                cypher_query += ")"
                
                # Add property filters
                where_clauses = []
                for key, value in query.properties_filter.items():
                    param_key = f"prop_{key}"
                    where_clauses.append(f"n.{key} = ${param_key}")
                    params[param_key] = value
                
                if where_clauses:
                    cypher_query += " WHERE " + " AND ".join(where_clauses)
                
                cypher_query += " RETURN n LIMIT 100"
                
                result = session.run(cypher_query, **params)
                
                nodes = []
                for record in result:
                    nodes.append(dict(record["n"]))
                
                return nodes
                
            except Neo4jError as e:
                logger.error(f"Error searching nodes: {e}")
                raise
    
    def full_text_search(self, query_text: str, 
                        node_type: Optional[NodeType] = None) -> List[Dict[str, Any]]:
        """Perform full-text search on indexed properties."""
        with self.db.get_session() as session:
            try:
                if node_type == NodeType.DOCUMENT:
                    index_name = "document_search"
                elif node_type == NodeType.PROJECT:
                    index_name = "project_search"
                else:
                    # Search all text indexes
                    results = []
                    for idx in ["document_search", "project_search"]:
                        results.extend(self._search_index(session, idx, query_text))
                    return results
                
                return self._search_index(session, index_name, query_text)
                
            except Neo4jError as e:
                logger.error(f"Error in full-text search: {e}")
                raise
    
    def _search_index(self, session, index_name: str, query_text: str) -> List[Dict[str, Any]]:
        """Search a specific full-text index."""
        query = f"""
        CALL db.index.fulltext.queryNodes('{index_name}', $query_text)
        YIELD node, score
        RETURN node, score
        ORDER BY score DESC
        LIMIT 50
        """
        
        result = session.run(query, query_text=query_text)
        
        results = []
        for record in result:
            node_data = dict(record["node"])
            node_data["_score"] = record["score"]
            results.append(node_data)
        
        return results
    
    def get_related_nodes(self, node_id: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """Get all nodes related to a given node up to max_depth."""
        with self.db.get_session() as session:
            try:
                query = """
                MATCH (start {{id: $node_id}})
                MATCH (start)-[*1..{max_depth}]-(related)
                WHERE related.id <> $node_id
                RETURN DISTINCT related
                LIMIT 100
                """.format(max_depth=max_depth)
                
                result = session.run(query, node_id=node_id)
                
                nodes = []
                for record in result:
                    nodes.append(dict(record["related"]))
                
                return nodes
                
            except Neo4jError as e:
                logger.error(f"Error getting related nodes: {e}")
                raise
    
    def create_document_uploaded_event(self, document_id: int, user_id: int, 
                                     project_id: int, experiment_id: Optional[int] = None):
        """Create graph nodes and relationships when a document is uploaded."""
        try:
            # Create or update user node
            user_node = UserNode(user_id=user_id, username=f"user_{user_id}", 
                               email=f"user_{user_id}@example.com")
            self.create_node(user_node)
            
            # Create document node
            doc_node = DocumentNode(document_id=document_id, 
                                  title=f"Document {document_id}",
                                  file_type="unknown")
            self.create_node(doc_node)
            
            # Create relationships
            # User uploaded document
            self.create_relationship(GraphRelationship(
                type=RelationType.CREATED_BY,
                source_id=doc_node.id,
                target_id=user_node.id
            ))
            
            # Document belongs to project
            if project_id:
                project_node = ProjectNode(project_id=project_id, 
                                         name=f"Project {project_id}")
                self.create_node(project_node)
                
                self.create_relationship(GraphRelationship(
                    type=RelationType.BELONGS_TO,
                    source_id=doc_node.id,
                    target_id=project_node.id
                ))
            
            # Document belongs to experiment
            if experiment_id:
                exp_node = ExperimentNode(experiment_id=experiment_id,
                                        name=f"Experiment {experiment_id}")
                self.create_node(exp_node)
                
                self.create_relationship(GraphRelationship(
                    type=RelationType.BELONGS_TO,
                    source_id=doc_node.id,
                    target_id=exp_node.id
                ))
                
        except Exception as e:
            logger.error(f"Error creating document upload event: {e}")
            raise


# Global knowledge graph service instance
knowledge_graph = KnowledgeGraphService()