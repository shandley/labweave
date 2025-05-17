"""Protocol schemas."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ProtocolBase(BaseModel):
    """Base protocol schema."""
    name: str
    description: Optional[str] = None
    protocol_type: Optional[str] = None
    version: str = "1.0"
    content: Optional[str] = None
    extra_metadata: Optional[str] = None


class ProtocolCreate(ProtocolBase):
    """Schema for creating a protocol."""
    author_id: int


class ProtocolUpdate(BaseModel):
    """Schema for updating a protocol."""
    name: Optional[str] = None
    description: Optional[str] = None
    protocol_type: Optional[str] = None
    version: Optional[str] = None
    content: Optional[str] = None
    extra_metadata: Optional[str] = None


class ProtocolInDBBase(ProtocolBase):
    """Base schema for protocol in database."""
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Protocol(ProtocolInDBBase):
    """Schema for protocol response."""
    pass