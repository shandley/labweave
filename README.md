# LabWeave

![LabWeave Logo](labweave_logo.png)

A comprehensive research operations platform that unifies knowledge management, sample tracking, and AI-driven orchestration for omics research.

## Project Status

🚧 Under active development - MVP in progress

### Completed ✅
- Project structure and organization
- Backend API skeleton with FastAPI
- Database models (User, Project, Experiment, Protocol, Sample, Document)
- Authentication system with JWT
- Basic CRUD endpoints
- Test framework setup
- Development environment configuration
- Document management system with file upload/download
- **Version control for documents** (track document history, restore previous versions)
- File organization with automatic structure and user customization

### In Progress 🟨
- Neo4j integration for knowledge graph
- Complete API endpoint implementation
- Error handling and validation
- Advanced document metadata extraction

## Overview

LabWeave transforms how scientific research is conducted by:
- Eliminating boundaries between ELNs, LIMS, and analysis tools
- Introducing intelligent research orchestration capabilities
- Focusing on omics research (initially metagenomics)

### Current Focus
- **Domain**: Metagenomics with Illumina sequencing data
- **Scale**: Single lab deployment (8-12 users)
- **Phase**: MVP development focusing on core knowledge management
- **Priority**: Knowledge management → LIMS features → AI capabilities

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

3. Start infrastructure services
```bash
cd ../infrastructure/docker
docker-compose up -d
```

4. Run database migrations
```bash
cd ../../backend
alembic upgrade head
```

5. Start development server
```bash
# Backend (in activated virtual environment)
cd backend
uvicorn src.main:app --reload

# Access the API documentation at http://localhost:8000/docs
```

### Smart Development Workflow (Recommended)

We provide automated tools for development:

```bash
cd backend
source venv/bin/activate

# Automated startup with all checks and fixes
python smart_start.py

# OR using make commands
make smart-start     # Runs all checks, fixes, and starts server
make check          # Run pre-flight checks only
make fix           # Run automated fixes only
make test          # Run test suite
```

## API Endpoints

The API is accessible at `http://localhost:8000` when running locally.

### Available Endpoints

- **Root**: `GET /` - Welcome message and API info
- **API Documentation**: `GET /docs` - Interactive API documentation (Swagger UI)
- **ReDoc**: `GET /redoc` - Alternative API documentation

#### API v1 Endpoints (`/api/v1`)

- **Health Check**: `GET /api/v1/health` - System health status
- **Authentication**:
  - `POST /api/v1/auth/register` - User registration
  - `POST /api/v1/auth/login` - User login
  - `POST /api/v1/auth/refresh` - Refresh access token
- **Users**:
  - `GET /api/v1/users/me` - Get current user
  - `GET /api/v1/users/{user_id}` - Get user by ID
  - `PUT /api/v1/users/{user_id}` - Update user
- **Projects**:
  - `GET /api/v1/projects` - List projects
  - `POST /api/v1/projects` - Create project
  - `GET /api/v1/projects/{project_id}` - Get project details
  - `PUT /api/v1/projects/{project_id}` - Update project
  - `DELETE /api/v1/projects/{project_id}` - Delete project
- **Experiments**:
  - `GET /api/v1/experiments` - List experiments
  - `POST /api/v1/experiments` - Create experiment
  - `GET /api/v1/experiments/{experiment_id}` - Get experiment details
  - `PUT /api/v1/experiments/{experiment_id}` - Update experiment
  - `DELETE /api/v1/experiments/{experiment_id}` - Delete experiment
- **Protocols**:
  - `GET /api/v1/protocols` - List protocols
  - `POST /api/v1/protocols` - Create protocol
  - `GET /api/v1/protocols/{protocol_id}` - Get protocol details
  - `PUT /api/v1/protocols/{protocol_id}` - Update protocol
  - `DELETE /api/v1/protocols/{protocol_id}` - Delete protocol
- **Samples**:
  - `GET /api/v1/samples` - List samples
  - `POST /api/v1/samples` - Create sample
  - `GET /api/v1/samples/{sample_id}` - Get sample details
  - `PUT /api/v1/samples/{sample_id}` - Update sample
  - `DELETE /api/v1/samples/{sample_id}` - Delete sample
- **Documents** (with version control):
  - `GET /api/v1/documents` - List documents (with optional latest_only filter)
  - `POST /api/v1/documents/upload` - Upload new document
  - `GET /api/v1/documents/{document_id}` - Get document details
  - `GET /api/v1/documents/{document_id}/download` - Download document file
  - `PATCH /api/v1/documents/{document_id}` - Update document metadata
  - `DELETE /api/v1/documents/{document_id}` - Delete document
  - `POST /api/v1/documents/{document_id}/versions` - Upload new version
  - `GET /api/v1/documents/{document_id}/versions` - List all versions
  - `GET /api/v1/documents/{document_id}/versions/{version_number}` - Get specific version
  - `POST /api/v1/documents/{document_id}/restore/{version_number}` - Restore old version

