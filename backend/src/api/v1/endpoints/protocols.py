"""Protocol endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.v1.endpoints.auth import get_db
from src.models.protocol import Protocol as ProtocolModel
from src.schemas.protocol import Protocol, ProtocolCreate, ProtocolUpdate

router = APIRouter()


@router.post("/", response_model=Protocol)
def create_protocol(protocol: ProtocolCreate, db: Session = Depends(get_db)):
    """Create a new protocol."""
    db_protocol = ProtocolModel(**protocol.dict())
    db.add(db_protocol)
    db.commit()
    db.refresh(db_protocol)
    return db_protocol


@router.get("/", response_model=List[Protocol])
def read_protocols(
    skip: int = 0, 
    limit: int = 100,
    protocol_type: Optional[str] = Query(None, description="Filter by protocol type"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    db: Session = Depends(get_db)
):
    """Get list of protocols with optional filtering."""
    query = db.query(ProtocolModel)
    
    if protocol_type is not None:
        query = query.filter(ProtocolModel.protocol_type == protocol_type)
    
    if author_id is not None:
        query = query.filter(ProtocolModel.author_id == author_id)
    
    protocols = query.offset(skip).limit(limit).all()
    return protocols


@router.get("/{protocol_id}", response_model=Protocol)
def read_protocol(protocol_id: int, db: Session = Depends(get_db)):
    """Get a specific protocol by ID."""
    protocol = db.query(ProtocolModel).filter(ProtocolModel.id == protocol_id).first()
    if protocol is None:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return protocol


@router.patch("/{protocol_id}", response_model=Protocol)
def update_protocol(
    protocol_id: int,
    protocol_update: ProtocolUpdate,
    db: Session = Depends(get_db)
):
    """Update a protocol."""
    protocol = db.query(ProtocolModel).filter(ProtocolModel.id == protocol_id).first()
    if protocol is None:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    update_data = protocol_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(protocol, field, value)
    
    db.commit()
    db.refresh(protocol)
    return protocol


@router.delete("/{protocol_id}")
def delete_protocol(protocol_id: int, db: Session = Depends(get_db)):
    """Delete a protocol."""
    protocol = db.query(ProtocolModel).filter(ProtocolModel.id == protocol_id).first()
    if protocol is None:
        raise HTTPException(status_code=404, detail="Protocol not found")
    
    db.delete(protocol)
    db.commit()
    return {"detail": "Protocol deleted successfully"}