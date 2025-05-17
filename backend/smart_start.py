#!/usr/bin/env python3
"""Smart startup script that runs all checks and fixes before starting the server."""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔸 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"   ✅ Success")
        return True
    else:
        print(f"   ❌ Failed")
        if result.stderr:
            print(f"   Error: {result.stderr[:200]}...")
        return False


def main():
    """Main entry point for smart startup."""
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Use virtual environment Python if available
    venv_python = backend_dir / "venv" / "bin" / "python"
    if not venv_python.exists():
        venv_python = backend_dir / "venv" / "Scripts" / "python.exe"  # Windows
    
    python_cmd = str(venv_python) if venv_python.exists() else sys.executable
    
    print("🚀 LabWeave Smart Startup System")
    print("="*40)
    
    # Step 1: Run pre-flight checks
    if not run_command(
        f"{python_cmd} preflight_check.py",
        "Running pre-flight validation"
    ):
        print("\n⚠️  Pre-flight checks failed. Running automated fixes...")
        
        # Step 2: Run automated fixes
        if not run_command(
            f"{python_cmd} automated_fix.py",
            "Attempting automated fixes"
        ):
            print("\n❌ Automated fixes failed. Manual intervention required.")
            return 1
    
    # Step 3: Run tests
    print("\n🧪 Running test suite...")
    test_result = subprocess.run(
        f"{python_cmd} -m pytest tests/test_startup.py -v",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if test_result.returncode != 0:
        print("⚠️  Some tests failed. This might cause runtime issues.")
        print(test_result.stdout)
    else:
        print("✅ All tests passed")
    
    # Step 4: Create missing directories
    for dir_name in ['logs', 'uploads']:
        dir_path = backend_dir / dir_name
        if not dir_path.exists():
            dir_path.mkdir()
            print(f"📁 Created missing directory: {dir_name}")
    
    # Step 5: Check if databases are running
    print("\n🔍 Checking database services...")
    docker_check = subprocess.run(
        "docker ps | grep -E '(postgres|neo4j|redis)'",
        shell=True,
        capture_output=True
    )
    
    if docker_check.returncode != 0:
        print("⚠️  Database services not running. Starting them...")
        subprocess.run(
            "cd ../infrastructure/docker && docker-compose up -d",
            shell=True
        )
    else:
        print("✅ Database services are running")
    
    # Step 6: Start the server
    print("\n🌟 Starting LabWeave server...")
    print("="*40)
    
    try:
        subprocess.run(
            f"{python_cmd} -m uvicorn src.main:app --reload --port 8000",
            shell=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())