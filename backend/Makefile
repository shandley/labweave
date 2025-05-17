# LabWeave Backend Makefile

.PHONY: help install test start smart-start check fix clean docs docs-advanced

help:
	@echo "LabWeave Backend Commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run all tests"
	@echo "  make start         - Start server (basic)"
	@echo "  make smart-start   - Start with all checks and fixes"
	@echo "  make check         - Run pre-flight checks only"
	@echo "  make fix           - Run automated fixes"
	@echo "  make docs          - Update documentation (basic)"
	@echo "  make docs-advanced - Update documentation (full analysis)"
	@echo "  make clean         - Clean cache files"

install:
	pip install -r requirements.txt

test:
	pytest -v

start:
	uvicorn src.main:app --reload --port 8000

smart-start:
	source venv/bin/activate && python smart_start.py

check:
	source venv/bin/activate && python preflight_check.py

fix:
	source venv/bin/activate && python automated_fix.py

docs:
	source venv/bin/activate && python doc_manager.py

docs-advanced:
	source venv/bin/activate && python doc_manager_advanced.py

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete