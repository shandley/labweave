# LabWeave Project Context

## Important Documents to Reference

Always consult these core documents when discussing LabWeave implementation:

- `/Users/scotthandley/Code/labweave/instructions/labweave-overview.md` - Project vision, goals, and transformative impact
- `/Users/scotthandley/Code/labweave/instructions/labweave-prompt.md` - Detailed implementation requirements and development approach
- `/Users/scotthandley/Code/labweave/instructions/tech-stack.md` - Technology stack decisions and architecture
- `/Users/scotthandley/Code/labweave/instructions/mvp-plan.md` - MVP roadmap focusing on knowledge management → LIMS → AI
- `/Users/scotthandley/Code/labweave/instructions/api-design.md` - RESTful API design patterns and endpoints
- `/Users/scotthandley/Code/labweave/instructions/phase1-implementation.md` - Current implementation progress tracker
- `/Users/scotthandley/Code/labweave/instructions/python-compatibility-analysis.md` - Python version requirements and analysis
- `/Users/scotthandley/Code/labweave/instructions/development-setup-guide.md` - Developer environment setup instructions

### Document Relationships

- **labweave-prompt.md**: Serves as the stable requirements document defining WHAT to build
- **tech-stack.md**: Details HOW to build it with specific technology choices
- **CLAUDE.md**: Captures CURRENT FOCUS and implementation priorities
- **phase1-implementation.md**: Tracks actual implementation progress and blockers
- **development-setup-guide.md**: Practical instructions for getting started

The prompt remains the north star for requirements while other documents capture evolving implementation decisions.

## Project Guidelines

### Current Focus
- **Domain**: Omics research (specifically metagenomics/Illumina data)
- **Scale**: Initial deployment for 8-12 users per lab  
- **Phase**: Focus on Phase 1 (Foundation with Basic Intelligence) from the overview
- **Architecture**: Single lab deployment initially (but designed for future multi-tenancy)

### Development Priorities
1. Knowledge Management first (document CRUD, basic knowledge graph) ✅
2. LIMS functionality second (sample tracking, metagenomics focus) 🟨
3. AI features last (after core functionality is stable)
4. PubMed integration as primary external knowledge source
5. Calendar integration for shared equipment/facilities (Cal.com preferred)
6. Frontend development in parallel with backend (now active)

### Known Issues & Solutions
- **Python 3.13 Compatibility**: Use Python 3.11.x until ecosystem catches up
- **Database Setup**: Ensure Docker services are running before starting backend
- **Import Errors**: Always activate virtual environment before running code

### Technology Decisions
- **Python Version**: 3.11.x (3.13 not yet supported due to ecosystem compatibility)
- **Backend**: Python/FastAPI with PostgreSQL and Neo4j
- **Frontend**: React with TypeScript
- **AI/ML**: PyTorch locally + OpenAI/Claude/Gemini APIs
- **Omics Tools**: Biopython, BioBERT, RDKit for domain-specific needs
- **Development Tools**: Black, Ruff, pytest for code quality

### What NOT to Focus On (Yet)
- Mobile/field work capabilities (see `/future-ideas/mobile-field-work.md`)
- Multi-lab federation (Phase 3 feature)
- Regulatory compliance frameworks
- Petabyte-scale data handling

### Development Approach
1. Start with core functionality before advanced features
2. Use modular architecture for easy extension
3. Implement automated testing during development
4. Design APIs first for frontend-backend separation
5. Keep security in mind but don't over-engineer initially
6. Git repository: https://github.com/shandley/labweave
7. Use Python 3.11 for compatibility and stability
8. Iterate quickly with basic tests for MVP, comprehensive testing post-concept validation
9. Maintain comprehensive documentation as we build

### File Format Support (Omics Data)
Initial support planned for:
- Sequencing data: FASTQ, FASTA, SAM, BAM
- Analysis outputs: Count tables, taxonomy tables
- Phylogenetic data: Tree files (Newick, Nexus)
- Architecture designed for easy format expansion

