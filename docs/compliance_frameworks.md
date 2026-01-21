# MediGuard: Compliance Frameworks and Jurisdictions

## Executive Summary

This document defines the compliance frameworks and jurisdictions that MediGuard will support in v1.0. We're starting with a focused set (1-2 frameworks) to ship faster and establish a solid foundation before expanding.

---

## 1. Framework Selection Strategy

### Approach
- **Start Small**: Begin with 1-2 frameworks to establish patterns
- **Version Everything**: All policies are versioned with effective dates
- **Metadata Filtering**: Use jurisdiction, effective date, and policy version for precise retrieval
- **Expand Later**: Add more frameworks once the foundation is proven

### Rationale
Supporting multiple jurisdictions early complicates metadata and conflict resolution. We'll build the infrastructure to support expansion, but focus on depth in v1.0.

---

## 2. Primary Framework: HIPAA De-identification (Safe Harbor Method)

### 2.1 Framework Details

**Full Name**: Health Insurance Portability and Accountability Act (HIPAA) - De-identification via Safe Harbor Method

**Regulation**: 45 CFR §164.514(b)(2) - Standards for De-identification of Protected Health Information

**Source**: U.S. Department of Health and Human Services (HHS)

**Method**: Safe Harbor - Removal of 18 specified identifiers

**Applicability**: All documents containing PHI that need to be de-identified

**Effective Date**: Policy effective as of [To be set when policy documents are ingested]

### 2.2 The 18 Identifiers (Safe Harbor Requirements)

For de-identification, all of the following must be removed:

1. **Names**: Patient, relatives, employers, household members
2. **Geographic Subdivisions**: All geographic subdivisions smaller than state
   - Exception: Initial 3 digits of ZIP if population > 20,000
3. **Dates**: All dates directly related to an individual
   - Dates of birth, death, admission, discharge, service
   - Ages over 89 are considered dates and must be redacted
   - Exception: Year only (not specific dates)
4. **Telephone Numbers**: All telephone numbers
5. **Fax Numbers**: All fax numbers
6. **Email Addresses**: All email addresses
7. **Social Security Numbers**: All SSNs
8. **Medical Record Numbers**: All MRNs and health plan numbers
9. **Health Plan Beneficiary Numbers**: All beneficiary numbers
10. **Account Numbers**: All account numbers
11. **Certificate/License Numbers**: All certificate/license numbers
12. **Vehicle Identifiers**: Serial numbers, license plate numbers
13. **Device Identifiers**: Serial numbers, identifiers
14. **Web Universal Resource Locators (URLs)**: All URLs
15. **Internet Protocol (IP) Addresses**: All IP addresses
16. **Biometric Identifiers**: Fingerprints, voiceprints, retinal patterns
17. **Full Face Photographic Images**: Any comparable images
18. **Other Unique Identifying Numbers**: Any other unique identifier

### 2.3 Policy Structure

Each HIPAA policy chunk will include:
- **Policy ID**: `HIPAA_164514b_3.10` (regulation section reference)
- **Policy Family**: `HIPAA`
- **Jurisdiction**: `US_FEDERAL`
- **Effective Date**: `YYYY-MM-DD`
- **Version**: `1.0`, `2.0`, etc.
- **Section Title**: Descriptive title
- **Policy Text**: The actual requirement text
- **Identifier Type**: Which of the 18 identifiers this covers
- **Compliance Rule ID**: Machine-readable rule identifier (e.g., `HIPAA_SF_001`)

### 2.4 Compliance Rules

Each of the 18 identifiers will map to one or more compliance rules:

```
HIPAA_SF_001: Remove patient names
HIPAA_SF_002: Remove geographic subdivisions < state level
HIPAA_SF_003: Remove dates (birth, death, admission, discharge, service)
HIPAA_SF_004: Remove telephone numbers
HIPAA_SF_005: Remove fax numbers
HIPAA_SF_006: Remove email addresses
HIPAA_SF_007: Remove SSNs
HIPAA_SF_008: Remove MRNs
HIPAA_SF_009: Remove health plan beneficiary numbers
HIPAA_SF_010: Remove account numbers
HIPAA_SF_011: Remove certificate/license numbers
HIPAA_SF_012: Remove vehicle identifiers
HIPAA_SF_013: Remove device identifiers
HIPAA_SF_014: Remove URLs
HIPAA_SF_015: Remove IP addresses
HIPAA_SF_016: Remove biometric identifiers
HIPAA_SF_017: Remove full face photographic images
HIPAA_SF_018: Remove other unique identifying numbers
```

---

## 3. Secondary Framework: Internal Documentation Checklist

### 3.1 Framework Details

**Full Name**: Internal Clinical Documentation Standards

**Type**: Organization-specific compliance requirements

**Source**: [To be defined - internal policy documents]

**Purpose**: Ensure clinical documents meet internal quality and completeness standards

**Applicability**: All clinical documentation types

**Effective Date**: [To be set when policy documents are ingested]

### 3.2 Common Requirements (Examples)

**Note**: These are examples - actual requirements will come from internal policy documents.

#### 3.2.1 Required Sections

- **INT_DOC_001**: Document must contain History of Present Illness (HPI) section
- **INT_DOC_002**: Document must contain Assessment section
- **INT_DOC_003**: Document must contain Plan section
- **INT_DOC_004**: Document must contain signature/author information

#### 3.2.2 Content Requirements

- **INT_DOC_005**: HPI must be at least [N] characters or sentences
- **INT_DOC_006**: Assessment must include diagnosis or clinical impression
- **INT_DOC_007**: Plan must include actionable next steps or recommendations

