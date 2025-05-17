"""Document endpoints without authentication for testing."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.v1.endpoints.auth import get_db
from src.models.document import Document as DocumentModel
from src.schemas.document import Document

router = APIRouter()


@router.get("/", response_model=List[Document])
def read_documents_noauth(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of documents without authentication."""
    documents = db.query(DocumentModel).offset(skip).limit(limit).all()
    return documents