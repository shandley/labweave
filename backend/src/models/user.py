"""User model."""
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class User(BaseModel):
    """User model for authentication and authorization."""
    
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    experiments = relationship("Experiment", back_populates="creator")
    protocols = relationship("Protocol", back_populates="creator")
    uploaded_documents = relationship("Document", back_populates="uploader")