#### 3.2.3 Format Requirements

- **INT_DOC_008**: Document must include date of service
- **INT_DOC_009**: Document must include patient identifier (if not redacted)
- **INT_DOC_010**: Document must be signed/attested

### 3.3 Policy Structure

Each internal policy chunk will include:
- **Policy ID**: `INT_DOC_XXX` (internal rule identifier)
- **Policy Family**: `INTERNAL_DOCUMENTATION`
- **Jurisdiction**: `INTERNAL` (or specific org identifier)
- **Effective Date**: `YYYY-MM-DD`
- **Version**: `1.0`, `2.0`, etc.
- **Section Title**: Descriptive title
- **Policy Text**: The actual requirement text
- **Document Type Applicability**: Which document types this rule applies to
- **Compliance Rule ID**: Machine-readable rule identifier

---

## 4. Policy Versioning Strategy

### 4.1 Version Numbering

- **Format**: `MAJOR.MINOR.PATCH`
  - `MAJOR`: Breaking changes to rule interpretation
  - `MINOR`: New requirements or clarifications
  - `PATCH`: Typo fixes, formatting changes
- **Examples**: `1.0.0`, `1.1.0`, `1.1.1`

### 4.2 Effective Dates

- Each policy version has an `effective_date` (ISO 8601: `YYYY-MM-DD`)
- Policies can be backdated for historical compliance checks
- Only policies with `effective_date <= document_date` are applicable

### 4.3 Retrieval Filtering

When retrieving policies for a document:
```python
filters = {
    "jurisdiction": ["US_FEDERAL"],  # or ["INTERNAL"]
    "effective_date": {"$lte": document_date},
    "policy_family": ["HIPAA"]  # or ["INTERNAL_DOCUMENTATION"]
}
```

### 4.4 Policy Deprecation

- Policies can be marked as `deprecated: true`
- Deprecated policies are not retrieved for new documents
- Historical documents continue to reference the version that was effective at that time

---

## 5. Metadata Schema for Policies

### 5.1 Required Metadata Fields

```python
{
    "policy_id": str,              # e.g., "HIPAA_164514b_3.10"
    "policy_family": str,          # "HIPAA" | "INTERNAL_DOCUMENTATION"
    "jurisdiction": str,           # "US_FEDERAL" | "INTERNAL" | "US_CA" | etc.
    "effective_date": str,         # "YYYY-MM-DD"
    "version": str,                # "1.0.0"
    "section_title": str,          # Human-readable title
    "rule_id": str,                # Machine-readable rule ID
    "applicable_doc_types": list,  # ["progress_note", "discharge_summary", ...]
    "deprecated": bool,            # false
    "source_url": str,             # URL to original policy document
    "chunk_index": int             # Position in source document
}
```

### 5.2 Pinecone Metadata Filtering

These metadata fields enable:
- **Jurisdiction filtering**: Only retrieve relevant jurisdiction policies
- **Date filtering**: Only retrieve policies effective for the document date
- **Document type filtering**: Only retrieve policies applicable to this document type
- **Version control**: Ensure we're using the correct policy version

---

## 6. Conflict Resolution Strategy (Future)

### 6.1 Current Approach (v1.0)

- **Single Jurisdiction Focus**: Each document is checked against one primary jurisdiction
- **No Conflicts**: Start with frameworks that don't conflict (HIPAA is federal baseline)

### 6.2 Future Expansion (v2.0+)

When multiple jurisdictions apply:
- **Precedence Rules**: Define which framework takes precedence (e.g., federal > state)
- **Strictest Rule**: Apply the most restrictive requirement when rules conflict
- **Conflict Flagging**: Flag documents where multiple jurisdictions have conflicting requirements for human review

---

## 7. Implementation Priorities

### Phase 1 (v1.0 - Current)
1. ✅ HIPAA Safe Harbor - All 18 identifiers
2. ✅ Internal Documentation Checklist - Core requirements

### Phase 2 (v2.0 - Future)
- Expert Determination method (HIPAA alternative)
- State-specific regulations (CA, NY, etc.)
- International regulations (GDPR, etc.)

---

## 8. Policy Sources and Ingestion

### 8.1 HIPAA Sources

**Primary Source**: 
- HHS.gov - Methods for De-identification of PHI
- URL: https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html

**Additional Sources**:
- 45 CFR §164.514 (official regulation text)
- HHS Guidance Documents

### 8.2 Internal Policy Sources

**To Be Determined**:
- Internal policy documents (PDF/HTML/text)
- Organization's compliance handbook
- Clinical documentation standards

### 8.3 Ingestion Process (To Be Built)

1. Collect policy documents → `policies/hipaa/`, `policies/internal/`
2. Normalize to clean text with stable section IDs
3. Chunk by section headers + token windows
4. Embed chunks
5. Upsert to Pinecone with metadata

---

## 9. Success Criteria for Step 2

This compliance framework selection is complete when:
- [x] Primary framework (HIPAA Safe Harbor) is fully documented
- [x] Secondary framework (Internal Documentation) is defined
- [x] Policy versioning strategy is established
- [x] Metadata schema for filtering is defined
- [x] Conflict resolution approach is documented (even if deferred)
- [x] Policy sources are identified

---

## 10. Next Steps

After framework approval, proceed to:
- **Step 3**: Choose PHI handling standard (expand on Safe Harbor implementation details)
- **Step 12**: Collect policy content and version it (set up policy ingestion)

---

**Document Version**: 1.0  
**Last Updated**: Jan 20, 2026  
**Status**: Draft - Awaiting Review
