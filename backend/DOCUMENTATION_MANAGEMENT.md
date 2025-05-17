# LabWeave Documentation Management System

## Overview

The LabWeave project includes an automatic documentation management system that keeps project documentation in sync with the codebase. This system runs automatically when you start the development server and can also be run manually.

## Components

### doc_manager.py
Basic documentation manager that:
- Detects file changes using MD5 hashes
- Updates documentation timestamps
- Maintains configuration in `doc_config.json`

### doc_manager_advanced.py
Advanced documentation manager with:
- Semantic code analysis using Python AST
- Automatic detection of:
  - New models, endpoints, and functions
  - Test coverage statistics
  - TODO/FIXME comments
  - Test failures
- Comprehensive documentation generation

## Automatic Updates

The system automatically updates:

1. **CLAUDE.md**
   - Implementation status
   - System statistics
   - Known issues
   - Development priorities

2. **instructions/phase1-implementation.md**
   - Progress tracking
   - Completed features
   - Test coverage reports
   - Next steps

3. **docs/api/endpoints.md** (when endpoints exist)
   - API endpoint documentation
   - Auto-generated from code

## Usage

### Automatic (with smart_start.py)
```bash
cd backend
python smart_start.py
```
The documentation check runs automatically before starting the server.

### Manual Updates
```bash
cd backend

# Basic updates (fast)
python doc_manager.py

# Advanced analysis (comprehensive)
python doc_manager_advanced.py
```

## Configuration

The system uses `doc_config.json` to track:
- Monitored file paths
- File hashes for change detection
- Documentation file locations
- Code pattern definitions

## How It Works

1. **Change Detection**
   - Monitors specified directories
   - Calculates file hashes
   - Compares with previous scan

2. **Code Analysis**
   - Parses Python files using AST
   - Identifies classes, functions, decorators
   - Extracts test information
   - Finds TODO/FIXME comments

3. **Documentation Generation**
   - Updates relevant sections
   - Preserves manual content
   - Adds timestamps
   - Generates statistics

4. **Smart Updates**
   - Only updates when changes detected
   - Preserves existing structure
   - Non-destructive updates

## Adding New Documentation

To add a new document to auto-update:

1. Edit `doc_manager.py` or `doc_manager_advanced.py`
2. Add document configuration
3. Define update logic
4. Test with manual run

## Best Practices

1. **Run regularly**: Let smart_start.py handle it automatically
2. **Review updates**: Check generated documentation for accuracy
3. **Manual edits**: The system preserves manual documentation edits
4. **Commit changes**: Include auto-generated updates in commits

## Troubleshooting

If documentation updates fail:
1. Check file permissions
2. Verify paths in config
3. Run with Python directly for error messages
4. Check `doc_config.json` for issues

## Future Enhancements

Planned improvements:
- Git integration for change detection
- Markdown section preservation
- Multi-format documentation support
- Real-time monitoring mode
- Documentation versioning