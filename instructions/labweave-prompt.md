# LabWeave Development Prompt

## Project Objective
Create LabWeave, a next-generation scientific research platform that unifies knowledge management, sample tracking, and AI orchestration for research laboratories. The platform should be designed to replace traditional ELNs and LIMS while introducing intelligent research orchestration capabilities.

## Core System Requirements

### Knowledge Infrastructure Component
1. Create a flexible, modular documentation system that:
   - Uses lightweight formats (markdown, structured data) for scientific protocols and methods
   - Implements version control for tracking changes to protocols and methods
   - Establishes a consistent but adaptable project organization structure
   - Captures metadata that connects related research components
   - Supports multiple input methods (text, voice-to-text, image annotation)

2. Design a knowledge graph backend that:
   - Identifies entities (experiments, reagents, samples, results) in research documentation
   - Maps relationships between these entities automatically
   - Constructs timelines from disparate documentation
   - Infers connections based on content and context

### LIMS Integration Component
1. Develop a sample management system that:
   - Treats samples as first-class citizens in the knowledge graph
   - Tracks complete sample lineage and processing history
   - Manages chain of custody with location history
   - Links samples directly to all associated experimental data

2. Create an inventory management system that:
   - Tracks reagents, consumables, and equipment in real-time
   - Predicts supply needs based on planned experiments
   - Monitors expiration dates and usage patterns
   - Integrates with laboratory equipment when possible

### AI Orchestration Component
1. Build a research intelligence engine that:
   - Continuously analyzes all lab data, protocols, and results
   - Identifies patterns across experiments and projects
   - Detects anomalies and unexpected results
   - Generates hypotheses based on emerging patterns

2. Implement a predictive research planning system that:
   - Assists with experiment design and optimization
   - Forecasts resource requirements for planned work
   - Estimates success probabilities for proposed approaches
   - Suggests alternative methods with tradeoff analysis

## Technical Architecture Guidelines

1. System Architecture:
   - Design a modular, API-first architecture
   - Implement a scalable knowledge graph database
   - Create separate services for different functional areas
   - Ensure all components communicate through well-defined interfaces

2. Frontend Development:
   - Focus on an intuitive, workflow-oriented user experience
   - Support multiple input modalities (desktop, mobile, voice)
   - Design visualization tools for knowledge relationships
   - Implement real-time collaboration capabilities

3. AI/ML Implementation:
   - Develop domain-specific models for scientific workflows
   - Implement explainable AI approaches for research suggestions
   - Create adaptive learning systems that improve with usage
   - Build feedback mechanisms for model refinement

4. Data Management:
   - Ensure robust data security and privacy controls
   - Implement comprehensive audit logging
   - Design for regulatory compliance where needed
   - Create flexible data export capabilities

## Development Approach

1. Initial Phase:
   - Focus on building the core knowledge infrastructure
   - Implement basic sample tracking capabilities
   - Develop foundational AI features for organization and retrieval
   - Create a simple but extensible user interface

2. Technical Considerations:
   - Prioritize extensibility through plugin architecture
   - Use open standards wherever possible
   - Implement comprehensive automated testing
   - Design for eventual multi-tenant deployment

## User Experience Principles

1. LabWeave should:
   - Adapt to existing lab workflows rather than disrupting them
   - Minimize documentation burden through intelligent assistance
   - Surface insights that would otherwise remain hidden
   - Scale from individual researchers to large collaborative teams

2. The system should be:
   - Intuitive for scientists without technical backgrounds
   - Powerful enough for computational specialists
   - Flexible enough to adapt to diverse research domains
   - Robust enough for mission-critical research operations

## Evaluation Metrics

The successful implementation should demonstrate:
1. Reduced time spent on documentation and administration
2. Improved experimental reproducibility and transparency
3. Enhanced resource utilization and planning
4. Novel insights generated through AI-assisted analysis
5. Seamless tracking of samples and associated data

This prompt establishes the foundational requirements and vision for the LabWeave platform. The implementation should balance immediate utility with the long-term vision of AI-orchestrated research.