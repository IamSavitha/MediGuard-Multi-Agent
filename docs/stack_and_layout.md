# MediGuard: Stack & Repository Layout

## Executive Summary

This document defines the technology stack and repository layout for MediGuard. We're using Python + FastAPI + LangGraph + Pinecone + Ollama + Postgres, with a monolith-first approach for speed, with modular boundaries for future splitting.

---

## 1. Technology Stack

### 1.1 Core Stack

**Language**: Python 3.11+

**Web Framework**: FastAPI
- REST API endpoints
- Async support
- Automatic OpenAPI docs
- Request validation

**Orchestration**: LangGraph
- Multi-agent workflow
- State machine
- Durable execution support

**Vector DB**: Pinecone
- Policy chunk storage
- Semantic search
- Metadata filtering

**LLM**: Ollama
- Local model execution
- Privacy-preserving
- Model variety (Llama, Mistral, etc.)

**Database**: PostgreSQL
- Compliance findings
- Audit logs
- Run metadata

**Embeddings**: TBD (OpenAI embeddings API or local model)
- Policy chunk embeddings
- Semantic search support

### 1.2 Supporting Stack

**Document Processing**:
- `pypdf` or `pdfplumber`: PDF parsing
- `python-docx`: DOCX parsing
- `python-magic`: File type detection

**PHI Detection**:
- `regex`: Pattern matching
- `spacy` or `scispacy`: Named Entity Recognition
- Custom rule-based detectors

**Validation**:
- `pydantic`: Data validation and schemas
- `jsonschema`: JSON schema validation (if needed)

**Testing**:
- `pytest`: Unit and integration tests
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting

**Code Quality**:
- `black`: Code formatting
- `ruff` or `flake8`: Linting
- `mypy`: Type checking

**Monitoring**:
- Structured logging (Python `logging`)
- Metrics (custom or Prometheus)

**Infrastructure**:
- `docker`: Containerization
- `docker-compose`: Local development
- `poetry` or `pip`: Dependency management

---

## 2. Repository Layout

### 2.1 High-Level Structure

```
Mediguard/
├── .github/                  # GitHub workflows
│   └── workflows/
│       ├── ci.yml           # CI pipeline
│       └── test.yml         # Test automation
├── config/                   # Configuration files
│   ├── ollama.yaml          # Ollama config
│   ├── retention.yaml       # Data retention config
│   └── logging.yaml         # Logging config
├── data/                     # Data directory
│   ├── gold_set/            # Labeled gold set (synthetic)
│   │   ├── documents/       # Synthetic documents
│   │   └── labels/          # Labels (PHI spans, compliance)
│   └── synthetic/           # Generated synthetic data
├── docs/                     # Documentation
│   ├── *.md                 # Spec documents
│   └── architecture/        # Architecture diagrams
├── policies/                 # Policy documents
│   ├── hipaa/               # HIPAA policy documents
│   └── internal/            # Internal policy documents
├── src/                      # Source code
│   ├── mediguard/
│   │   ├── __init__.py
│   │   ├── api/             # FastAPI routes
│   │   ├── agents/          # LangGraph agents
│   │   ├── core/            # Core models and schemas
│   │   ├── detectors/       # PHI detection
│   │   ├── llm/             # Ollama client wrapper
│   │   ├── orchestrator/    # LangGraph workflow
│   │   ├── redaction/       # PHI redaction engine
│   │   ├── retrieval/       # RAG retrieval
│   │   ├── storage/         # Database models and access
│   │   └── utils/           # Utilities
│   └── scripts/             # Utility scripts
│       ├── ingest_policies.py
│       └── generate_synthetic_data.py
├── tests/                    # Tests
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── fixtures/            # Test fixtures
├── .env.example             # Example environment variables
├── .gitignore
├── docker-compose.yml       # Docker compose for local dev
├── Dockerfile               # Production Docker image
├── pyproject.toml           # Poetry/pip dependencies
├── README.md
└── requirements.txt         # Pip requirements (if not using poetry)
```

### 2.2 Detailed Structure

#### `src/mediguard/api/` - FastAPI Routes

```
api/
├── __init__.py
├── main.py                  # FastAPI app initialization
├── routes/
│   ├── __init__.py
│   ├── validate.py         # POST /validate
│   ├── runs.py             # GET /runs/{id}
│   └── review.py           # POST /runs/{id}/review
├── middleware/
│   ├── __init__.py
│   ├── auth.py             # Authentication middleware
│   └── logging.py          # Request logging middleware
└── dependencies.py         # FastAPI dependencies
```

#### `src/mediguard/core/` - Core Models & Schemas

```
core/
├── __init__.py
├── models/                  # Pydantic models
│   ├── __init__.py
│   ├── document.py         # Document models
│   ├── findings.py         # Finding models
│   ├── redaction.py        # Redaction models
│   └── state.py            # LangGraph state models
└── schemas/                 # JSON schemas
    ├── __init__.py
    └── compliance.py       # Compliance finding schemas
```

#### `src/mediguard/agents/` - LangGraph Agents

```
agents/
├── __init__.py
├── base.py                 # Base agent class
├── classify.py             # Document classification agent
├── compliance_matcher.py   # Compliance matching agent
├── retrieval.py            # Policy retrieval agent
├── redaction.py            # PHI redaction agent
├── verifier.py             # Verification agent
└── router.py               # Risk routing agent
```

