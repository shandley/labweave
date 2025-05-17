# LabWeave Development Setup Guide

## Python Version Requirements

### Current Requirement: Python 3.11.x

We're currently using Python 3.11 for development due to ecosystem compatibility. Python 3.13 is too new and many dependencies haven't released compatible versions yet.

### Why This Matters

1. **Dependency Ecosystem**: Major packages like pydantic, psycopg2-binary need pre-compiled wheels
2. **Scientific Stack**: NumPy, SciPy, BioPython are tested primarily on stable Python versions
3. **Stability**: Python 3.11 is the current stable LTS-like version with broad support

### Setup Instructions

#### macOS
```bash
# Install Python 3.11 using Homebrew
brew install python@3.11

# Verify installation
python3.11 --version
```

#### Ubuntu/Debian
```bash
# Add deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev

# Verify installation
python3.11 --version
```

#### Windows
Download Python 3.11 from [python.org](https://www.python.org/downloads/) and install.

### Using the Setup Script

We provide an automated setup script:

```bash
cd backend
./setup-dev.sh
```

This script will:
1. Check for Python 3.11
2. Create a virtual environment
3. Install all dependencies
4. Create necessary directories
5. Set up configuration files

### Manual Setup (Alternative)

If you prefer manual setup:

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Verifying Your Setup

After setup, verify everything works:

```bash
# Check Python version
python --version  # Should show 3.11.x

# Test FastAPI
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"

# Run a simple test
python test_simple.py
```

### Common Issues and Solutions

#### Issue: psycopg2-binary fails to install
**Solution**: Install PostgreSQL development files
```bash
# macOS
brew install postgresql

# Ubuntu
sudo apt install libpq-dev
```

#### Issue: Python version conflicts
**Solution**: Use pyenv to manage Python versions
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.7
pyenv local 3.11.7
```

#### Issue: Import errors after installation
**Solution**: Ensure virtual environment is activated
```bash
source venv/bin/activate  # Linux/macOS
# OR
.\venv\Scripts\activate  # Windows
```

### Future Python Version Support

- **Q1 2024**: Continue with Python 3.11
- **Q2 2024**: Test compatibility with Python 3.12
- **Q3 2024**: Evaluate Python 3.13 when ecosystem is ready
- **Q4 2024**: Potentially upgrade to newer version

### Development Workflow

#### NEW: Automated Smart Start (Recommended)
```bash
cd backend
source venv/bin/activate
python smart_start.py  # Runs all checks, fixes issues, and starts server
```

This smart startup system:
- Validates code structure before starting
- Automatically fixes common issues
- Runs comprehensive tests
- Manages database services
- Starts the server with proper error handling

#### Alternative: Using Make Commands
```bash
make smart-start  # Full automated startup
make check       # Pre-flight checks only
make fix         # Automated fixes only
make test        # Run test suite
```

#### Traditional Workflow
1. Always activate virtual environment before working
2. Keep dependencies updated: `pip install --upgrade -r requirements.txt`
3. Run tests before committing: `pytest`
4. Use the linter: `ruff check .`
5. Format code: `black .`

### Automated Testing System Documentation

For full details on the automated testing system, see:
- `/backend/AUTOMATED_TESTING.md` - Complete documentation
- `/backend/smart_start.py` - Main automation script
- `/backend/preflight_check.py` - Pre-flight validation
- `/backend/automated_fix.py` - Error detection and fixing
- `/backend/tests/test_startup.py` - Startup validation tests

### CI/CD Considerations

Our CI/CD pipeline tests against:
- Python 3.11 (primary)
- Python 3.12 (compatibility check)

This ensures code works across versions while maintaining stable development.