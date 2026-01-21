# MediGuard: Outputs Specification (Contract with Users)

## Executive Summary

This document defines the four output types that MediGuard produces. These outputs represent the "contract" with users—what they can expect from the system. A stable output schema makes the system integratable with EHR systems, ticketing systems, and audit tools.

---

## 1. Output Design Principles

### 1.1 Principles

- **Stable Schema**: Output formats don't change without versioning
- **Machine-Readable**: JSON outputs for automation/integration
- **Human-Readable**: Reports for audit and review
- **Evidence-Grounded**: All findings reference policy sources
- **Auditable**: All outputs support audit trails
- **PHI-Safe**: All outputs contain redacted content only

### 1.2 Tradeoffs

**More Outputs = More Value**:
- ✅ More use cases supported
- ✅ Better integration with existing tools
- ✅ Richer audit trails

**More Outputs = More Risk**:
- ⚠️ Every output increases leakage risk
- ⚠️ Larger test surface
- ⚠️ More complexity in validation

**Decision**: Separate machine-readable findings from narrative reports to keep automation reliable.

---

## 2. Output Types Overview

The system produces **four types of outputs**:

1. **Redacted Document**: Safe version of the original document
2. **Compliance Findings (JSON)**: Machine-readable structured results
3. **Audit Report**: Human-readable narrative report
4. **Routing Decision**: Automated workflow routing recommendation

---

## 3. Output 1: Redacted Document

### 3.1 Purpose

A PHI-safe version of the original document for sharing, storage, or further processing.

### 3.2 Format

**Input Format Preserved**: Same format as input (text/PDF/DOCX)

**Content**: Original document with PHI replaced by typed placeholders

### 3.3 Placeholder Types

All PHI is replaced with typed placeholders:

| Placeholder | Original PHI Type | Example |
|------------|------------------|---------|
| `[PATIENT_NAME]` | Patient names | "John Smith" → `[PATIENT_NAME]` |
| `[DATE_OF_BIRTH]` | Date of birth | "01/15/1985" → `[DATE_OF_BIRTH]` |
| `[AGE_89_PLUS]` | Ages > 89 | "95 years old" → `[AGE_89_PLUS]` |
| `[MRN]` | Medical record number | "MRN12345" → `[MRN]` |
| `[SSN]` | Social Security Number | "123-45-6789" → `[SSN]` |
| `[PHONE]` | Telephone number | "(555) 123-4567" → `[PHONE]` |
| `[FAX]` | Fax number | "(555) 123-4568" → `[FAX]` |
| `[EMAIL]` | Email address | "john@example.com" → `[EMAIL]` |
| `[ADDRESS]` | Street address | "123 Main St" → `[ADDRESS]` |
| `[CITY]` | City name | "Boston" → `[CITY]` |
| `[ZIP_CODE]` | ZIP code | "02115" → `[ZIP_CODE]` |
| `[BENEFICIARY_ID]` | Health plan beneficiary number | "BEN12345" → `[BENEFICIARY_ID]` |
| `[ACCOUNT_NUMBER]` | Account number | "ACC12345" → `[ACCOUNT_NUMBER]` |
| `[LICENSE_NUMBER]` | Certificate/license number | "LIC12345" → `[LICENSE_NUMBER]` |
| `[VEHICLE_ID]` | Vehicle identifier | "ABC123" → `[VEHICLE_ID]` |
| `[DEVICE_ID]` | Device identifier | "DEV12345" → `[DEVICE_ID]` |
| `[URL]` | Web URL | "https://example.com" → `[URL]` |
| `[IP_ADDRESS]` | IP address | "192.168.1.1" → `[IP_ADDRESS]` |
| `[BIOMETRIC_ID]` | Biometric identifier | Fingerprint/voiceprint → `[BIOMETRIC_ID]` |
| `[PHOTO_IMAGE]` | Photographic image | Face photo → `[PHOTO_IMAGE]` |
| `[UNIQUE_ID]` | Other unique identifier | Any other ID → `[UNIQUE_ID]` |

### 3.4 Metadata (Optional)