#### `src/mediguard/orchestrator/` - LangGraph Workflow

```
orchestrator/
├── __init__.py
├── graph.py                # LangGraph workflow definition
├── nodes.py                # Node implementations
├── edges.py                # Edge/conditional logic
└── checkpointer.py         # Durable execution checkpointing
```

#### `src/mediguard/detectors/` - PHI Detection

```
detectors/
├── __init__.py
├── base.py                 # Base detector interface
├── regex.py                # Regex-based detectors
├── ner.py                  # NER-based detectors
├── llm.py                  # LLM-based detectors
└── validator.py            # Post-redaction validator
```

#### `src/mediguard/redaction/` - PHI Redaction

```
redaction/
├── __init__.py
├── engine.py               # Redaction engine
├── placeholders.py         # Placeholder definitions
└── mapping.py              # Redaction mapping (if reversible)
```

#### `src/mediguard/retrieval/` - RAG Retrieval

```
retrieval/
├── __init__.py
├── pinecone_client.py      # Pinecone client wrapper
├── retriever.py            # Policy retrieval logic
└── embeddings.py           # Embedding generation
```

#### `src/mediguard/llm/` - Ollama Integration

```
llm/
├── __init__.py
├── client.py               # Ollama client wrapper
├── structured_outputs.py   # JSON mode parsing
└── prompts.py              # Prompt templates
```

#### `src/mediguard/storage/` - Database

```
storage/
├── __init__.py
├── database.py             # Database connection
├── models.py               # SQLAlchemy models
├── repositories/           # Data access layer
│   ├── __init__.py
│   ├── findings.py
│   └── runs.py
└── migrations/             # Alembic migrations
    └── versions/
```

---

## 3. Dependency Management

### 3.1 Poetry (Recommended)

**File**: `pyproject.toml`

```toml
[tool.poetry]
name = "mediguard"
version = "0.1.0"
description = "Multi-Agent Clinical Compliance Orchestrator"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
langgraph = "^0.0.20"
langchain = "^0.1.0"
langchain-community = "^0.0.10"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
pinecone-client = "^2.2.0"
ollama = "^0.1.0"
psycopg2-binary = "^2.9.9"
sqlalchemy = "^2.0.23"
alembic = "^1.12.1"
pypdf = "^3.17.0"
python-docx = "^1.1.0"
spacy = "^3.7.0"
regex = "^2023.10.3"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
pytest-cov = "^4.1.0"
black = "^23.11.0"
ruff = "^0.1.6"
mypy = "^1.7.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
```

### 3.2 Requirements.txt (Alternative)

**File**: `requirements.txt`

```
fastapi==0.104.0
uvicorn==0.24.0
langgraph==0.0.20
langchain==0.1.0
langchain-community==0.0.10
pydantic==2.5.0
pydantic-settings==2.1.0
pinecone-client==2.2.0
ollama==0.1.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.12.1
pypdf==3.17.0
python-docx==1.1.0
spacy==3.7.0
regex==2023.10.3
```

---

## 4. Environment Configuration

### 4.1 Environment Variables

**File**: `.env.example`

```bash
# Application
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=your-api-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mediguard

# Pinecone
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=mediguard-policies

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.1:8b

# Embeddings (if using OpenAI embeddings)
# OPENAI_API_KEY=your-openai-api-key

# Security
JWT_SECRET=your-jwt-secret-key
ENCRYPTION_KEY=your-encryption-key

# Data Retention
RETENTION_RAW_DOCUMENTS_ENABLED=false
RETENTION_REDACTED_DOCUMENTS_DAYS=30
RETENTION_FINDINGS_DAYS=365
RETENTION_AUDIT_LOGS_DAYS=90
```

---

## 5. Docker Setup

### 5.1 Dockerfile

**File**: `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "mediguard.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 Docker Compose

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://mediguard:password@db:5432/mediguard
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - db
    volumes:
      - ./config:/app/config

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=mediguard
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mediguard
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  postgres_data:
  ollama_data:
```

---

## 6. Development Workflow

### 6.1 Setup

```bash
# Clone repository
git clone <repo-url>
cd Mediguard

# Install dependencies (Poetry)
poetry install

# Or (pip)
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your values

# Run database migrations
alembic upgrade head

# Install Spacy model
python -m spacy download en_core_web_sm

# Run tests
pytest
```

### 6.2 Running Locally

```bash
# Start services (Docker Compose)
docker-compose up

# Or run API directly
poetry run uvicorn mediguard.api.main:app --reload
```

---

## 7. Success Criteria for Step 9

This stack and layout specification is complete when:
- [x] Technology stack is defined
- [x] Repository layout is specified
- [x] Directory structure is detailed
- [x] Dependency management is configured
- [x] Environment configuration is documented
- [x] Docker setup is provided

---

## 8. Next Steps

After stack and layout approval, proceed to:
- **Step 10**: Set up CI/CD guardrails (before logic)
- **Step 11**: Define canonical data model (implement Pydantic models)

---

**Document Version**: 1.0  
**Last Updated**: Jan 20, 2026  
**Status**: Draft - Awaiting Review
