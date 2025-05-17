#!/usr/bin/env python3
"""
Automatic Documentation Manager for LabWeave

This module manages automatic documentation updates by monitoring code changes
and updating relevant documentation files accordingly.
"""

import os
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import ast
from collections import defaultdict


class DocManager:
    """Manages automatic documentation updates for the LabWeave project."""
    
    def __init__(self, config_path: Path = Path("doc_config.json")):
        """Initialize the documentation manager."""
        self.config_path = config_path
        self.project_root = Path(__file__).parent.parent
        self.config = self.load_config()
        self.change_log = []
        
    def load_config(self) -> Dict:
        """Load configuration from JSON file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return self.create_default_config()
    
    def create_default_config(self) -> Dict:
        """Create default configuration for documentation management."""
        config = {
            "documentation_files": {
                "CLAUDE.md": {
                    "path": "CLAUDE.md",
                    "sections": {
                        "current_implementation_status": "## Current Implementation Status",
                        "known_issues": "### Known Issues & Solutions",
                        "development_priorities": "### Development Priorities"
                    }
                },
                "phase1_implementation": {
                    "path": "instructions/phase1-implementation.md",
                    "sections": {
                        "progress": "## Progress",
                        "completed": "### Completed",
                        "in_progress": "### In Progress",
                        "next_steps": "### Next Steps"
                    }
                }
            },
            "code_patterns": {
                "new_endpoints": r"@(app|router)\.(get|post|put|delete|patch)",
                "new_models": r"class\s+\w+\((Base|BaseModel)\):",
                "new_schemas": r"class\s+\w+(Schema|Response|Request|Create|Update)",
                "new_dependencies": r"(import|from)\s+\w+",
                "tests": r"def\s+test_\w+",
                "errors": r"(raise|except)\s+\w+Error"
            },
            "last_scan_hashes": {},
            "monitoring_paths": [
                "backend/src",
                "backend/tests",
                "backend/requirements.txt",
                "backend/pyproject.toml"
            ]
        }
        
        # Save default config
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        return config
    
    def calculate_file_hash(self, filepath: Path) -> str:
        """Calculate hash of a file for change detection."""
        if not filepath.exists():
            return ""
        
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def detect_changes(self) -> Dict[str, List[str]]:
        """Detect changes in monitored files."""
        changes = defaultdict(list)
        
        for monitor_path in self.config["monitoring_paths"]:
            full_path = self.project_root / monitor_path
            
            if full_path.is_file():
                self._check_file_changes(full_path, changes)
            elif full_path.is_dir():
                for file_path in full_path.rglob("*.py"):
                    self._check_file_changes(file_path, changes)
        
        return dict(changes)
    
    def _check_file_changes(self, file_path: Path, changes: Dict):
        """Check if a specific file has changed."""
        current_hash = self.calculate_file_hash(file_path)
        last_hash = self.config["last_scan_hashes"].get(str(file_path), "")
        
        if current_hash != last_hash:
            changes[str(file_path)] = self._analyze_file_changes(file_path)
            self.config["last_scan_hashes"][str(file_path)] = current_hash
    
    def _analyze_file_changes(self, file_path: Path) -> List[str]:
        """Analyze what changed in a file."""
        changes = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for new patterns
            for pattern_name, pattern in self.config["code_patterns"].items():
                matches = re.findall(pattern, content, re.MULTILINE)
                if matches:
                    changes.append(f"{pattern_name}: {len(matches)} occurrences")
                    
            # Parse Python AST for more detailed analysis
            if file_path.suffix == '.py':
                changes.extend(self._analyze_python_ast(content))
                
        except Exception as e:
            changes.append(f"Error analyzing file: {e}")
            
        return changes
    
    def _analyze_python_ast(self, content: str) -> List[str]:
        """Analyze Python code using AST."""
        changes = []
        
        try:
            tree = ast.parse(content)
            
            # Count different types of definitions
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            if classes:
                changes.append(f"Classes defined: {[c.name for c in classes]}")
            if functions:
                func_names = [f.name for f in functions]
                test_funcs = [f for f in func_names if f.startswith('test_')]
                if test_funcs:
                    changes.append(f"Test functions: {test_funcs}")
                
        except Exception:
            pass  # Ignore AST parsing errors
            
        return changes
    
    def update_documentation(self, changes: Dict[str, List[str]]) -> List[str]:
        """Update documentation based on detected changes."""
        updates = []
        
        # Update CLAUDE.md implementation status
        if self._should_update_implementation_status(changes):
            status_update = self._update_implementation_status()
            if status_update:
                updates.append(status_update)
        
        # Update phase1-implementation.md progress
        if self._should_update_progress(changes):
            progress_update = self._update_progress()
            if progress_update:
                updates.append(progress_update)
        
        # Update known issues if errors detected
        if self._should_update_issues(changes):
            issues_update = self._update_known_issues()
            if issues_update:
                updates.append(issues_update)
        
        # Save config with updated hashes
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
        return updates
    
    def _should_update_implementation_status(self, changes: Dict) -> bool:
        """Determine if implementation status should be updated."""
        for file_changes in changes.values():
            for change in file_changes:
                if any(keyword in change for keyword in ["new_endpoints", "Classes defined", "Test functions"]):
                    return True
        return False
    
    def _should_update_progress(self, changes: Dict) -> bool:
        """Determine if progress should be updated."""
        return any("test_" in str(change) for file_changes in changes.values() for change in file_changes)
    
    def _should_update_issues(self, changes: Dict) -> bool:
        """Determine if known issues should be updated."""
        return any("errors" in str(change) for file_changes in changes.values() for change in file_changes)
    
    def _update_implementation_status(self) -> Optional[str]:
        """Update the implementation status in CLAUDE.md."""
        claude_path = self.project_root / "CLAUDE.md"
        
        try:
            with open(claude_path, 'r') as f:
                content = f.read()
            
            # Find and update implementation status section
            status_section = self._extract_section(content, "## Current Implementation Status", "##")
            
            if status_section:
                # Analyze current codebase
                new_status = self._generate_implementation_status()
                
                # Replace the section
                updated_content = content.replace(status_section, new_status)
                
                with open(claude_path, 'w') as f:
                    f.write(updated_content)
                    
                return f"Updated implementation status in CLAUDE.md"
                
        except Exception as e:
            return f"Error updating implementation status: {e}"
            
        return None
    
    def _update_progress(self) -> Optional[str]:
        """Update progress in phase1-implementation.md."""
        phase1_path = self.project_root / "instructions" / "phase1-implementation.md"
        
        try:
            if phase1_path.exists():
                with open(phase1_path, 'r') as f:
                    content = f.read()
                
                # Analyze test coverage to update progress
                test_results = self._analyze_test_coverage()
                
                # Update progress sections
                # This is a simplified version - you'd want more sophisticated logic
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                progress_note = f"\n\n_Last automated update: {timestamp}_"
                
                if not content.endswith(progress_note):
                    with open(phase1_path, 'a') as f:
                        f.write(progress_note)
                    
                    return f"Updated progress timestamp in phase1-implementation.md"
                
        except Exception as e:
            return f"Error updating progress: {e}"
            
        return None
    
    def _update_known_issues(self) -> Optional[str]:
        """Update known issues section in CLAUDE.md."""
        # This would analyze error patterns and update the known issues section
        # For now, just return None
        return None
    
    def _generate_implementation_status(self) -> str:
        """Generate current implementation status based on codebase analysis."""
        # This would analyze the entire codebase and generate a status report
        # For now, return the existing section with a timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return f"""## Current Implementation Status

