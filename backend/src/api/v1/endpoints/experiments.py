"""Experiment endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.v1.endpoints.auth import get_db
from src.models.experiment import Experiment as ExperimentModel
from src.schemas.experiment import Experiment, ExperimentCreate

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
def read_experiments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of experiments."""
    experiments = db.query(ExperimentModel).offset(skip).limit(limit).all()
    return experiments