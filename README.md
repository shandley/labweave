# LabWeave

![LabWeave Logo](labweave_logo.png)

A comprehensive research operations platform that unifies knowledge management, sample tracking, and AI-driven orchestration for omics research.

## Project Status

🚧 Under active development - MVP in progress

## Overview

LabWeave transforms how scientific research is conducted by:
- Eliminating boundaries between ELNs, LIMS, and analysis tools
- Introducing intelligent research orchestration capabilities
- Focusing on omics research (initially metagenomics)

## Quick Start

### Prerequisites

- Python 3.11.x (Note: Python 3.13 not yet supported due to dependency compatibility)
- Node.js 18+
- Docker & Docker Compose
- Git

### Development Setup

1. Clone the repository
```bash
git clone https://github.com/shandley/labweave.git
cd labweave
```

2. Set up the backend
```bash
cd backend
./setup-dev.sh  # Automated setup script
# OR manually:
python3.11 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up the frontend
```bash
cd ../frontend
npm install
```

4. Start infrastructure services
```bash
cd ../infrastructure/docker
docker-compose up -d
```

5. Run database migrations
```bash
cd ../../backend
alembic upgrade head
```

6. Start development servers
```bash
# Terminal 1 - Backend
cd backend
uvicorn src.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## Architecture

- **Backend**: Python/FastAPI with PostgreSQL and Neo4j
- **Frontend**: React with TypeScript
- **AI/ML**: PyTorch + Cloud APIs (OpenAI, Claude, Gemini)
- **Infrastructure**: Docker, Redis, MinIO

## Documentation

- [Project Overview](instructions/labweave-overview.md)
- [Implementation Requirements](instructions/labweave-prompt.md)
- [Technology Stack](instructions/tech-stack.md)
- [API Documentation](docs/api/)

## Contributing

This project is in early development. Please contact the maintainers before contributing.

## License

[License pending]