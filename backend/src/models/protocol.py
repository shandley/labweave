"""Protocol model."""
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Protocol(BaseModel):
    """Protocol model for experimental procedures."""
    
    title = Column(String, nullable=False)
    description = Column(Text)
    version = Column(String, default="1.0")
    status = Column(String, default="draft")  # draft, approved, deprecated
    
    # Markdown content
    content = Column(Text, nullable=False)
    
    # Foreign keys
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("protocols.id"))  # For versioning
    
    # Relationships
    creator = relationship("User", back_populates="protocols")
    parent = relationship("Protocol", remote_side="Protocol.id")
    
    # Extra data
    extra_metadata = Column(Text)  # JSON string
    tags = Column(Text)  # Comma-separated tags for now