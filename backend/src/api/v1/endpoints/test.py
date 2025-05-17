"""Test endpoint to debug routing."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def test_endpoint():
    """Simple test endpoint."""
    return {"message": "Test endpoint works!"}