### File Organization
- `/instructions/` - Core project documentation
- `/backend/src/` - Backend source code (FastAPI application)
- `/backend/tests/` - Backend test files
- `/frontend/src/` - Frontend source code (React application)
- `/infrastructure/docker/` - Docker compose and infrastructure configs
- `/docs/` - API and user documentation (to be created)
- `/future-ideas/` - Features for later consideration

## Current Implementation Status

_Last manual update: 2025-05-17 10:07_

### Completed (Phase 1)
- ✅ Project structure and organization
- ✅ Backend API skeleton with FastAPI
- ✅ Database models (User, Project, Experiment, Protocol, Sample, Document)
- ✅ Authentication system with JWT
- ✅ Basic CRUD endpoints for all entities
- ✅ Test framework setup
- ✅ Development environment configuration
- ✅ Automated documentation management system
- ✅ Neo4j integration for knowledge graph
- ✅ Document management with versioning
- ✅ File upload capabilities
- ✅ Frontend application initialized with React/TypeScript/Vite
- ✅ Frontend authentication flow (login/register)
- ✅ Frontend routing with React Router
- ✅ Frontend state management with TanStack Query
- ✅ Frontend UI with Tailwind CSS
- ✅ Projects page with full CRUD operations
- ✅ Dashboard with statistics
- ✅ Navigation layout and responsive design

### In Progress
- 🟨 Error handling and validation improvements
- 🟨 Additional frontend pages (Experiments, Samples, Protocols)
- 🟨 File upload UI in frontend
- 🟨 Knowledge graph visualization

### Next Steps
1. Complete remaining frontend pages (Experiments, Samples, Documents, Protocols)
2. Implement file upload UI for omics data
3. Add knowledge graph visualization component
4. Improve error handling and user feedback
5. Implement search functionality
6. Add data export/import features

## Development Tips

### Environment Setup
```bash
cd backend
./setup-dev.sh  # Use our automated setup script
```

### Smart Development Workflow (NEW - Recommended)
```bash
cd backend
source venv/bin/activate

# Option 1: Automated startup with all checks and fixes
python smart_start.py

# Option 2: Using make commands
make smart-start     # Runs all checks, fixes, and starts server
make check          # Run pre-flight checks only
make fix           # Run automated fixes only
make test          # Run test suite
```

### Automated Testing System
We now have a comprehensive automated testing and fixing system:
- **smart_start.py**: Runs all checks, applies fixes, documentation updates, and starts server
- **preflight_check.py**: Validates code structure before startup
- **automated_fix.py**: Detects and fixes common errors automatically
- **tests/test_startup.py**: Comprehensive startup validation tests
- **AUTOMATED_TESTING.md**: Full documentation of the system

### Automatic Documentation Management (NEW)
The project now includes an automatic documentation management system that runs with smart_start.py:
- **doc_manager.py**: Basic documentation update system with change detection
- **doc_manager_advanced.py**: Advanced system with semantic code analysis
- **Auto-updated files**:
  - `CLAUDE.md`: Implementation status, known issues, priorities
  - `instructions/phase1-implementation.md`: Progress tracking
  - `docs/api/endpoints.md`: API documentation (when endpoints exist)

The documentation manager automatically:
- Detects code changes (new models, endpoints, tests)
- Updates implementation status sections
- Tracks test coverage and failures
- Identifies TODO/FIXME items in code
- Updates progress timestamps
- Generates API documentation from code

To run documentation updates manually:
```bash
cd backend
python doc_manager.py  # Basic updates
python doc_manager_advanced.py  # Full semantic analysis
```

The system maintains a `doc_config.json` file to track file hashes and monitor changes between runs.

### Manual Testing
```bash
pytest  # Run all tests
pytest -v  # Verbose output
pytest --cov=src  # With coverage
pytest tests/test_startup.py  # Run startup validation tests
```

### Code Quality
```bash
black .  # Format code
ruff check .  # Lint code
mypy .  # Type checking
```

## Remember
- LabWeave aims to be transformative, not just another ELN/LIMS
- Focus on scientist-friendly UX over technical complexity
- The platform should adapt to researchers, not vice versa
- AI should augment human intelligence, not replace it
- Always test with realistic scientific workflows