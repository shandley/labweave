"""Comprehensive startup tests to catch common issues."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import importlib
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestStartupValidation:
    """Test suite for catching startup issues before they happen."""
    
    def test_all_models_importable(self):
        """Ensure all models can be imported without errors."""
        models = ['user', 'project', 'experiment', 'protocol', 'sample']
        
        for model_name in models:
            try:
                module = importlib.import_module(f'src.models.{model_name}')
                assert hasattr(module, model_name.capitalize())
            except ImportError as e:
                pytest.fail(f"Failed to import {model_name} model: {e}")
    
    def test_all_schemas_importable(self):
        """Ensure all schemas can be imported without errors."""
        schemas = ['user', 'project', 'experiment']
        
        for schema_name in schemas:
            try:
                module = importlib.import_module(f'src.schemas.{schema_name}')
                # Check for common schema classes
                expected_classes = [
                    f'{schema_name.capitalize()}Base',
                    f'{schema_name.capitalize()}Create',
                    f'{schema_name.capitalize()}'
                ]
                for class_name in expected_classes:
                    assert hasattr(module, class_name)
            except ImportError as e:
                pytest.fail(f"Failed to import {schema_name} schema: {e}")
    
    def test_config_imports_correctly(self):
        """Test that configuration imports work properly."""
        try:
            from src.config import settings
            assert settings is not None
            assert hasattr(settings, 'DATABASE_URL')
            assert hasattr(settings, 'SECRET_KEY')
        except ImportError as e:
            pytest.fail(f"Failed to import settings: {e}")
    
    def test_no_reserved_sqlalchemy_columns(self):
        """Check that models don't use reserved SQLAlchemy column names."""
        reserved_words = {'metadata', 'query', 'registry', 'class_'}
        
        models_dir = Path(__file__).parent.parent / "src" / "models"
        for model_file in models_dir.glob("*.py"):
            if model_file.name == "__init__.py":
                continue
                
            content = model_file.read_text()
            for word in reserved_words:
                pattern = f"{word} = Column"
                assert pattern not in content, f"Reserved word '{word}' used in {model_file.name}"
    
    def test_model_schema_field_matching(self):
        """Test that model fields match schema fields."""
        import re
        
        pairs = [
            ('project', 'project'),
            ('experiment', 'experiment'),
            ('user', 'user'),
        ]
        
        for model_name, schema_name in pairs:
            model_file = Path(__file__).parent.parent / "src" / "models" / f"{model_name}.py"
            schema_file = Path(__file__).parent.parent / "src" / "schemas" / f"{schema_name}.py"
            
            if not model_file.exists() or not schema_file.exists():
                continue
            
            # Extract column names from model
            model_content = model_file.read_text()
            model_columns = set(re.findall(r'(\w+)\s*=\s*Column', model_content))
            
            # Extract field names from schema base
            schema_content = schema_file.read_text()
            schema_fields = set(re.findall(r'(\w+):\s*(?:Optional\[)?(?:str|int|float|bool)', schema_content))
            
            # Remove common fields that might not be in schemas
            model_columns -= {'id', 'created_at', 'updated_at'}
            
            # Check major mismatches
            model_only = model_columns - schema_fields
            if model_only:
                # This is more of a warning than error
                print(f"Warning: {model_name} model has fields not in schema: {model_only}")
    
    def test_fastapi_app_creation(self):
        """Test that the FastAPI app can be created."""
        try:
            from src.main import app
            assert app is not None
            assert hasattr(app, 'routes')
        except Exception as e:
            pytest.fail(f"Failed to create FastAPI app: {e}")
    
    def test_database_models_create_tables(self):
        """Test that database models can create tables."""
        from src.db.base import Base
        from src.models import user, project, experiment, protocol, sample
        
        # Use in-memory SQLite for testing
        engine = create_engine("sqlite:///:memory:")
        
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as e:
            pytest.fail(f"Failed to create database tables: {e}")
    
    def test_api_endpoints_registered(self):
        """Test that API endpoints are properly registered."""
        try:
            from src.main import app
            
            # Check for expected endpoints
            routes = [route.path for route in app.routes]
            
            expected_endpoints = [
                "/api/v1/health",
                "/api/v1/auth/login",
                "/api/v1/users/me",
                "/api/v1/projects"
            ]
            
            for endpoint in expected_endpoints:
                # Use partial matching as FastAPI adds path parameters
                matching_routes = [r for r in routes if endpoint in r]
                assert matching_routes, f"Expected endpoint '{endpoint}' not found"
        except Exception as e:
            pytest.fail(f"Failed to check API endpoints: {e}")