# MediGuard: Scope Specification

## Executive Summary

MediGuard is a Multi-Agent Clinical Compliance Orchestrator that automates compliance checking and PHI redaction for clinical documents. This document defines the exact problem scope to prevent scope creep and ensure measurable outcomes.

---

## 1. Problem Statement

Clinical compliance teams spend significant time manually:
- Reviewing documents for Protected Health Information (PHI)
- Checking documents against compliance frameworks (e.g., HIPAA)
- Producing redacted versions and audit reports
- Routing documents based on compliance risk

**Goal**: Automate this process with AI agents while maintaining safety, auditability, and accuracy.

---

## 2. Document Types in Scope

### Initial Scope (v1.0)
- **Clinical Notes**: Progress notes, discharge summaries, consultation reports
- **Forms**: Intake forms, consent forms
- **Reports**: Lab reports, imaging reports (text-based)

### Formats Supported
- Plain text (.txt)
- PDF documents (.pdf)
- Microsoft Word documents (.docx)

### Out of Scope (v1.0)
- Scanned images (OCR not included)
- Audio/video transcripts (future)
- Structured data (HL7, FHIR - future)
- Real-time document streams

---

## 3. Compliance Regimes

### Primary Focus (v1.0)
1. **HIPAA De-identification (Safe Harbor Method)**
   - Removal of 18 specified identifiers per 45 CFR §164.514(b)(2)
   - Focus on deterministic rule-based detection

2. **Internal Documentation Checklist**
   - Organization-specific compliance requirements
   - Document completeness checks
   - Required section presence (HPI, Assessment, Plan, etc.)

### Out of Scope (v1.0)
- Expert Determination method (future)
- State-specific privacy regulations (CA, NY, etc.)
- International regulations (GDPR, etc.)
- Real-time enforcement (batch processing only)

---

## 4. System Outputs (Contract with Users)

The system must produce **four types of outputs**:

### 4.1 Redacted Document
- **Format**: Same as input (text/PDF/DOCX)
- **Content**: Original document with PHI replaced by typed placeholders:
  - `[PATIENT_NAME]`
  - `[DATE_OF_BIRTH]`
  - `[MRN]`
  - `[SSN]`
  - `[PHONE]`
  - `[EMAIL]`
  - `[ADDRESS]`
  - etc.
- **Purpose**: Safe version for sharing/storage

### 4.2 Compliance Findings (JSON)
- **Format**: Structured JSON with schema validation
- **Content**:
  ```json
  {
    "run_id": "uuid",
    "document_id": "uuid",
    "document_type": "progress_note",
    "findings": [
      {
        "rule_id": "HIPAA_164514b_3.10",
        "status": "pass|fail|needs_review",
        "evidence_chunk_ids": ["policy_chunk_123"],
        "rationale": "Section 3.10 requires...",
        "confidence": 0.95
      }
    ],
    "overall_status": "pass|fail|needs_review",
    "risk_score": 0.25
  }
  ```
- **Purpose**: Machine-readable results for automation/integration

### 4.3 Human-Readable Audit Report
- **Format**: Markdown (and optionally PDF)
- **Content**:
  - Executive summary
  - Document metadata
  - Per-requirement compliance status
  - Evidence citations (policy section references)
  - Redaction summary (counts by PHI type)
  - Remediation suggestions
- **Purpose**: Human review and audit trail

### 4.4 Routing Decision
- **Format**: JSON
- **Content**:
  ```json
  {
    "route_action": "auto_approve|requires_review|reject",
    "confidence": 0.92,
    "reason": "All requirements met with high confidence",
    "risk_factors": []
  }
  ```
- **Purpose**: Automated workflow routing

---

## 5. Success Metrics

### 5.1 Efficiency Metrics
- **Baseline**: Manual audit time per document
- **Target**: 50% reduction in audit time
- **Measurement**: Time from document submission to final decision

### 5.2 Accuracy Metrics
- **Target**: 92% accuracy in compliance matching
  - Precision: % of flagged issues that are actual violations
  - Recall: % of actual violations that are detected
- **Measurement**: Against labeled gold set (synthetic documents)

### 5.3 Safety Metrics
- **PHI Leakage Rate**: < 0.1% (measured as % of documents where redacted output contains PHI)
- **False Positive Rate**: < 5% (compliant documents incorrectly flagged)
- **False Negative Rate**: < 8% (non-compliant documents missed)

### 5.4 Operational Metrics
- **Processing Latency**: < 30 seconds per document (95th percentile)
- **Throughput**: Support 100 documents/hour per instance
- **Cost per Document**: Track and optimize

---

## 6. Constraints & Boundaries

### Security Constraints
- **No PHI in logs**: All logging must be PHI-free
- **No PHI in vector DB**: Only policy chunks (non-PHI) stored in Pinecone
- **No PHI in analytics**: Aggregated metrics only
- **Ephemeral processing**: Patient documents processed in-memory; stored only if org policy allows

### Trust Boundaries
- **Ollama LLM (Local)**: Receives redacted documents only (after PHI removal), runs locally for privacy
- **Pinecone**: Stores policy chunks only (never patient data)
- **Logs/Audit Trail**: PHI-sanitized metadata only
- **Reports**: Contain redacted content only

### Technical Constraints
- **Synthetic data only**: No real PHI in development/testing
- **Production prototype**: Secure and testable, but validate with legal/compliance before real deployment
- **Fail-closed design**: If PHI detected in output, block the document

---

## 7. Non-Goals (What We're NOT Building)

- Real-time streaming compliance checking
- Multi-jurisdiction conflict resolution (v1.0)
- Expert Determination workflows (v1.0)
- OCR for scanned documents
- Direct EHR integration (API-first design)
- Legal advice or interpretation
- Automated remediation/editing of documents

---

## 8. Success Criteria for Step 1

This scope specification is complete when:
- [x] Document types are clearly defined
- [x] Compliance frameworks are specified
- [x] Output formats are documented with schemas
- [x] Success metrics are measurable and agreed upon
- [x] Constraints and boundaries are explicit
- [x] Non-goals are stated to prevent scope creep

---

## 9. Next Steps

After scope approval, proceed to:
- **Step 2**: Pick compliance frameworks and jurisdictions (expand on HIPAA + internal checklist details)
- **Step 3**: Choose PHI handling standard (Safe Harbor implementation details)

---

**Document Version**: 1.0  
**Last Updated**: Jan 20 , 2026  
**Status**: Reviewed and Approved
