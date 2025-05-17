"""Sample endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.v1.endpoints.auth import get_db
from src.models.sample import Sample as SampleModel
from src.schemas.sample import Sample, SampleCreate, SampleUpdate

router = APIRouter()


@router.post("/", response_model=Sample)
def create_sample(sample: SampleCreate, db: Session = Depends(get_db)):
    """Create a new sample."""
    db_sample = SampleModel(**sample.dict())
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample


@router.get("/", response_model=List[Sample])
def read_samples(
    skip: int = 0, 
    limit: int = 100,
    experiment_id: Optional[int] = Query(None, description="Filter by experiment ID"),
    sample_type: Optional[str] = Query(None, description="Filter by sample type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get list of samples with optional filtering."""
    query = db.query(SampleModel)
    
    if experiment_id is not None:
        query = query.filter(SampleModel.experiment_id == experiment_id)
    
    if sample_type is not None:
        query = query.filter(SampleModel.sample_type == sample_type)
    
    if status is not None:
        query = query.filter(SampleModel.status == status)
    
    samples = query.offset(skip).limit(limit).all()
    return samples


@router.get("/{sample_id}", response_model=Sample)
def read_sample(sample_id: int, db: Session = Depends(get_db)):
    """Get a specific sample by ID."""
    sample = db.query(SampleModel).filter(SampleModel.id == sample_id).first()
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@router.patch("/{sample_id}", response_model=Sample)
def update_sample(
    sample_id: int,
    sample_update: SampleUpdate,
    db: Session = Depends(get_db)
):
    """Update a sample."""
    sample = db.query(SampleModel).filter(SampleModel.id == sample_id).first()
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    update_data = sample_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sample, field, value)
    
    db.commit()
    db.refresh(sample)
    return sample


@router.delete("/{sample_id}")
def delete_sample(sample_id: int, db: Session = Depends(get_db)):
    """Delete a sample."""
    sample = db.query(SampleModel).filter(SampleModel.id == sample_id).first()
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    db.delete(sample)
    db.commit()
    return {"detail": "Sample deleted successfully"}