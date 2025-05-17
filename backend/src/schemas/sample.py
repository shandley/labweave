"""Sample schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class SampleBase(BaseModel):
    """Base sample schema."""
    name: str
    description: Optional[str] = None
    sample_type: Optional[str] = None
    source: Optional[str] = None
    status: str = "collected"
    storage_location: Optional[str] = None
    extra_metadata: Optional[str] = None


class SampleCreate(SampleBase):
    """Schema for creating a sample."""
    experiment_id: int
    collected_by: int


class SampleUpdate(BaseModel):
    """Schema for updating a sample."""
    name: Optional[str] = None
    description: Optional[str] = None
    sample_type: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    storage_location: Optional[str] = None
    extra_metadata: Optional[str] = None


class SampleInDBBase(SampleBase):
    """Base schema for sample in database."""
    id: int
    experiment_id: int
    collected_by: int
    collected_at: Optional[datetime]
    processed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Sample(SampleInDBBase):
    """Schema for sample response."""
    pass