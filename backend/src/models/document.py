"""Document model for knowledge management."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.models.base import Base


class Document(Base):
    """Document model for storing research documents and omics data files."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(String(500))  # Path to the actual file
    file_type = Column(String(50))  # PDF, FASTQ, FASTA, SAM, BAM, etc.
    file_size = Column(Integer)  # File size in bytes
    mime_type = Column(String(100))
    
    # Document metadata
    document_type = Column(String(50))  # research_paper, protocol, dataset, analysis, etc.
    tags = Column(JSON)  # List of tags for categorization
    extra_metadata = Column(JSON)  # Flexible metadata storage
    
    # Relationships
    project_id = Column(Integer, ForeignKey("projects.id"))
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    experiment = relationship("Experiment", back_populates="documents")
    uploader = relationship("User", back_populates="uploaded_documents")