**Redacted Document Metadata** (stored separately):
```json
{
  "document_id": "uuid",
  "redaction_timestamp": "2026-01-20T10:30:00Z",
  "redaction_method": "safe_harbor",
  "placeholders_used": {
    "[PATIENT_NAME]": 5,
    "[DATE_OF_BIRTH]": 1,
    "[MRN]": 2,
    "[PHONE]": 1
  },
  "redaction_summary": {
    "total_redactions": 9,
    "phi_types_detected": ["patient_name", "date_of_birth", "mrn", "phone"]
  }
}
```

**Note**: Metadata does NOT include original PHI values (non-reversible by design in v1.0)

### 3.5 Example

**Original Document**:
```
Patient: John Smith
DOB: 01/15/1985
MRN: MRN12345
Phone: (555) 123-4567

History of Present Illness:
The patient presented with chest pain...
```

**Redacted Document**:
```
Patient: [PATIENT_NAME]
DOB: [DATE_OF_BIRTH]
MRN: [MRN]
Phone: [PHONE]

History of Present Illness:
The patient presented with chest pain...
```

---

## 4. Output 2: Compliance Findings (JSON)

### 4.1 Purpose

Machine-readable structured results for automation, integration with EHR systems, ticketing systems, and audit tools.

### 4.2 Schema (Pydantic)

```python
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime
from uuid import UUID

class EvidenceChunk(BaseModel):
    """Reference to policy chunk used as evidence"""
    chunk_id: str = Field(..., description="Pinecone chunk ID")
    policy_id: str = Field(..., description="Policy identifier (e.g., HIPAA_164514b_3.10)")
    excerpt: Optional[str] = Field(None, description="Relevant excerpt from policy (non-PHI)")

class Finding(BaseModel):
    """Individual compliance finding"""
    rule_id: str = Field(..., description="Compliance rule ID (e.g., HIPAA_SF_001)")
    status: Literal["pass", "fail", "needs_review"] = Field(
        ..., 
        description="Compliance status: pass = compliant, fail = violation, needs_review = ambiguous"
    )
    evidence_chunk_ids: List[str] = Field(
        ..., 
        description="List of policy chunk IDs used as evidence"
    )
    rationale: str = Field(
        ..., 
        description="Explanation of the finding, citing policy sections"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score (0.0-1.0)"
    )
    document_excerpt_hash: Optional[str] = Field(
        None, 
        description="Hash of relevant document excerpt (for audit, not PHI)"
    )
    remediation_suggestion: Optional[str] = Field(
        None, 
        description="Suggested remediation if status is 'fail'"
    )

class RedactionSummary(BaseModel):
    """Summary of PHI redaction"""
    total_redactions: int = Field(..., description="Total number of PHI redactions")
    phi_types_detected: List[str] = Field(..., description="List of PHI types found (e.g., ['patient_name', 'mrn'])")
    placeholders_used: dict[str, int] = Field(..., description="Count of each placeholder type used")
    redaction_method: str = Field(..., description="Method used (e.g., 'safe_harbor')")

class ComplianceResult(BaseModel):
    """Complete compliance checking result"""
    run_id: UUID = Field(..., description="Unique run identifier")
    document_id: UUID = Field(..., description="Document identifier")
    document_type: str = Field(..., description="Document type (e.g., 'progress_note')")
    timestamp: datetime = Field(..., description="When the check was performed")
    
    findings: List[Finding] = Field(..., description="List of compliance findings")
    overall_status: Literal["pass", "fail", "needs_review"] = Field(
        ..., 
        description="Overall compliance status"
    )
    risk_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Overall risk score (0.0 = low risk, 1.0 = high risk)"
    )
    
    redaction_summary: RedactionSummary = Field(..., description="Summary of PHI redaction")
    
    policy_versions_used: List[str] = Field(
        ..., 
        description="List of policy versions checked (e.g., ['HIPAA_v1.0', 'INT_DOC_v1.0'])"
    )
    jurisdiction: str = Field(..., description="Jurisdiction checked (e.g., 'US_FEDERAL')")
    
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
```

### 4.3 JSON Schema Example

