"""Debug script to check API routes."""
import sys
sys.path.insert(0, '.')

from src.api.v1.api import api_router
from src.main import app

print("Main app routes:")
for route in app.routes:
    if hasattr(route, 'path'):
        print(f"  {route.path}")

print("\nAPI router routes:")
for route in api_router.routes:
    if hasattr(route, 'path'):
        print(f"  {route.path}")

print("\nDocument endpoints that should be included:")
from src.api.v1.endpoints.documents import router as doc_router
for route in doc_router.routes:
    if hasattr(route, 'path'):
        print(f"  {route.path}")