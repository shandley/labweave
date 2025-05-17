# LabWeave Automated Development Quick Reference

## 🚀 Quick Start

```bash
cd backend
source venv/bin/activate
python smart_start.py
```

That's it! The smart start system handles everything else.

## 🛠️ Make Commands

```bash
make smart-start  # Full automated startup (recommended)
make check       # Pre-flight validation only
make fix         # Automated fixes only
make test        # Run test suite
make clean       # Clean cache files
```

## 📝 What Gets Automated

### Pre-flight Checks
- SQLAlchemy reserved word detection
- Model-schema consistency validation
- Import cycle detection
- Pydantic compatibility checks
- Environment setup validation

### Automated Fixes
- Pydantic import corrections
- SQLAlchemy metadata naming conflicts
- Configuration issues
- Missing __init__.py files
- Permission issues

### Startup Process
1. Pre-flight validation
2. Automated error fixing
3. Test suite execution
4. Database service check
5. Server startup with proper configuration

## 🔧 Individual Tools

```bash
# Run specific tools if needed
python preflight_check.py    # Validation only
python automated_fix.py      # Fixes only
python test_startup.py       # Tests only
```

## 📚 Documentation

- Full guide: `/backend/AUTOMATED_TESTING.md`
- Implementation tracking: `/instructions/phase1-implementation.md`
- Development setup: `/instructions/development-setup-guide.md`

## ⚠️ Common Issues

### Virtual Environment Not Found
```bash
# Recreate if needed
./setup-dev.sh
```

### Docker Not Running
```bash
# Start Docker Desktop first, then:
cd ../infrastructure/docker
docker-compose up -d
```

### Import Errors
```bash
# Make sure venv is activated
source venv/bin/activate
```

## 🎯 Benefits

1. **No manual debugging** - Common errors fixed automatically
2. **Faster development** - One command to start
3. **Better error messages** - Clear indication of issues
4. **Learning tool** - Shows what was fixed and why

## 💡 Tips

- Always use `smart_start.py` for development
- Check `AUTOMATED_TESTING.md` for adding new fixes
- Run `make check` before commits
- Use `make clean` to remove cache files