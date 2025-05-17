#!/usr/bin/env python3
"""Automated error detection and fixing system for LabWeave backend."""

import subprocess
import re
import sys
import time
from pathlib import Path
from typing import List, Tuple, Optional
import ast

class AutomatedFixer:
    """Automatically detect and fix common startup errors."""
    
    def __init__(self, max_attempts: int = 5):
        self.max_attempts = max_attempts
        self.backend_dir = Path(__file__).parent
        self.fixes_applied = []
        
    def run_server_test(self) -> Tuple[bool, str]:
        """Try to start the server and capture any errors."""
        try:
            # Use virtual environment if it exists
            venv_python = self.backend_dir / "venv" / "bin" / "python"
            if not venv_python.exists():
                venv_python = self.backend_dir / "venv" / "Scripts" / "python.exe"  # Windows
            
            python_cmd = str(venv_python) if venv_python.exists() else sys.executable
            
            # Test import without actually starting server
            result = subprocess.run(
                [python_cmd, "-c", "from src.main import app; print('Import successful')"],
                capture_output=True,
                text=True,
                cwd=self.backend_dir,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, "Server imports successful"
            else:
                return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Import test timeout"
        except Exception as e:
            return False, str(e)
    
    def fix_sqlalchemy_metadata_conflict(self, error_text: str) -> bool:
        """Fix SQLAlchemy metadata naming conflicts."""
        if "Attribute name 'metadata' is reserved" not in error_text:
            return False
            
        print("🔧 Fixing SQLAlchemy metadata naming conflict...")
        
        # Find all model files
        models_dir = self.backend_dir / "src" / "models"
        fixed_files = []
        
        for model_file in models_dir.glob("*.py"):
            if model_file.name == "__init__.py":
                continue
                
            content = model_file.read_text()
            if "metadata = Column" in content:
                new_content = content.replace(
                    "metadata = Column",
                    "extra_metadata = Column"
                ).replace(
                    "# Metadata",
                    "# Extra data"
                )
                model_file.write_text(new_content)
                fixed_files.append(model_file.name)
        
        # Also fix schemas
        schemas_dir = self.backend_dir / "src" / "schemas"
        for schema_file in schemas_dir.glob("*.py"):
            content = schema_file.read_text()
            if "metadata:" in content:
                new_content = content.replace(
                    "metadata:",
                    "extra_metadata:"
                )
                schema_file.write_text(new_content)
                fixed_files.append(f"schemas/{schema_file.name}")
        
        if fixed_files:
            self.fixes_applied.append(f"Fixed metadata naming in: {', '.join(fixed_files)}")
            return True
        return False
    
    def fix_pydantic_import_error(self, error_text: str) -> bool:
        """Fix Pydantic v2 import errors."""
        if "BaseSettings` has been moved to the `pydantic-settings`" not in error_text:
            return False
            
        print("🔧 Fixing Pydantic import error...")
        
        config_file = self.backend_dir / "src" / "config.py"
        content = config_file.read_text()
        
        if "from pydantic import BaseSettings" in content:
            new_content = content.replace(
                "from pydantic import BaseSettings",
                "from pydantic_settings import BaseSettings"
            )
            config_file.write_text(new_content)
            self.fixes_applied.append("Fixed Pydantic import in config.py")
            return True
        return False
    
    def fix_pydantic_config_extra(self, error_text: str) -> bool:
        """Fix Pydantic extra fields validation error."""
        if "Extra inputs are not permitted" not in error_text:
            return False
            
        print("🔧 Fixing Pydantic extra fields configuration...")
        
        config_file = self.backend_dir / "src" / "config.py"
        content = config_file.read_text()
        
        # Find the Config class and add extra = "allow"
        if 'extra = "allow"' not in content:
            new_content = re.sub(
                r'(class Config:.*?)(env_file|case_sensitive)',
                r'\1extra = "allow"\n        \2',
                content,
                flags=re.DOTALL
            )
            config_file.write_text(new_content)
            self.fixes_applied.append("Added extra='allow' to Config class")
            return True
        return False
    
    def fix_import_errors(self, error_text: str) -> bool:
        """Fix various import errors."""
        # Fix missing __init__.py files
        if "No module named" in error_text:
            match = re.search(r"No module named '(src\.[^']+)'", error_text)
            if match:
                module_path = match.group(1).replace('.', '/')
                init_file = self.backend_dir / f"{module_path}/__init__.py"
                if not init_file.exists() and init_file.parent.exists():
                    init_file.touch()
                    self.fixes_applied.append(f"Created {init_file}")
                    return True
        
        # Fix missing email-validator for pydantic
        if "email-validator is not installed" in error_text:
            print("🔧 Installing email-validator for Pydantic...")
            # Update requirements.txt to use pydantic[email]
            req_file = self.backend_dir / "requirements.txt"
            content = req_file.read_text()
            if "pydantic==" in content and "[email]" not in content:
                new_content = content.replace("pydantic==", "pydantic[email]==")
                req_file.write_text(new_content)
                
                # Install the dependency
                venv_pip = self.backend_dir / "venv" / "bin" / "pip"
                if not venv_pip.exists():
                    venv_pip = self.backend_dir / "venv" / "Scripts" / "pip.exe"
                
                pip_cmd = str(venv_pip) if venv_pip.exists() else "pip"
                subprocess.run([pip_cmd, "install", "pydantic[email]"], check=True)
                
                self.fixes_applied.append("Installed email-validator for Pydantic")
                return True
        
        return False
    
    def run_automated_fixes(self) -> bool:
        """Run all automated fixes until server starts or max attempts reached."""
        print("🚀 Starting automated error detection and fixing...")
        
        for attempt in range(self.max_attempts):
            print(f"\n📍 Attempt {attempt + 1}/{self.max_attempts}")
            
            success, error_text = self.run_server_test()
            
            if success:
                print("✅ Server started successfully!")
                if self.fixes_applied:
                    print("\n🔧 Fixes applied:")
                    for fix in self.fixes_applied:
                        print(f"  - {fix}")
                return True
            
            print(f"❌ Error detected: {error_text[:200]}...")
            
            # Try to apply fixes
            fixed = False
            for fixer in [
                self.fix_pydantic_import_error,
                self.fix_pydantic_config_extra,
                self.fix_sqlalchemy_metadata_conflict,
                self.fix_import_errors,
            ]:
                if fixer(error_text):
                    fixed = True
                    break
            
            if not fixed:
                print("⚠️  No automated fix available for this error.")
                print("\nFull error:")
                print(error_text)
                return False
            
            # Give the system a moment
            time.sleep(0.5)
        
        print(f"\n⚠️  Max attempts ({self.max_attempts}) reached.")
        return False


if __name__ == "__main__":
    fixer = AutomatedFixer()
    success = fixer.run_automated_fixes()
    sys.exit(0 if success else 1)