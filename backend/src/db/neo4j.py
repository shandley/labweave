"""Neo4j database connection and session management."""
import logging
from contextlib import contextmanager
from typing import Generator

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from src.config import settings

logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Handle Neo4j database connection."""
    
    def __init__(self):
        """Initialize Neo4j connection."""
        self._driver = None
        self._connect()
    
    def _connect(self):
        """Create Neo4j driver connection."""
        try:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j")
        except ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to Neo4j: {e}")
            raise
    
    def close(self):
        """Close Neo4j connection."""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed")
    
    @contextmanager
    def get_session(self):
        """Get Neo4j session as context manager."""
        if not self._driver:
            self._connect()
        
        session = self._driver.session()
        try:
            yield session
        finally:
            session.close()
    
    def check_connection(self) -> bool:
        """Check if Neo4j is connected and responsive."""
        try:
            with self.get_session() as session:
                result = session.run("RETURN 1")
                result.single()
                return True
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False


# Global Neo4j connection instance
neo4j_db = Neo4jConnection()


def get_neo4j_db() -> Neo4jConnection:
    """Get Neo4j database connection."""
    return neo4j_db


def init_neo4j_indexes():
    """Initialize Neo4j indexes and constraints."""
    with neo4j_db.get_session() as session:
        try:
            # Create indexes for better performance
            indexes = [
                "CREATE INDEX project_id IF NOT EXISTS FOR (p:Project) ON (p.id)",
                "CREATE INDEX experiment_id IF NOT EXISTS FOR (e:Experiment) ON (e.id)",
                "CREATE INDEX document_id IF NOT EXISTS FOR (d:Document) ON (d.id)",
                "CREATE INDEX user_id IF NOT EXISTS FOR (u:User) ON (u.id)",
                "CREATE INDEX sample_id IF NOT EXISTS FOR (s:Sample) ON (s.id)",
                "CREATE INDEX protocol_id IF NOT EXISTS FOR (p:Protocol) ON (p.id)",
                
                # Full-text search indexes
                "CREATE FULLTEXT INDEX document_search IF NOT EXISTS FOR (d:Document) ON EACH [d.title, d.description]",
                "CREATE FULLTEXT INDEX project_search IF NOT EXISTS FOR (p:Project) ON EACH [p.name, p.description]",
            ]
            
            for index in indexes:
                session.run(index)
                logger.info(f"Created index: {index}")
            
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT project_id_unique IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT experiment_id_unique IF NOT EXISTS FOR (e:Experiment) REQUIRE e.id IS UNIQUE",
                "CREATE CONSTRAINT document_id_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
                "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
                "CREATE CONSTRAINT sample_id_unique IF NOT EXISTS FOR (s:Sample) REQUIRE s.id IS UNIQUE",
                "CREATE CONSTRAINT protocol_id_unique IF NOT EXISTS FOR (p:Protocol) REQUIRE p.id IS UNIQUE",
            ]
            
            for constraint in constraints:
                session.run(constraint)
                logger.info(f"Created constraint: {constraint}")
                
        except Exception as e:
            logger.error(f"Error initializing Neo4j indexes: {e}")
            raise