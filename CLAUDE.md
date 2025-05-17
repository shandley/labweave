# LabWeave Project Context

## Important Documents to Reference

Always consult these core documents when discussing LabWeave implementation:

- `/Users/scotthandley/Code/labweave/instructions/labweave-overview.md` - Project vision, goals, and transformative impact
- `/Users/scotthandley/Code/labweave/instructions/labweave-prompt.md` - Detailed implementation requirements and development approach
- `/Users/scotthandley/Code/labweave/instructions/tech-stack.md` - Technology stack decisions and architecture
- `/Users/scotthandley/Code/labweave/instructions/mvp-plan.md` - MVP roadmap focusing on knowledge management → LIMS → AI
- `/Users/scotthandley/Code/labweave/instructions/api-design.md` - RESTful API design patterns and endpoints

### Document Relationships

- **labweave-prompt.md**: Serves as the stable requirements document defining WHAT to build
- **tech-stack.md**: Details HOW to build it with specific technology choices
- **CLAUDE.md**: Captures CURRENT FOCUS and implementation priorities

The prompt remains the north star for requirements while other documents capture evolving implementation decisions.

## Project Guidelines

### Current Focus
- **Domain**: Omics research (specifically metagenomics/Illumina data)
- **Scale**: Initial deployment for 8-12 users per lab  
- **Phase**: Focus on Phase 1 (Foundation with Basic Intelligence) from the overview
- **Architecture**: Single lab deployment initially (but designed for future multi-tenancy)

### Development Priorities
1. Knowledge Management first (document CRUD, basic knowledge graph)
2. LIMS functionality second (sample tracking, metagenomics focus)
3. AI features last (after core functionality is stable)
4. PubMed integration as primary external knowledge source
5. Calendar integration for shared equipment/facilities (Cal.com preferred)

### Technology Decisions
- **Backend**: Python/FastAPI with PostgreSQL and Neo4j
- **Frontend**: React with TypeScript
- **AI/ML**: PyTorch locally + OpenAI/Claude/Gemini APIs
- **Omics Tools**: Biopython, BioBERT, RDKit for domain-specific needs

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

### File Organization
- `/instructions/` - Core project documentation
- `/src/` - Source code (to be created)
- `/tests/` - Test files (to be created)
- `/docs/` - API and user documentation (to be created)
- `/future-ideas/` - Features for later consideration

## Remember
- LabWeave aims to be transformative, not just another ELN/LIMS
- Focus on scientist-friendly UX over technical complexity
- The platform should adapt to researchers, not vice versa
- AI should augment human intelligence, not replace it