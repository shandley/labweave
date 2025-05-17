"""Document schemas."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, validator


class DocumentBase(BaseModel):
    """Base document schema."""
    title: str
    description: Optional[str] = None
    file_type: Optional[str] = None
    document_type: Optional[str] = None
    tags: Optional[List[str]] = []
    extra_metadata: Optional[Dict[str, Any]] = {}


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    project_id: int
    experiment_id: Optional[int] = None


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""
    title: Optional[str] = None
    description: Optional[str] = None
    document_type: Optional[str] = None
    tags: Optional[List[str]] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class DocumentUploadResponse(BaseModel):
    """Response after file upload."""
    id: int
    file_path: str
    file_size: int
    mime_type: str


class DocumentInDBBase(DocumentBase):
    """Base schema for document in database."""
    id: int
    file_path: Optional[str]
    file_size: Optional[int]
    mime_type: Optional[str]
    project_id: int
    experiment_id: Optional[int]
    uploaded_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Document(DocumentInDBBase):
    """Schema for document response."""
    pass