```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_id": "660e8400-e29b-41d4-a716-446655440001",
  "document_type": "progress_note",
  "timestamp": "2026-01-20T10:30:00Z",
  "findings": [
    {
      "rule_id": "HIPAA_SF_001",
      "status": "pass",
      "evidence_chunk_ids": ["policy_chunk_123"],
      "rationale": "Patient names were successfully redacted per HIPAA Safe Harbor requirement. All instances replaced with [PATIENT_NAME] placeholder.",
      "confidence": 0.98,
      "document_excerpt_hash": "sha256:abc123...",
      "remediation_suggestion": null
    },
    {
      "rule_id": "HIPAA_SF_003",
      "status": "pass",
      "evidence_chunk_ids": ["policy_chunk_456"],
      "rationale": "Dates of birth and admission dates were redacted per HIPAA Safe Harbor requirement.",
      "confidence": 0.95,
      "document_excerpt_hash": "sha256:def456...",
      "remediation_suggestion": null
    },
    {
      "rule_id": "INT_DOC_001",
      "status": "fail",
      "evidence_chunk_ids": ["policy_chunk_789"],
      "rationale": "Document does not contain a clear History of Present Illness (HPI) section as required by internal documentation standards.",
      "confidence": 0.92,
      "document_excerpt_hash": "sha256:ghi789...",
      "remediation_suggestion": "Add a dedicated HPI section describing the patient's current condition and relevant history."
    }
  ],
  "overall_status": "fail",
  "risk_score": 0.65,
  "redaction_summary": {
    "total_redactions": 9,
    "phi_types_detected": ["patient_name", "date_of_birth", "mrn", "phone"],
    "placeholders_used": {
      "[PATIENT_NAME]": 5,
      "[DATE_OF_BIRTH]": 1,
      "[MRN]": 2,
      "[PHONE]": 1
    },
    "redaction_method": "safe_harbor"
  },
  "policy_versions_used": ["HIPAA_v1.0", "INT_DOC_v1.0"],
  "jurisdiction": "US_FEDERAL",
  "metadata": {
    "processing_time_seconds": 12.5,
    "model_used": "llama3.1:8b",
    "policy_chunks_retrieved": 8
  }
}
```

### 4.4 Status Determination Logic

**Overall Status**:
- `"pass"`: All findings are `"pass"`
- `"fail"`: Any finding is `"fail"`
- `"needs_review"`: No failures, but at least one `"needs_review"`

**Risk Score Calculation**:
```python
def calculate_risk_score(findings: List[Finding]) -> float:
    """
    Calculate overall risk score based on findings
    0.0 = low risk (all pass)
    1.0 = high risk (many failures)
    """
    if not findings:
        return 0.0
    
    fail_count = sum(1 for f in findings if f.status == "fail")
    needs_review_count = sum(1 for f in findings if f.status == "needs_review")
    avg_confidence = sum(1 - f.confidence for f in findings) / len(findings)
    
    # Weighted combination
    risk = (fail_count * 0.6 + needs_review_count * 0.3) / len(findings)
    risk = min(1.0, risk + avg_confidence * 0.2)
    
    return round(risk, 2)
```

---

## 5. Output 3: Human-Readable Audit Report

### 5.1 Purpose

Human-readable narrative report for compliance officers, auditors, and reviewers.

### 5.2 Format

**Primary Format**: Markdown (.md)

**Optional Format**: PDF (generated from Markdown)

### 5.3 Report Structure

