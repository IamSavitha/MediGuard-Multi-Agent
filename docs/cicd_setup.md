# MediGuard: CI/CD Setup Guide

## Summary

This document describes the CI/CD guardrails set up for MediGuard to ensure code quality, security, and maintainability.

---

## 1. Pre-commit Hooks

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

### Hooks Configured

- **Black**: Code formatting (line length: 100)
- **Ruff**: Fast Python linter (replaces flake8, isort)
- **MyPy**: Type checking (non-blocking for now)
- **General Checks**: Trailing whitespace, end-of-file, YAML/JSON validation
- **Secret Scanning**: detect-secrets baseline

### Run Manually

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only (automatic on commit)
pre-commit run
```

---

## 2. GitHub Actions CI

### Workflows

**`.github/workflows/ci.yml`** runs on push/PR:

1. **Lint Job**: Ruff, Black, MyPy
2. **Test Job**: pytest with PostgreSQL service
3. **Secrets Scan**: detect-secrets audit
4. **Docker Build**: Verify Dockerfile builds

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run linters
ruff check src/ tests/
black --check src/ tests/
mypy src/ || true

# Run tests
pytest tests/ -v
```

---

## 3. Testing Setup

### Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── unit/               # Unit tests
│   └── test_*.py
└── integration/        # Integration tests
    └── test_*.py
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# With coverage (requires pytest-cov)
pytest --cov=src/mediguard --cov-report=html

# Specific test file
pytest tests/unit/test_gold_set_validation.py -v
```

### Test Markers

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow tests (skip with `-m "not slow"`)

---

## 4. Secret Scanning

### Baseline

`.secrets.baseline` stores known false positives (UUIDs, test data, etc.)

### Audit Secrets

```bash
# Scan for new secrets
detect-secrets scan --baseline .secrets.baseline

# Audit baseline (review flagged secrets)
detect-secrets audit .secrets.baseline
```

### Adding False Positives

When legitimate secrets-like strings are found:
1. Run `detect-secrets scan --baseline .secrets.baseline`
2. Review and audit
3. Commit updated `.secrets.baseline`

---

## 5. Docker Build

### Build Locally

```bash
# Build image
docker build -t mediguard:latest .

# Run container
docker run -p 8000:8000 mediguard:latest

# Test with docker-compose
docker-compose up --build
```

### Health Check

Dockerfile includes health check (requires `/health` endpoint)

---

## 6. Code Quality Standards

### Formatting

- **Line Length**: 100 characters
- **Tool**: Black
- **Auto-format**: `black src/ tests/`

### Linting

- **Tool**: Ruff
- **Checks**: E, W, F, I, N, UP, B, C4, SIM
- **Fix auto-fixable**: `ruff check --fix src/ tests/`

### Type Checking

- **Tool**: MyPy
- **Strictness**: Gradual (ignore missing imports for now)
- **Target**: Python 3.11+

---

## 7. Success Criteria

CI/CD setup is complete when:
- [x] Pre-commit hooks configured
- [x] GitHub Actions workflow created
- [x] Test structure and fixtures in place
- [x] Secret scanning baseline created
- [x] Dockerfile created
- [x] Code quality tools configured (Black, Ruff, MyPy)

---

**Document Version**: 1.0  
**Last Updated**: Jan 20, 2026  
**Status**: Complete
