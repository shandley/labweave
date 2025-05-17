"""Document endpoints."""
import os
from typing import List, Optional
from pathlib import Path
import shutil

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.api.v1.endpoints.auth import get_db, get_current_user
from src.models.document import Document as DocumentModel
from src.models.user import User
from src.schemas.document import Document, DocumentCreate, DocumentUpdate, DocumentUploadResponse

router = APIRouter()

# Configure upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Supported omics file formats
OMICS_FORMATS = {
    ".fastq", ".fq", ".fastq.gz", ".fq.gz",  # Sequencing reads
    ".fasta", ".fa", ".fna", ".fasta.gz",    # Sequences
    ".sam", ".bam",                          # Alignments
    ".vcf", ".vcf.gz",                       # Variant calls
    ".bed", ".gff", ".gtf",                  # Annotations
    ".nwk", ".tree", ".nxs",                 # Phylogenetic trees
    ".tsv", ".csv", ".txt",                  # Count tables, metadata
    ".pdf",                                  # Documentation
}


def is_valid_file_type(filename: str) -> bool:
    """Check if file type is supported."""
    return any(filename.lower().endswith(fmt) for fmt in OMICS_FORMATS)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    project_id: int = Form(...),
    experiment_id: Optional[int] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated tags
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document file."""
    # Validate file type
    if not is_valid_file_type(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported formats: {', '.join(OMICS_FORMATS)}"
        )
    
    # Create subdirectory structure
    project_dir = UPLOAD_DIR / f"project_{project_id}"
    if experiment_id:
        upload_dir = project_dir / f"experiment_{experiment_id}"
    else:
        upload_dir = project_dir / "documents"
    
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(file.filename).suffix
    base_name = Path(file.filename).stem
    unique_filename = f"{base_name}_{timestamp}{file_extension}"
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Get file info
    file_size = os.path.getsize(file_path)
    mime_type = file.content_type
    
    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    
    # Create document record
    db_document = DocumentModel(
        title=title,
        description=description,
        file_path=str(file_path),
        file_type=file_extension,
        file_size=file_size,
        mime_type=mime_type,
        document_type=document_type,
        tags=tag_list,
        project_id=project_id,
        experiment_id=experiment_id,
        uploaded_by=current_user.id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return DocumentUploadResponse(
        id=db_document.id,
        file_path=db_document.file_path,
        file_size=db_document.file_size,
        mime_type=db_document.mime_type
    )


@router.get("/", response_model=List[Document])
def read_documents(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    experiment_id: Optional[int] = Query(None, description="Filter by experiment ID"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of documents with optional filtering."""
    query = db.query(DocumentModel)
    
    # Apply filters
    if project_id is not None:
        query = query.filter(DocumentModel.project_id == project_id)
    
    if experiment_id is not None:
        query = query.filter(DocumentModel.experiment_id == experiment_id)
    
    if document_type is not None:
        query = query.filter(DocumentModel.document_type == document_type)
    
    if file_type is not None:
        query = query.filter(DocumentModel.file_type == file_type)
    
    documents = query.offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=Document)
def read_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document by ID."""
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a document file."""
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=document.file_path,
        filename=os.path.basename(document.file_path),
        media_type=document.mime_type
    )


@router.patch("/{document_id}", response_model=Document)
def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a document's metadata."""
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    update_data = document_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document and its file."""
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from disk
    if document.file_path and os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except Exception as e:
            print(f"Warning: Failed to delete file {document.file_path}: {str(e)}")
    
    # Delete database record
    db.delete(document)
    db.commit()
    
    return {"detail": "Document deleted successfully"}