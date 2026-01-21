# MediGuard: Multi-Agent Clinical Compliance Orchestrator

A production-minded prototype for automated clinical compliance checking and PHI redaction using LangGraph, Ollama (local LLM), Pinecone RAG, and custom guardrails.


## Architecture Overview

- **API Layer**: FastAPI for REST endpoints
- **Orchestration**: LangGraph for multi-agent workflow
- **RAG**: Pinecone for policy retrieval with metadata filtering
- **LLM**: Ollama (local LLM) with structured outputs (JSON mode)
- **Guardrails**: PHI detection, redaction, leakage checks, prompt injection defenses

## Getting Started

This project is being built step-by-step:
- **Step 1**: ✅ Scope Definition - See `docs/scope_specification.md`
- **Step 2**: ✅ Compliance Frameworks - See `docs/compliance_frameworks.md`
- **Step 3**: ✅ PHI Handling Standard - See `docs/phi_handling_standard.md`
- **Step 4**: ✅ Define Outputs - See `docs/outputs_specification.md`
- **Step 5**: ✅ Threat Model & Trust Boundaries - See `docs/threat_model.md`
- **Step 6**: ✅ Data Retention Strategy - See `docs/data_retention.md`
- **Step 7**: ✅ Success Metrics - See `docs/metrics_specification.md`
- **Step 8**: ✅ Gold Set + Baseline - See `data/gold_set/README.md`
- **Step 9**: ✅ Stack & Repository Layout - See `docs/stack_and_layout.md`
- **Step 10**: ✅ CI/CD Guardrails - See `.github/workflows/ci.yml`
- **LLM Configuration**: See `docs/llm_configuration.md` (Ollama setup and structured outputs)

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
