#!/usr/bin/env python3
"""Pre-flight validation system for LabWeave backend."""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
import importlib.util
import re

class PreflightValidator:
    """Validate the codebase before starting the server."""
    
    def __init__(self):
        self.backend_dir = Path(__file__).parent
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def check_sqlalchemy_reserved_words(self) -> bool:
        """Check for SQLAlchemy reserved column names."""
        reserved_words = {'metadata', 'query', 'registry', 'class_'}
        issues = []
        
        models_dir = self.backend_dir / "src" / "models"
        for model_file in models_dir.glob("*.py"):
            if model_file.name == "__init__.py":
                continue
                
            content = model_file.read_text()
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id in reserved_words:
                            if isinstance(node.value, ast.Call):
                                func_name = getattr(node.value.func, 'id', '')
                                if func_name == 'Column':
                                    issues.append(
                                        f"{model_file.name}: Reserved word '{target.id}' used as column name"
                                    )
        
        if issues:
            self.errors.extend(issues)
            return False
        return True
    
    def check_model_schema_consistency(self) -> bool:
        """Ensure model fields match schema fields."""
        issues = []
        
        # Map models to schemas
        model_schema_map = {
            'project': 'project',
            'experiment': 'experiment',
            'user': 'user',
            'protocol': 'protocol',
            'sample': 'sample'
        }
        
        for model_name, schema_name in model_schema_map.items():
            model_file = self.backend_dir / "src" / "models" / f"{model_name}.py"
            schema_file = self.backend_dir / "src" / "schemas" / f"{schema_name}.py"
            
            if not model_file.exists() or not schema_file.exists():
                continue
            
            # Extract column names from model
            model_content = model_file.read_text()
            model_columns = set(re.findall(r'(\w+)\s*=\s*Column', model_content))
            
            # Extract field names from schema (more comprehensive pattern)
            schema_content = schema_file.read_text()
            # Find all field definitions including EmailStr and other types
            schema_fields = set(re.findall(r'(\w+):\s*(?:Optional\[)?(?:\w+)', schema_content))
            
            # Common fields that are typically in base models or handled differently
            ignored_fields = {'id', 'created_at', 'updated_at', 'password', 'hashed_password'}
            
            # Check for critical mismatches only
            model_only = model_columns - schema_fields - ignored_fields
            
            # Only report actual issues, not warnings for schema-only fields
            critical_model_only = {f for f in model_only if f not in {'email', 'username'}}
            
            if critical_model_only:
                issues.append(
                    f"{model_name}: Model has fields not in schema: {critical_model_only}"
                )
        
        if issues:
            self.errors.extend(issues)
            return False
        return True
    
    def check_import_cycles(self) -> bool:
        """Detect circular imports."""
        def get_imports(file_path: Path) -> Set[str]:
            content = file_path.read_text()
            imports = set()
            
            # Find all imports
            import_patterns = [
                r'from\s+([\w.]+)\s+import',
                r'import\s+([\w.]+)'
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                imports.update(matches)
            
            return imports
        
        # Build import graph
        import_graph: Dict[str, Set[str]] = {}
        src_dir = self.backend_dir / "src"
        
        for py_file in src_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            module_path = str(py_file.relative_to(src_dir)).replace('/', '.').replace('.py', '')
            imports = get_imports(py_file)
            import_graph[module_path] = {
                imp for imp in imports 
                if imp.startswith('src.')
            }
        
        # Simple cycle detection (DFS)
        def has_cycle(node: str, visited: Set[str], path: List[str]) -> Optional[List[str]]:
            if node in path:
                cycle_start = path.index(node)
                return path[cycle_start:] + [node]
            
            if node in visited:
                return None
            
            visited.add(node)
            path.append(node)
            
            for neighbor in import_graph.get(node, []):
                cycle = has_cycle(neighbor, visited, path.copy())
                if cycle:
                    return cycle
            
            return None
        
        visited = set()
        for module in import_graph:
            if module not in visited:
                cycle = has_cycle(module, visited, [])
                if cycle:
                    self.errors.append(f"Circular import detected: {' -> '.join(cycle)}")
                    return False
        
        return True
    
    def check_pydantic_compatibility(self) -> bool:
        """Check for Pydantic v2 compatibility issues."""
        issues = []
        
        # Check for old imports
        config_file = self.backend_dir / "src" / "config.py"
        if config_file.exists():
            content = config_file.read_text()
            if "from pydantic import BaseSettings" in content:
                issues.append("config.py: Using old Pydantic import")
        
        # Check for Config class setup
        for py_file in (self.backend_dir / "src").rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            content = py_file.read_text()
            if "class Config:" in content and "from_attributes" not in content:
                if "orm_mode" in content:
                    self.warnings.append(
                        f"{py_file.name}: Using deprecated 'orm_mode' instead of 'from_attributes'"
                    )
        
        if issues:
            self.errors.extend(issues)
            return False
        return True
    
    def check_environment_setup(self) -> bool:
        """Check if environment is properly configured."""
        issues = []
        
        # Check for .env file
        env_file = self.backend_dir / ".env"
        if not env_file.exists():
            issues.append(".env file missing")
        else:
            content = env_file.read_text()
            required_vars = [
                'DATABASE_URL',
                'SECRET_KEY',
            ]
            
            for var in required_vars:
                if var not in content:
                    issues.append(f"Missing required environment variable: {var}")
        
        # Check for required directories
        required_dirs = ['logs', 'uploads']
        for dir_name in required_dirs:
            dir_path = self.backend_dir / dir_name
            if not dir_path.exists():
                self.warnings.append(f"Directory '{dir_name}' missing (will be created)")
        
        if issues:
            self.errors.extend(issues)
            return False
        return True
    
    def run_all_checks(self) -> bool:
        """Run all validation checks."""
        print("🔍 Running pre-flight checks...")
        
        checks = [
            ("SQLAlchemy reserved words", self.check_sqlalchemy_reserved_words),
            ("Model-Schema consistency", self.check_model_schema_consistency),
            ("Import cycles", self.check_import_cycles),
            ("Pydantic compatibility", self.check_pydantic_compatibility),
            ("Environment setup", self.check_environment_setup),
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            print(f"\n🔸 Checking {check_name}...")
            passed = check_func()
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"   {status}")
            all_passed &= passed
        
        print("\n" + "="*50)
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if all_passed and not self.errors:
            print("\n✅ All pre-flight checks passed!")
        else:
            print("\n❌ Pre-flight checks failed. Please fix errors before starting.")
        
        return all_passed and not self.errors


if __name__ == "__main__":
    validator = PreflightValidator()
    success = validator.run_all_checks()
    sys.exit(0 if success else 1)