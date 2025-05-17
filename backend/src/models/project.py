"""Project model."""
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Project(BaseModel):
    """Project model for organizing research work."""
    
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="active")  # active, archived, completed
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    experiments = relationship("Experiment", back_populates="project")
    documents = relationship("Document", back_populates="project")
    
    # Additional data stored as JSON
    extra_metadata = Column(Text)  # JSON string for now, can migrate to JSONB later