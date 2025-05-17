"""Project endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.v1.endpoints.auth import get_db
from src.models.project import Project as ProjectModel
from src.schemas.project import Project, ProjectCreate

router = APIRouter()


@router.post("/", response_model=Project)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project."""
    db_project = ProjectModel(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/", response_model=List[Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of projects."""
    projects = db.query(ProjectModel).offset(skip).limit(limit).all()
    return projects