# MediGuard: Multi-Agent Clinical Compliance Orchestrator

A production-minded prototype for automated clinical compliance checking and PHI redaction using LangGraph, GPT-4o, Pinecone RAG, and custom guardrails.


## Architecture Overview

- **API Layer**: FastAPI for REST endpoints
- **Orchestration**: LangGraph for multi-agent workflow
- **RAG**: Pinecone for policy retrieval with metadata filtering
- **LLM**: GPT-4o with structured outputs
- **Guardrails**: PHI detection, redaction, leakage checks, prompt injection defenses

## Getting Started

This project is being built step-by-step:
- **Step 1**: ✅ Scope Definition - See `docs/scope_specification.md`
- **Step 2**: 🔄 Compliance Frameworks - See `docs/compliance_frameworks.md`

## Important Disclaimers

- **Production Prototype**: This is a production-minded prototype, not a legal product. Validate with compliance/legal for real deployments.
- **No Real PHI**: Never use real PHI in dev/test—use synthetic documents only.
- **Ephemeral Processing**: Patient documents are processed ephemerally; stored only if org policy allows.

## Project Structure

```
Mediguard/
├── docs/              # Documentation and specifications
├── src/               # Source code (to be created)
├── tests/             # Test files (to be created)
├── policies/          # Policy documents (to be created)
├── data/              # Synthetic test data (to be created)
└── README.md
```

## License

[To be determined]
