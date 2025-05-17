# Automated Testing and Startup System

This directory now includes a comprehensive automated testing and fixing system to minimize manual intervention during development.

## Components

### 1. Automated Fixer (`automated_fix.py`)
- Detects and fixes common startup errors automatically
- Handles Pydantic imports, SQLAlchemy conflicts, configuration issues
- Runs up to 5 attempts to fix issues before giving up

### 2. Pre-flight Validator (`preflight_check.py`)
- Validates code before server startup
- Checks for:
  - SQLAlchemy reserved word usage
  - Model-schema consistency
  - Import cycles
  - Pydantic compatibility
  - Environment setup

### 3. Startup Tests (`tests/test_startup.py`)
- Comprehensive test suite for startup validation
- Tests imports, configurations, database models
- Catches issues before they cause runtime errors

### 4. Smart Startup (`smart_start.py`)
- Combines all tools into one intelligent startup process
- Runs checks, applies fixes, runs tests, starts databases, then starts server
- One command to rule them all

## Usage

### Quick Start (Recommended)
```bash
# Use the smart startup system
python smart_start.py

# Or use Make
make smart-start
```

### Individual Tools
```bash
# Run pre-flight checks only
python preflight_check.py

# Run automated fixes
python automated_fix.py

# Run startup tests
pytest tests/test_startup.py -v

# Traditional startup (no checks)
uvicorn src.main:app --reload
```

### Makefile Commands
```bash
make check        # Run pre-flight checks
make fix          # Run automated fixes
make test         # Run all tests
make start        # Basic server start
make smart-start  # Smart startup with all checks
```

## How It Works

1. **Pre-flight Check**: Validates the codebase structure and configuration
2. **Automated Fix**: Attempts to fix any issues found
3. **Test Suite**: Runs comprehensive tests to ensure everything works
4. **Environment Setup**: Creates missing directories, checks databases
5. **Server Start**: Finally starts the FastAPI server

## Benefits

- **Reduces Manual Debugging**: Common errors are fixed automatically
- **Faster Development**: Less time spent on configuration issues
- **Better Error Messages**: Clear indication of what's wrong
- **Learning Tool**: Shows common issues and their fixes

## Adding New Fixes

To add new automated fixes:

1. Add detection logic to `automated_fix.py`
2. Add validation to `preflight_check.py`
3. Add tests to `tests/test_startup.py`
4. Update this documentation

## Common Issues Fixed

- Pydantic v2 import changes
- SQLAlchemy reserved word conflicts
- Missing configuration settings
- Import cycles
- Missing directories
- Database connection issues