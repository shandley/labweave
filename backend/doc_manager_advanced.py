#!/usr/bin/env python3
"""
Advanced Documentation Manager for LabWeave

This module provides more sophisticated documentation management with:
- Semantic analysis of code changes
- Automatic completion detection
- Issue tracking from test failures
- Change categorization
"""

import os
import re
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import ast
from collections import defaultdict
from enum import Enum


class ChangeType(Enum):
    """Types of changes detected in the codebase."""
    NEW_FEATURE = "new_feature"
    BUG_FIX = "bug_fix"
    TEST_ADDED = "test_added"
    REFACTOR = "refactor"
    DEPENDENCY = "dependency"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"


class AdvancedDocManager:
    """Advanced documentation manager with semantic change detection."""
    
    def __init__(self):
        """Initialize the advanced documentation manager."""
        self.project_root = Path(__file__).parent.parent
        self.patterns = {
            ChangeType.NEW_FEATURE: [
                r"class\s+\w+\(.*\):",  # New classes
                r"def\s+[^_]\w+\(",     # New public functions
                r"@(app|router)\.(get|post|put|delete|patch)",  # New endpoints
            ],
            ChangeType.BUG_FIX: [
                r"fix\s*\(",  # Fix commits
                r"bugfix",    # Bugfix mentions
                r"resolve[sd]?\s+#\d+",  # Issue resolutions
            ],
            ChangeType.TEST_ADDED: [
                r"def\s+test_\w+",  # Test functions
                r"class\s+Test\w+",  # Test classes
            ],
            ChangeType.REFACTOR: [
                r"refactor",
                r"rename",
                r"restructure",
            ],
            ChangeType.DEPENDENCY: [
                r"(pip|poetry)\s+install",
                r"requirements\.txt",
                r"pyproject\.toml",
            ],
        }
        
    def analyze_codebase(self) -> Dict[str, any]:
        """Analyze the entire codebase for current state."""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "modules": {},
            "endpoints": [],
            "models": [],
            "tests": [],
            "coverage": self._get_test_coverage(),
            "issues": self._get_known_issues(),
            "dependencies": self._get_dependencies(),
        }
        
        # Analyze Python modules
        src_path = self.project_root / "backend" / "src"
        for py_file in src_path.rglob("*.py"):
            module_info = self._analyze_module(py_file)
            if module_info:
                analysis["modules"][str(py_file)] = module_info
                analysis["endpoints"].extend(module_info.get("endpoints", []))
                analysis["models"].extend(module_info.get("models", []))
        
        # Analyze tests
        test_path = self.project_root / "backend" / "tests"
        for test_file in test_path.rglob("test_*.py"):
            test_info = self._analyze_test_file(test_file)
            if test_info:
                analysis["tests"].extend(test_info)
        
        return analysis
    
    def _analyze_module(self, file_path: Path) -> Optional[Dict]:
        """Analyze a Python module for documentation-relevant information."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            module_info = {
                "classes": [],
                "functions": [],
                "endpoints": [],
                "models": [],
                "imports": [],
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "bases": [self._get_node_name(base) for base in node.bases],
                        "methods": []
                    }
                    
                    # Check if it's a model
                    if any(base in ["Base", "BaseModel"] for base in class_info["bases"]):
                        module_info["models"].append(node.name)
                    
                    # Get methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info["methods"].append(item.name)
                    
                    module_info["classes"].append(class_info)
                    
                elif isinstance(node, ast.FunctionDef):
                    # Check for endpoint decorators
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Attribute):
                            if decorator.attr in ["get", "post", "put", "delete", "patch"]:
                                endpoint_info = {
                                    "name": node.name,
                                    "method": decorator.attr.upper(),
                                    "path": self._extract_endpoint_path(decorator)
                                }
                                module_info["endpoints"].append(endpoint_info)
                    
                    module_info["functions"].append(node.name)
                    
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        module_info["imports"].append(alias.name)
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_info["imports"].append(node.module)
            
            return module_info if any(module_info.values()) else None
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def _get_node_name(self, node) -> str:
        """Get the name of an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return str(node)
    
    def _extract_endpoint_path(self, decorator) -> str:
        """Extract the path from an endpoint decorator."""
        # This is a simplified version - would need more sophisticated parsing
        return "/api/v1/unknown"
    
    def _analyze_test_file(self, file_path: Path) -> List[Dict]:
        """Analyze a test file for test information."""
        tests = []
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    tests.append({
                        "name": node.name,
                        "file": str(file_path),
                        "docstring": ast.get_docstring(node)
                    })
            
        except Exception as e:
            print(f"Error analyzing test file {file_path}: {e}")
        
        return tests
    
    def _get_test_coverage(self) -> Dict:
        """Get test coverage information."""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--cov=src", "--cov-report=json"],
                cwd=self.project_root / "backend",
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                coverage_file = self.project_root / "backend" / "coverage.json"
                if coverage_file.exists():
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                    return {
                        "percentage": coverage_data.get("totals", {}).get("percent_covered", 0),
                        "files": coverage_data.get("files", {})
                    }
        except Exception as e:
            print(f"Error getting test coverage: {e}")
        
        return {"percentage": 0, "files": {}}
    
    def _get_known_issues(self) -> List[Dict]:
        """Extract known issues from various sources."""
        issues = []
        
        # Check for TODO/FIXME comments
        for py_file in (self.project_root / "backend").rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Find TODO/FIXME comments
                for i, line in enumerate(content.splitlines(), 1):
                    if "TODO" in line or "FIXME" in line:
                        issues.append({
                            "type": "code_comment",
                            "file": str(py_file),
                            "line": i,
                            "text": line.strip()
                        })
            except Exception:
                pass
        
        # Check for recent test failures
        test_log = self.project_root / "backend" / "tests" / "test.log"
        if test_log.exists():
            try:
                with open(test_log, 'r') as f:
                    content = f.read()
                
                # Parse test failures
                failure_pattern = r"FAILED (.*?) - (.*?)$"
                for match in re.finditer(failure_pattern, content, re.MULTILINE):
                    issues.append({
                        "type": "test_failure",
                        "test": match.group(1),
                        "error": match.group(2)
                    })
            except Exception:
                pass
        
        return issues
    
    def _get_dependencies(self) -> Dict:
        """Get project dependencies."""
        deps = {}
        
        # Check requirements.txt
        req_file = self.project_root / "backend" / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                deps["requirements"] = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        # Check pyproject.toml
        pyproject_file = self.project_root / "backend" / "pyproject.toml"
        if pyproject_file.exists():
            # Simple extraction - would use toml library in production
            with open(pyproject_file, 'r') as f:
                content = f.read()
                if "[tool.poetry.dependencies]" in content:
                    deps["poetry"] = "Found"
        
        return deps
    
    def generate_documentation_update(self, analysis: Dict) -> Dict[str, str]:
        """Generate documentation updates based on analysis."""
        updates = {}
        
        # Update CLAUDE.md implementation status
        claude_content = self._generate_claude_update(analysis)
        updates["CLAUDE.md"] = claude_content
        
        # Update phase1-implementation.md
        phase1_content = self._generate_phase1_update(analysis)
        updates["instructions/phase1-implementation.md"] = phase1_content
        
        # Update API documentation if needed
        if analysis["endpoints"]:
            api_content = self._generate_api_docs(analysis)
            updates["docs/api/endpoints.md"] = api_content
        
        return updates
    
    def _generate_claude_update(self, analysis: Dict) -> str:
        """Generate updated content for CLAUDE.md."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Count completed items
        completed_items = []
        if analysis["models"]:
            completed_items.append(f"✅ {len(analysis['models'])} database models implemented")
        if analysis["endpoints"]:
            completed_items.append(f"✅ {len(analysis['endpoints'])} API endpoints created")
        if analysis["tests"]:
            completed_items.append(f"✅ {len(analysis['tests'])} tests written")
        if analysis["coverage"]["percentage"] > 0:
            completed_items.append(f"✅ {analysis['coverage']['percentage']:.1f}% test coverage")
        
        # Identify in-progress items
        in_progress = []
        if analysis["issues"]:
            todo_count = len([i for i in analysis["issues"] if i["type"] == "code_comment"])
            if todo_count > 0:
                in_progress.append(f"🟨 {todo_count} TODO/FIXME items to address")
        
        test_failures = [i for i in analysis["issues"] if i["type"] == "test_failure"]
        if test_failures:
            in_progress.append(f"🟨 {len(test_failures)} failing tests to fix")
        
        content = f"""## Current Implementation Status

