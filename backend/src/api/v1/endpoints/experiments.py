"""Experiment endpoints."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.v1.endpoints.auth import get_db
from src.models.experiment import Experiment as ExperimentModel
from src.schemas.experiment import Experiment, ExperimentCreate, ExperimentUpdate

router = APIRouter()


@router.post("/", response_model=Experiment)
def create_experiment(experiment: ExperimentCreate, db: Session = Depends(get_db)):
    """Create a new experiment."""
    db_experiment = ExperimentModel(**experiment.dict())
    db.add(db_experiment)
    db.commit()
    db.refresh(db_experiment)
    return db_experiment


@router.get("/", response_model=List[Experiment])
def read_experiments(
    skip: int = 0, 
    limit: int = 100,
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get list of experiments with optional filtering."""
    query = db.query(ExperimentModel)
    
    if project_id is not None:
        query = query.filter(ExperimentModel.project_id == project_id)
    
    if status is not None:
        query = query.filter(ExperimentModel.status == status)
    
    experiments = query.offset(skip).limit(limit).all()
    return experiments


@router.get("/{experiment_id}", response_model=Experiment)
def read_experiment(experiment_id: int, db: Session = Depends(get_db)):
    """Get a specific experiment by ID."""
    experiment = db.query(ExperimentModel).filter(ExperimentModel.id == experiment_id).first()
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@router.patch("/{experiment_id}", response_model=Experiment)
def update_experiment(
    experiment_id: int,
    experiment_update: ExperimentUpdate,
    db: Session = Depends(get_db)
):
    """Update an experiment."""
    experiment = db.query(ExperimentModel).filter(ExperimentModel.id == experiment_id).first()
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    update_data = experiment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(experiment, field, value)
    
    db.commit()
    db.refresh(experiment)
    return experiment


@router.delete("/{experiment_id}")
def delete_experiment(experiment_id: int, db: Session = Depends(get_db)):
    """Delete an experiment."""
    experiment = db.query(ExperimentModel).filter(ExperimentModel.id == experiment_id).first()
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    db.delete(experiment)
    db.commit()
    return {"detail": "Experiment deleted successfully"}