```markdown
# MediGuard Compliance Audit Report

## Executive Summary

- **Document ID**: `550e8400-e29b-41d4-a716-446655440001`
- **Document Type**: Progress Note
- **Run ID**: `660e8400-e29b-41d4-a716-446655440000`
- **Timestamp**: January 20, 2026, 10:30:00 AM UTC
- **Overall Status**: ⚠️ FAIL
- **Risk Score**: 0.65 (Moderate Risk)

### Summary Statistics
- **Total Findings**: 3
- **Passed**: 2
- **Failed**: 1
- **Needs Review**: 0
- **Total PHI Redactions**: 9

---

## Compliance Findings

### ✅ HIPAA_SF_001: Patient Name Redaction (PASS)

**Status**: PASS  
**Confidence**: 98%

**Finding**: Patient names were successfully redacted per HIPAA Safe Harbor requirement. All instances replaced with `[PATIENT_NAME]` placeholder.

**Evidence**:
- Policy Section: HIPAA §164.514(b)(2) - Identifier #1 (Names)
- Policy Chunk: `policy_chunk_123`

**Document Excerpt** (Hash: `sha256:abc123...`):  
*[Redacted content reference - no PHI]*

---

### ✅ HIPAA_SF_003: Date Redaction (PASS)

**Status**: PASS  
**Confidence**: 95%

**Finding**: Dates of birth and admission dates were redacted per HIPAA Safe Harbor requirement.

**Evidence**:
- Policy Section: HIPAA §164.514(b)(2) - Identifier #3 (Dates)
- Policy Chunk: `policy_chunk_456`

---

### ❌ INT_DOC_001: History of Present Illness (FAIL)

**Status**: FAIL  
**Confidence**: 92%

**Finding**: Document does not contain a clear History of Present Illness (HPI) section as required by internal documentation standards.

**Evidence**:
- Policy Section: Internal Documentation Standards - Section 3.1
- Policy Chunk: `policy_chunk_789`

**Remediation Suggestion**:  
Add a dedicated HPI section describing the patient's current condition and relevant history.

---

## PHI Redaction Summary

### Redaction Method
- **Method**: Safe Harbor (HIPAA §164.514(b)(2))
- **Total Redactions**: 9

### PHI Types Detected
| PHI Type | Count |
|----------|-------|
| Patient Name | 5 |
| Date of Birth | 1 |
| Medical Record Number | 2 |
| Phone Number | 1 |

### Placeholder Usage
- `[PATIENT_NAME]`: 5 instances
- `[DATE_OF_BIRTH]`: 1 instance
- `[MRN]`: 2 instances
- `[PHONE]`: 1 instance

---

## Policy Versions Used

- **HIPAA**: v1.0 (Effective: 2024-01-01)
- **Internal Documentation Standards**: v1.0 (Effective: 2024-06-01)

**Jurisdiction**: US Federal

---

## Processing Metadata

- **Processing Time**: 12.5 seconds
- **Model Used**: llama3.1:8b
- **Policy Chunks Retrieved**: 8

---

## Recommendations

1. **Immediate Action Required**: Add History of Present Illness (HPI) section to document
2. **Review Recommended**: Document passes PHI redaction requirements but fails internal documentation standards
3. **Risk Assessment**: Moderate risk - document requires remediation before approval

---

*Report generated by MediGuard v1.0*  
*For questions, contact: compliance@organization.com*
```

### 5.4 Report Generation Rules

**Templates**:
- Use Markdown templates for consistency
- Support internationalization (future)
- Include organization branding (future)

**Styling**:
- ✅ Pass: Green checkmark
- ❌ Fail: Red X
- ⚠️ Needs Review: Yellow warning

---

## 6. Output 4: Routing Decision

### 6.1 Purpose

Automated workflow routing recommendation based on risk assessment.

### 6.2 Schema (Pydantic)

```python
from pydantic import BaseModel, Field
from typing import List, Literal

class RiskFactor(BaseModel):
    """Individual risk factor contributing to routing decision"""
    factor_type: str = Field(..., description="Type of risk factor (e.g., 'compliance_failure', 'low_confidence')")
    severity: Literal["low", "medium", "high"] = Field(..., description="Severity of the risk factor")
    description: str = Field(..., description="Description of the risk factor")
    rule_id: Optional[str] = Field(None, description="Related rule ID if applicable")

class RoutingDecision(BaseModel):
    """Automated routing decision"""
    run_id: UUID = Field(..., description="Run identifier")
    document_id: UUID = Field(..., description="Document identifier")
    route_action: Literal["auto_approve", "requires_review", "reject"] = Field(
        ..., 
        description="Recommended routing action"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence in routing decision (0.0-1.0)"
    )
    reason: str = Field(
        ..., 
        description="Human-readable explanation of routing decision"
    )
    risk_factors: List[RiskFactor] = Field(
        default_factory=list, 
        description="List of risk factors influencing decision"
    )
    threshold_info: dict = Field(
        default_factory=dict, 
        description="Threshold information (for transparency)"
    )
```

