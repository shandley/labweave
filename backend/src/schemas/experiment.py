"""Experiment schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ExperimentBase(BaseModel):
    """Base experiment schema."""
    name: str
    description: Optional[str] = None
    status: str = "planned"
    experiment_type: Optional[str] = None
    extra_metadata: Optional[str] = None
    results: Optional[str] = None


class ExperimentCreate(ExperimentBase):
    """Schema for creating an experiment."""
    project_id: int
    creator_id: int
    protocol_id: Optional[int] = None


class ExperimentUpdate(ExperimentBase):
    """Schema for updating an experiment."""
    name: Optional[str] = None
    status: Optional[str] = None


class ExperimentInDBBase(ExperimentBase):
    """Base schema for experiment in database."""
    id: int
    project_id: int
    creator_id: int
    protocol_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Experiment(ExperimentInDBBase):
    """Schema for experiment response."""
    pass