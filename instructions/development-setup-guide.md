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

1. Always activate virtual environment before working
2. Keep dependencies updated: `pip install --upgrade -r requirements.txt`
3. Run tests before committing: `pytest`
4. Use the linter: `ruff check .`
5. Format code: `black .`

### CI/CD Considerations

Our CI/CD pipeline tests against:
- Python 3.11 (primary)
- Python 3.12 (compatibility check)

This ensures code works across versions while maintaining stable development.