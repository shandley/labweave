"""Project schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str
    description: Optional[str] = None
    status: str = "active"
    extra_metadata: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    owner_id: int


class ProjectUpdate(ProjectBase):
    """Schema for updating a project."""
    name: Optional[str] = None
    status: Optional[str] = None


class ProjectInDBBase(ProjectBase):
    """Base schema for project in database."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Project(ProjectInDBBase):
    """Schema for project response."""
    pass