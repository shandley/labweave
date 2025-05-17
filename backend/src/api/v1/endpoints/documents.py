"""Document endpoints."""
import os
import hashlib
from typing import List, Optional
from pathlib import Path
import shutil

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.api.v1.endpoints.auth import get_db, get_current_user
from src.models.document import Document as DocumentModel
from src.models.user import User
from src.schemas.document import Document, DocumentCreate, DocumentUpdate, DocumentUploadResponse, DocumentVersion

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


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


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
    
    # Create subdirectory structure with versioning support
    project_dir = UPLOAD_DIR / f"project_{project_id}"
    if experiment_id:
        doc_dir = project_dir / f"experiment_{experiment_id}"
    else:
        doc_dir = project_dir / "documents"
    
    doc_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(file.filename).suffix
    base_name = Path(file.filename).stem
    unique_filename = f"{base_name}_{timestamp}{file_extension}"
    file_path = doc_dir / unique_filename
    
    # Save file and calculate hash
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_hash = calculate_file_hash(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Get file info
    file_size = os.path.getsize(file_path)
    mime_type = file.content_type
    
    # Parse tags
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    
    # Create document record with version info
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
        uploaded_by=current_user.id,
        file_hash=file_hash,
        version_number=1,
        is_latest=True
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


@router.post("/{document_id}/versions", response_model=Document)
async def upload_new_version(
    document_id: int,
    file: UploadFile = File(...),
    version_comment: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new version of an existing document."""
    # Get the latest version of the document
    current_doc = db.query(DocumentModel).filter(
        DocumentModel.id == document_id,
        DocumentModel.is_latest == True
    ).first()
    
    if not current_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Validate file type
    if not is_valid_file_type(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported formats: {', '.join(OMICS_FORMATS)}"
        )
    
    # Create version subdirectory
    base_dir = Path(current_doc.file_path).parent
    new_version = current_doc.version_number + 1
    version_dir = base_dir / f"v{new_version}"
    version_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename for new version
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(file.filename).suffix
    base_name = Path(file.filename).stem
    unique_filename = f"{base_name}_v{new_version}_{timestamp}{file_extension}"
    file_path = version_dir / unique_filename
    
    # Save file and calculate hash
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_hash = calculate_file_hash(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Update current version to not be latest
    current_doc.is_latest = False
    
    # Create new version document
    new_doc = DocumentModel(
        title=current_doc.title,
        description=current_doc.description,
        file_path=str(file_path),
        file_type=file_extension,
        file_size=os.path.getsize(file_path),
        mime_type=file.content_type,
        document_type=current_doc.document_type,
        tags=current_doc.tags,
        extra_metadata=current_doc.extra_metadata,
        project_id=current_doc.project_id,
        experiment_id=current_doc.experiment_id,
        uploaded_by=current_user.id,
        
        # Version info
        version_number=new_version,
        parent_document_id=current_doc.parent_document_id or current_doc.id,
        version_comment=version_comment,
        is_latest=True,
        file_hash=file_hash
    )
    
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    return new_doc


@router.get("/{document_id}/versions", response_model=List[DocumentVersion])
def get_document_versions(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all versions of a document."""
    # Find the original document or any version of it
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get the root document ID
    root_id = document.parent_document_id if document.parent_document_id else document.id
    
    # Get all versions including the original
    versions = db.query(DocumentModel).filter(
        (DocumentModel.id == root_id) | (DocumentModel.parent_document_id == root_id)
    ).order_by(DocumentModel.version_number).all()
    
    return versions


@router.get("/{document_id}/versions/{version_number}", response_model=Document)
def get_document_version(
    document_id: int,
    version_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific version of a document."""
    # Find the original document
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get the root document ID
    root_id = document.parent_document_id if document.parent_document_id else document.id
    
    # Find the specific version
    version = db.query(DocumentModel).filter(
        ((DocumentModel.id == root_id) | (DocumentModel.parent_document_id == root_id)) &
        (DocumentModel.version_number == version_number)
    ).first()
    
    if not version:
        raise HTTPException(status_code=404, detail=f"Version {version_number} not found")
    
    return version


@router.post("/{document_id}/restore/{version_number}", response_model=Document)
def restore_document_version(
    document_id: int,
    version_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restore a previous version of a document by creating a new version with the old content."""
    # Get the version to restore
    version_to_restore = get_document_version(document_id, version_number, current_user, db)
    
    if not version_to_restore:
        raise HTTPException(status_code=404, detail=f"Version {version_number} not found")
    
    # Get the current latest version
    current_latest = db.query(DocumentModel).filter(
        DocumentModel.parent_document_id == version_to_restore.parent_document_id,
        DocumentModel.is_latest == True
    ).first()
    
    if current_latest:
        current_latest.is_latest = False
        new_version_number = current_latest.version_number + 1
    else:
        new_version_number = version_to_restore.version_number + 1
    
    # Create new file path for restored version
    base_dir = Path(version_to_restore.file_path).parent.parent
    version_dir = base_dir / f"v{new_version_number}"
    version_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the old file to new location
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = Path(version_to_restore.file_path).name
    base_name = file_name.split('_v')[0]  # Remove version info from name
    file_extension = Path(file_name).suffix
    new_filename = f"{base_name}_v{new_version_number}_{timestamp}{file_extension}"
    new_file_path = version_dir / new_filename
    
    try:
        shutil.copy2(version_to_restore.file_path, new_file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore file: {str(e)}")
    
    # Create new document version
    restored_doc = DocumentModel(
        title=version_to_restore.title,
        description=version_to_restore.description,
        file_path=str(new_file_path),
        file_type=version_to_restore.file_type,
        file_size=version_to_restore.file_size,
        mime_type=version_to_restore.mime_type,
        document_type=version_to_restore.document_type,
        tags=version_to_restore.tags,
        extra_metadata=version_to_restore.extra_metadata,
        project_id=version_to_restore.project_id,
        experiment_id=version_to_restore.experiment_id,
        uploaded_by=current_user.id,
        
        # Version info
        version_number=new_version_number,
        parent_document_id=version_to_restore.parent_document_id or version_to_restore.id,
        version_comment=f"Restored from version {version_number}",
        is_latest=True,
        file_hash=version_to_restore.file_hash
    )
    
    db.add(restored_doc)
    db.commit()
    db.refresh(restored_doc)
    
    return restored_doc


@router.get("/", response_model=List[Document])
def read_documents(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    experiment_id: Optional[int] = Query(None, description="Filter by experiment ID"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    latest_only: bool = Query(True, description="Show only latest versions"),
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
    
    if latest_only:
        query = query.filter(DocumentModel.is_latest == True)
    
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
    cascade: bool = Query(False, description="Delete all versions"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document and optionally all its versions."""
    document = db.query(DocumentModel).filter(DocumentModel.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    documents_to_delete = []
    
    if cascade:
        # Get all versions
        root_id = document.parent_document_id if document.parent_document_id else document.id
        all_versions = db.query(DocumentModel).filter(
            (DocumentModel.id == root_id) | (DocumentModel.parent_document_id == root_id)
        ).all()
        documents_to_delete = all_versions
    else:
        documents_to_delete = [document]
    
    # Delete files and records
    for doc in documents_to_delete:
        if doc.file_path and os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception as e:
                print(f"Warning: Failed to delete file {doc.file_path}: {str(e)}")
        
        db.delete(doc)
    
    db.commit()
    
    return {"detail": f"Deleted {len(documents_to_delete)} document(s) successfully"}