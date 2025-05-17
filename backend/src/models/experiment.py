"""Experiment model."""
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Experiment(BaseModel):
    """Experiment model for tracking research experiments."""
    
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="planned")  # planned, in_progress, completed, failed
    experiment_type = Column(String)  # metagenomics, transcriptomics, etc.
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    protocol_id = Column(Integer, ForeignKey("protocols.id"))
    
    # Relationships
    project = relationship("Project", back_populates="experiments")
    creator = relationship("User", back_populates="experiments")
    protocol = relationship("Protocol")
    samples = relationship("Sample", back_populates="experiment")
    
    # Metadata and results
    metadata = Column(Text)  # JSON string
    results = Column(Text)  # JSON string