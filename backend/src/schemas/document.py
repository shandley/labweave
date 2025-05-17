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
    
    # Version control fields
    version_number: int = 1
    is_latest: bool = True
    parent_document_id: Optional[int] = None
    version_comment: Optional[str] = None
    file_hash: Optional[str] = None
    
    class Config:
        from_attributes = True


class Document(DocumentInDBBase):
    """Schema for document response."""
    pass


class DocumentVersion(BaseModel):
    """Schema for document version response."""
    id: int
    version_number: int
    is_latest: bool
    version_comment: Optional[str]
    created_at: datetime
    uploaded_by: int
    file_size: Optional[int]
    file_hash: Optional[str]
    
    class Config:
        from_attributes = True