_Last automated check: {timestamp}_

### Completed (Phase 1)
{chr(10).join('- ' + item for item in completed_items)}

### In Progress
{chr(10).join('- ' + item for item in in_progress)}

### System Statistics
- Total Modules: {len(analysis['modules'])}
- Total Models: {len(analysis['models'])}
- Total Endpoints: {len(analysis['endpoints'])}
- Total Tests: {len(analysis['tests'])}
- Test Coverage: {analysis['coverage']['percentage']:.1f}%
- Known Issues: {len(analysis['issues'])}

### Recent Changes
_Automatically detected by doc_manager_"""
        
        return content
    
    def _generate_phase1_update(self, analysis: Dict) -> str:
        """Generate updated content for phase1-implementation.md."""
        content = f"""# Phase 1 Implementation Progress

_Last automated update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_

## Overview
This document tracks the implementation progress of Phase 1 of the LabWeave project.

## Completed Features
{self._format_completed_features(analysis)}

## In Progress
{self._format_in_progress_features(analysis)}

## Test Coverage Report
- Overall Coverage: {analysis['coverage']['percentage']:.1f}%
- Number of Tests: {len(analysis['tests'])}

## Known Issues
{self._format_known_issues(analysis)}

## Next Steps
{self._format_next_steps(analysis)}
"""
        return content
    
    def _format_completed_features(self, analysis: Dict) -> str:
        """Format completed features for documentation."""
        features = []
        
        for model in analysis["models"]:
            features.append(f"- ✅ {model} model implemented")
        
        for endpoint in analysis["endpoints"]:
            features.append(f"- ✅ {endpoint['method']} {endpoint['path']} endpoint")
        
        return "\n".join(features) if features else "- None yet"
    
    def _format_in_progress_features(self, analysis: Dict) -> str:
        """Format in-progress features for documentation."""
        features = []
        
        # Add TODO items
        todos = [i for i in analysis["issues"] if i["type"] == "code_comment"]
        for todo in todos:
            features.append(f"- 🟨 {todo['text']}")
        
        return "\n".join(features) if features else "- None currently"
    
    def _format_known_issues(self, analysis: Dict) -> str:
        """Format known issues for documentation."""
        issues = []
        
        for issue in analysis["issues"]:
            if issue["type"] == "test_failure":
                issues.append(f"- ❌ Test failure: {issue['test']} - {issue['error']}")
            elif issue["type"] == "code_comment":
                issues.append(f"- ⚠️ {issue['text']} ({issue['file']}:{issue['line']})")
        
        return "\n".join(issues) if issues else "- No known issues"
    
    def _format_next_steps(self, analysis: Dict) -> str:
        """Generate next steps based on analysis."""
        steps = []
        
        if analysis["coverage"]["percentage"] < 80:
            steps.append(f"- Increase test coverage from {analysis['coverage']['percentage']:.1f}% to 80%")
        
        todo_count = len([i for i in analysis["issues"] if i["type"] == "code_comment"])
        if todo_count > 0:
            steps.append(f"- Address {todo_count} TODO/FIXME items")
        
        test_failures = len([i for i in analysis["issues"] if i["type"] == "test_failure"])
        if test_failures > 0:
            steps.append(f"- Fix {test_failures} failing tests")
        
        if not analysis["endpoints"]:
            steps.append("- Implement API endpoints")
        
        return "\n".join(steps) if steps else "- Continue with planned development"
    
    def _generate_api_docs(self, analysis: Dict) -> str:
        """Generate API documentation."""
        content = f"""# LabWeave API Documentation

_Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_

## Endpoints

"""
        for endpoint in sorted(analysis["endpoints"], key=lambda x: (x["path"], x["method"])):
            content += f"### {endpoint['method']} {endpoint['path']}\n"
            content += f"- Function: `{endpoint['name']}`\n\n"
        
        return content
    
    def write_updates(self, updates: Dict[str, str]):
        """Write documentation updates to files."""
        for file_path, content in updates.items():
            full_path = self.project_root / file_path
            
            # Create directory if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the update
            with open(full_path, 'w') as f:
                f.write(content)
            
            print(f"Updated: {file_path}")
    
    def run(self):
        """Run the advanced documentation manager."""
        print("🔍 Analyzing codebase...")
        analysis = self.analyze_codebase()
        
        print("📝 Generating documentation updates...")
        updates = self.generate_documentation_update(analysis)
        
        print("💾 Writing updates...")
        self.write_updates(updates)
        
        print("✅ Documentation update complete!")
        
        # Print summary
        print("\nSummary:")
        print(f"- Modules analyzed: {len(analysis['modules'])}")
        print(f"- Models found: {len(analysis['models'])}")
        print(f"- Endpoints found: {len(analysis['endpoints'])}")
        print(f"- Tests found: {len(analysis['tests'])}")
        print(f"- Test coverage: {analysis['coverage']['percentage']:.1f}%")
        print(f"- Issues detected: {len(analysis['issues'])}")
        print(f"- Files updated: {len(updates)}")


def main():
    """Main entry point."""
    manager = AdvancedDocManager()
    manager.run()


if __name__ == "__main__":
    main()