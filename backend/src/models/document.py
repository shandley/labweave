"""Document model for knowledge management."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Index, CheckConstraint
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
    
    # Version control fields
    version_number = Column(Integer, default=1, nullable=False)
    is_latest = Column(Boolean, default=True, nullable=False)
    parent_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    version_comment = Column(Text, nullable=True)
    file_hash = Column(String(64), nullable=True)  # SHA256 hash for file integrity
    
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
    
    # Self-referential relationships for versioning
    parent_document = relationship("Document", remote_side=[id], backref="versions")
    
    # Table constraints
    __table_args__ = (
        # A document must belong to either a project or an experiment
        CheckConstraint(
            "(project_id IS NOT NULL AND experiment_id IS NULL) OR "
            "(project_id IS NULL AND experiment_id IS NOT NULL)",
            name="check_document_parent"
        ),
        # Ensure version consistency
        Index('idx_latest_document', 'document_type', 'project_id', 'experiment_id', 'is_latest'),
        Index('idx_document_versions', 'parent_document_id', 'version_number'),
    )