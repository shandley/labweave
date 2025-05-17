#!/bin/bash
# Development environment setup script for LabWeave backend

echo "Setting up LabWeave backend development environment..."

# Check for Python 3.11
if command -v python3.11 &> /dev/null; then
    echo "✓ Python 3.11 found"
    PYTHON_CMD=python3.11
elif command -v python3 &> /dev/null; then
    # Check if python3 is 3.11.x
    PYTHON_VERSION=$(python3 --version | cut -d " " -f 2 | cut -d "." -f 1,2)
    if [ "$PYTHON_VERSION" = "3.11" ]; then
        echo "✓ Python 3.11 found"
        PYTHON_CMD=python3
    else
        echo "❌ Python 3.11 required, found Python $PYTHON_VERSION"
        echo "Please install Python 3.11:"
        echo "  - macOS: brew install python@3.11"
        echo "  - Ubuntu: sudo apt install python3.11"
        exit 1
    fi
else
    echo "❌ Python not found. Please install Python 3.11"
    exit 1
fi

# Check if venv exists, clean if it does
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "Creating virtual environment..."
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "⚠️  Some dependencies failed to install. Trying minimal requirements..."
        pip install -r requirements-minimal.txt
    fi
else
    echo "⚠️  requirements.txt not found, installing minimal requirements..."
    pip install fastapi uvicorn[standard] sqlalchemy==1.4.48 alembic pytest
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        # Create a minimal .env file
        cat > .env << EOF
# Database
DATABASE_URL=postgresql://labweave_user:labweave_password@localhost/labweave
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Security
SECRET_KEY=development-secret-key-change-in-production
EOF
    fi
    echo "⚠️  Please update .env with your configuration"
fi

# Create necessary directories
mkdir -p logs
mkdir -p uploads

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the development server, run:"
echo "  uvicorn src.main:app --reload --port 8000"
echo ""
echo "To run tests, run:"
echo "  pytest"
echo ""
echo "To start databases, run:"
echo "  cd ../infrastructure/docker && docker-compose up -d"