## Key Features

### Document Management
- **File Upload/Download**: Support for omics data formats (FASTQ, FASTA, SAM, BAM, VCF, etc.)
- **Version Control**: Track document history, upload new versions, restore previous versions
- **Automatic Organization**: Files organized by project/experiment with customizable structure
- **Metadata Support**: Flexible JSON metadata and tagging system
- **Hash Verification**: SHA256 hashes for file integrity checking

### Supported File Formats
- Sequencing data: `.fastq`, `.fq`, `.fastq.gz`, `.fq.gz`
- Sequences: `.fasta`, `.fa`, `.fna`, `.fasta.gz`
- Alignments: `.sam`, `.bam`
- Variant calls: `.vcf`, `.vcf.gz`
- Annotations: `.bed`, `.gff`, `.gtf`
- Phylogenetic trees: `.nwk`, `.tree`, `.nxs`
- Data tables: `.tsv`, `.csv`, `.txt`
- Documentation: `.pdf`

## Architecture

### Technology Stack
- **Backend**: Python 3.11 + FastAPI
- **Databases**: PostgreSQL (primary) + Neo4j (knowledge graph) + Redis (caching)
- **Frontend**: React 18 with TypeScript (planned)
- **AI/ML**: PyTorch + Cloud APIs (OpenAI, Claude, Gemini)
- **Infrastructure**: Docker, MinIO (object storage)
- **Testing**: pytest, httpx
- **Code Quality**: Black, Ruff, mypy
- **Bioinformatics**: Biopython, NumPy, pandas, SciPy, NetworkX

### Project Structure
```
labweave/
├── backend/              # FastAPI backend
│   ├── src/             # Source code
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── core/        # Core utilities
│   │   └── db/          # Database configuration
│   ├── tests/           # Backend tests
│   ├── alembic/         # Database migrations
│   └── smart_start.py   # Automated development startup
├── frontend/            # React frontend (planned)
├── infrastructure/      # Docker and configs
├── instructions/        # Project documentation
└── docs/                # API documentation
```

## Documentation

### Core Documentation
- [Project Overview](instructions/labweave-overview.md) - Vision and goals
- [Implementation Requirements](instructions/labweave-prompt.md) - Detailed requirements
- [Technology Stack](instructions/tech-stack.md) - Architecture decisions
- [MVP Plan](instructions/mvp-plan.md) - Development roadmap
- [API Design](instructions/api-design.md) - REST API patterns

### Development Guides
- [Development Setup Guide](instructions/development-setup-guide.md)
- [Python Compatibility Analysis](instructions/python-compatibility-analysis.md)
- [Phase 1 Implementation Tracker](instructions/phase1-implementation.md)
- [CLAUDE.md](CLAUDE.md) - Current implementation focus

### API Documentation
- Interactive docs available at `/docs` when running the backend server
- ReDoc available at `/redoc`
- OpenAPI specification at `/openapi.json`

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest
pytest --cov=src  # With coverage
pytest -v         # Verbose output
pytest tests/test_startup.py  # Run startup validation tests
```

### Code Quality
```bash
# Backend
cd backend
black .          # Format code
ruff check .     # Lint
mypy .          # Type checking

# All quality checks at once
make check      # Runs all checks
make fix        # Runs all fixes
```

### Common Issues

1. **Python Version**: Ensure you're using Python 3.11.x
   ```bash
   python --version  # Should show 3.11.x
   ```

2. **Database Connection**: Make sure Docker services are running
   ```bash
   docker ps  # Should show postgres, neo4j, redis, minio
   ```

3. **Import Errors**: Always activate the virtual environment
   ```bash
   source backend/venv/bin/activate
   ```

## Features

### Phase 1 (Current Focus)
- ✅ User authentication with JWT
- ✅ Basic project and experiment management
- ✅ Sample tracking for metagenomics
- ✅ Protocol management
- 🟨 Document management with version control
- 🟨 Knowledge graph for entity relationships
- 🟨 File upload for omics data

### Phase 2 (Planned)
- ⬜ PubMed integration
- ⬜ Equipment scheduling (Cal.com integration)
- ⬜ Advanced search capabilities
- ⬜ Collaborative features
- ⬜ Batch operations
- ⬜ Data visualization

### Phase 3 (Future)
- ⬜ AI-powered insights
- ⬜ Automated analysis pipelines
- ⬜ Multi-lab federation
- ⬜ Mobile field work support

## Contributing

This project is in early development. Please contact the maintainers before contributing.

### Development Workflow
1. Create a feature branch from `main`
2. Make your changes
3. Run tests and code quality checks
4. Submit a pull request

### Code Style
- Python: Black formatter, Ruff linter
- Follow PEP 8 guidelines
- Comprehensive docstrings for all functions
- Type hints for function parameters

## License

[License pending]

## Contact

For questions about LabWeave, please contact the project maintainers.

---

**Note**: This is an active development project. Features and APIs are subject to change.