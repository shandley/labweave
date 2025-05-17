"""Simple documents endpoint for testing."""
from fastapi import APIRouter
from typing import Dict

router = APIRouter()


@router.get("/test")
async def test_documents() -> Dict[str, str]:
    """Test endpoint for documents."""
    return {"message": "Documents endpoint works!"}