### 6.3 JSON Schema Example

```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_id": "660e8400-e29b-41d4-a716-446655440001",
  "route_action": "requires_review",
  "confidence": 0.88,
  "reason": "Document fails internal documentation standards (missing HPI section) but passes PHI redaction requirements. Requires human review for remediation.",
  "risk_factors": [
    {
      "factor_type": "compliance_failure",
      "severity": "medium",
      "description": "Document fails INT_DOC_001: Missing HPI section",
      "rule_id": "INT_DOC_001"
    },
    {
      "factor_type": "low_confidence",
      "severity": "low",
      "description": "One finding has confidence below 0.95 (0.92)",
      "rule_id": null
    }
  ],
  "threshold_info": {
    "auto_approve_threshold": 0.05,
    "requires_review_threshold": 0.30,
    "calculated_risk_score": 0.65
  }
}
```

### 6.4 Routing Logic

**Decision Rules**:

```python
def determine_route_action(
    overall_status: str,
    risk_score: float,
    findings: List[Finding],
    config: dict
) -> tuple[Literal["auto_approve", "requires_review", "reject"], str, List[RiskFactor]]:
    """
    Determine routing action based on compliance status and risk
    """
    risk_factors = []
    
    # Check for failures
    failures = [f for f in findings if f.status == "fail"]
    if failures:
        risk_factors.append(RiskFactor(
            factor_type="compliance_failure",
            severity="high" if len(failures) > 2 else "medium",
            description=f"{len(failures)} compliance rule(s) failed",
            rule_id=failures[0].rule_id if failures else None
        ))
    
    # Check risk score thresholds
    auto_approve_threshold = config.get("auto_approve_threshold", 0.05)
    requires_review_threshold = config.get("requires_review_threshold", 0.30)
    
    if overall_status == "pass" and risk_score <= auto_approve_threshold:
        return ("auto_approve", 
                "Document passes all compliance checks with low risk.",
                risk_factors)
    
    elif overall_status == "pass" and risk_score <= requires_review_threshold:
        risk_factors.append(RiskFactor(
            factor_type="elevated_risk",
            severity="low",
            description=f"Risk score ({risk_score}) exceeds auto-approve threshold",
            rule_id=None
        ))
        return ("requires_review",
                "Document passes compliance but has elevated risk. Recommend review.",
                risk_factors)
    
    elif overall_status == "fail":
        return ("requires_review",
                "Document has compliance failures. Requires human review and remediation.",
                risk_factors)
    
    else:  # needs_review or high risk
        return ("requires_review",
                "Document requires review due to ambiguous findings or high risk.",
                risk_factors)
```

---

## 7. Output Versioning

### 7.1 Versioning Strategy

**Schema Versioning**:
- Version numbers in API responses: `"output_version": "1.0"`
- Breaking changes increment major version
- Non-breaking additions increment minor version

**Example**:
```json
{
  "output_version": "1.0",
  "run_id": "...",
  ...
}
```

### 7.2 Backward Compatibility

**Principles**:
- Additive changes only (new optional fields)
- Deprecate fields before removing
- Version negotiation in API (future)

---

## 8. Success Criteria for Step 4

This outputs specification is complete when:
- [x] All four output types are documented with schemas
- [x] Pydantic models are defined for machine-readable outputs
- [x] JSON examples are provided
- [x] Report templates are specified
- [x] Routing logic is documented
- [x] Versioning strategy is defined

---

## 9. Next Steps

After outputs approval, proceed to:
- **Step 11**: Define canonical data model (implement Pydantic models from this spec)
- **Step 34**: Implement Compliance Matcher with structured outputs (use these schemas)

---

**Document Version**: 1.0  
**Last Updated**: Jan 20, 2026  
**Status**: Reviewed