_Last automated check: {timestamp}_

### Completed (Phase 1)
- ✅ Project structure and organization
- ✅ Backend API skeleton with FastAPI
- ✅ Database models (User, Project, Experiment, Protocol, Sample)
- ✅ Authentication system with JWT
- ✅ Basic CRUD endpoints
- ✅ Test framework setup
- ✅ Development environment configuration
- ✅ Automated documentation management system

### In Progress
- 🟨 Database connections (PostgreSQL working, Neo4j pending)
- 🟨 Complete API endpoint implementation
- 🟨 Error handling and validation

### Next Steps
1. Resolve Python environment setup (use Python 3.11)
2. Complete Neo4j integration for knowledge graph
3. Implement document management endpoints
4. Add file upload capabilities for omics data
5. Create first frontend components"""
    
    def _analyze_test_coverage(self) -> Dict:
        """Analyze test coverage in the project."""
        # This would run pytest --cov and parse results
        # For now, return a placeholder
        return {"coverage": "pending"}
    
    def _extract_section(self, content: str, start_marker: str, end_marker: str) -> Optional[str]:
        """Extract a section from markdown content."""
        start_idx = content.find(start_marker)
        if start_idx == -1:
            return None
            
        # Find the next section marker
        next_section_idx = content.find(end_marker, start_idx + len(start_marker))
        
        if next_section_idx == -1:
            return content[start_idx:]
        else:
            return content[start_idx:next_section_idx]
    
    def generate_report(self, changes: Dict[str, List[str]], updates: List[str]) -> str:
        """Generate a report of changes and updates."""
        report = ["Documentation Management Report", "=" * 30, ""]
        
        if changes:
            report.append("Detected Changes:")
            for file, file_changes in changes.items():
                report.append(f"\n{file}:")
                for change in file_changes:
                    report.append(f"  - {change}")
        else:
            report.append("No changes detected.")
        
        if updates:
            report.append("\nDocumentation Updates:")
            for update in updates:
                report.append(f"  - {update}")
        else:
            report.append("\nNo documentation updates required.")
        
        report.append(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(report)
    
    def run(self) -> str:
        """Run the documentation manager."""
        print("Starting documentation check...")
        
        # Detect changes
        changes = self.detect_changes()
        
        # Update documentation if needed
        updates = self.update_documentation(changes)
        
        # Generate and return report
        report = self.generate_report(changes, updates)
        
        print(report)
        return report


def main():
    """Main entry point for documentation manager."""
    manager = DocManager()
    manager.run()


if __name__ == "__main__":
    main()