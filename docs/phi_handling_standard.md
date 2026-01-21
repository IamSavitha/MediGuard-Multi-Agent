# MediGuard: PHI Handling Standard

## Executive Summary

This document defines the PHI (Protected Health Information) handling standard that MediGuard will implement. We've chosen to build **Safe Harbor-first** with an extension point for Expert Determination, as this provides a solid foundation while maintaining flexibility for future requirements.

---

## 1. Decision: Safe Harbor First

### 1.1 Primary Standard: Safe Harbor Method

**Standard**: HIPAA De-identification via Safe Harbor Method (45 CFR §164.514(b)(2))

**Implementation Approach**: Build Safe Harbor implementation as the primary method, with architecture designed to support Expert Determination as an extension.

**Rationale**:
- **Simplicity**: Safe Harbor is rules-based and deterministic
- **Clear Requirements**: The 18 identifiers are explicitly defined
- **Lower Risk**: Easier to implement correctly and audit
- **Foundation**: Establishes patterns that can be extended for Expert Determination

### 1.2 Extension Point: Expert Determination

**Standard**: HIPAA De-identification via Expert Determination Method (45 CFR §164.514(b)(1))

**Implementation Approach**: Architecture will support Expert Determination workflows, but not implemented in v1.0

**Rationale**:
- **Flexibility**: Some use cases may require expert determination
- **Future-Proofing**: Design allows addition without major refactoring
- **Complexity**: Expert Determination requires risk assessment and documentation beyond v1.0 scope

---

## 2. Safe Harbor Method: Implementation Details

### 2.1 Overview

**Legal Basis**: 45 CFR §164.514(b)(2)

**Requirement**: Remove all 18 specified identifiers from the document

**Result**: Document is considered de-identified and no longer PHI under HIPAA

**Deterministic**: Either all 18 are removed (compliant) or not (non-compliant)

### 2.2 The 18 Identifiers - Implementation Mapping

Each identifier maps to specific detection and redaction logic:

| # | Identifier Type | Detection Method | Redaction Placeholder | Rule ID |
|---|----------------|------------------|----------------------|---------|
| 1 | Names | NLP/NER + Rules | `[PATIENT_NAME]` | HIPAA_SF_001 |
| 2 | Geographic subdivisions < state | Rules + NLP | `[CITY]`, `[ZIP_CODE]` | HIPAA_SF_002 |
| 3 | Dates (birth, death, service) | Regex + Rules | `[DATE_OF_BIRTH]`, `[ADMISSION_DATE]` | HIPAA_SF_003 |
| 4 | Telephone numbers | Regex | `[PHONE]` | HIPAA_SF_004 |
| 5 | Fax numbers | Regex | `[FAX]` | HIPAA_SF_005 |
| 6 | Email addresses | Regex | `[EMAIL]` | HIPAA_SF_006 |
| 7 | SSN | Regex + Validation | `[SSN]` | HIPAA_SF_007 |
| 8 | Medical Record Numbers | Regex + Context | `[MRN]` | HIPAA_SF_008 |
| 9 | Health Plan Beneficiary Numbers | Regex + Context | `[BENEFICIARY_ID]` | HIPAA_SF_009 |
| 10 | Account numbers | Regex + Context | `[ACCOUNT_NUMBER]` | HIPAA_SF_010 |
| 11 | Certificate/License numbers | Regex + Context | `[LICENSE_NUMBER]` | HIPAA_SF_011 |
| 12 | Vehicle identifiers | Regex + NLP | `[VEHICLE_ID]` | HIPAA_SF_012 |
| 13 | Device identifiers | Regex + NLP | `[DEVICE_ID]` | HIPAA_SF_013 |
| 14 | URLs | Regex | `[URL]` | HIPAA_SF_014 |
| 15 | IP addresses | Regex | `[IP_ADDRESS]` | HIPAA_SF_015 |
| 16 | Biometric identifiers | NLP + Context | `[BIOMETRIC_ID]` | HIPAA_SF_016 |
| 17 | Full face photographic images | Image processing (future) | `[PHOTO_IMAGE]` | HIPAA_SF_017 |
| 18 | Other unique identifiers | Rules + Context | `[UNIQUE_ID]` | HIPAA_SF_018 |

### 2.3 Special Cases and Edge Cases

#### 2.3.1 Geographic Subdivisions

**Rule**: All geographic subdivisions smaller than state must be removed

**Exception**: Initial 3 digits of ZIP code permitted if:
- The geographic unit formed by combining all ZIP codes with the same initial three digits contains more than 20,000 people
- The initial three digits of a ZIP code for all such geographic units containing 20,000 or fewer people is changed to 000

**Implementation**: 
- Redact all city names, street addresses, county names
- Check ZIP code population before redacting (requires reference data)
- Default: redact all ZIP codes for safety

#### 2.3.2 Dates

**Rule**: All dates directly related to an individual must be removed

**Included**:
- Date of birth
- Date of death
- Date of admission
- Date of discharge
- Date of service
- Ages over 89 (considered dates)

**Exception**: Year only (not specific dates)
- ✅ "In 1995, the patient..."
- ❌ "On January 15, 1995, the patient..."

**Implementation**:
- Redact all specific dates (MM/DD/YYYY, DD-MM-YYYY, etc.)
- Redact ages > 89 (replace with `[AGE_89_PLUS]`)
- Allow year-only references to pass

#### 2.3.3 Ages Over 89

**Rule**: Ages over 89 and elements of dates (except year) indicative of such age must be redacted

**Rationale**: Ages 90+ combined with other data could identify individuals

**Implementation**:
- Detect ages > 89: "90 years old", "age 92", "95-year-old"
- Replace with: `[AGE_89_PLUS]`

### 2.4 Detection Strategy (Multi-Layer)

#### Layer 1: Deterministic Rules (Regex)
- **Purpose**: Fast, cheap, high-precision detection
- **Coverage**: Phone numbers, emails, SSNs, dates, IP addresses, URLs
- **False Positives**: Possible, but safe to over-redact
- **Example**: `\b\d{3}-\d{2}-\d{4}\b` for SSN

#### Layer 2: NLP/NER (Named Entity Recognition)
- **Purpose**: Contextual detection of names, locations, organizations
- **Coverage**: Person names, geographic entities, clinical entity names
- **False Positives**: Medication names may be flagged as names
- **Example**: Spacy `en_core_web_sm` or clinical NER model

#### Layer 3: LLM-Based Detection (Targeted)
- **Purpose**: Catch missed PHI in uncertain segments
- **Coverage**: Contextual identifiers like "patient's daughter Emily..."
- **When Used**: Only for segments where rules/NER disagree or low confidence
- **Cost**: Higher, so used sparingly
- **Example**: GPT-4o with structured outputs for PHI spans

### 2.5 Redaction Strategy

#### 2.5.1 Typed Placeholders

**Approach**: Replace PHI with typed placeholders that preserve:
- **Grammar**: Placeholder type indicates what was removed
- **Structure**: Compliance rules can reference "a date exists" without leaking it
- **Auditability**: Clear record of what was redacted

**Placeholder Format**: `[IDENTIFIER_TYPE]`

**Examples**:
- `John Smith` → `[PATIENT_NAME]`
- `01/15/1985` → `[DATE_OF_BIRTH]`
- `555-123-4567` → `[PHONE]`
- `john.doe@example.com` → `[EMAIL]`

#### 2.5.2 Reversible Mapping (Optional)

**Design Decision**: Store mapping of placeholder → original value

**Use Case**: 
- Allows "un-redaction" for authorized users
- Enables validation that original structure is preserved
- Supports audit trails

**Security**: 
- Mapping stored separately with encryption
- Access controlled and logged
- Only available to authorized personnel

**Implementation**: 
- For v1.0: Basic placeholder replacement (non-reversible)
- For v2.0: Add reversible mapping for authorized use cases

### 2.6 Validation Rules

#### 2.6.1 Pre-Redaction Validation

**Checks**:
- Document is parseable
- Document type is recognized
- No obvious formatting issues that would break detection

#### 2.6.2 Post-Redaction Validation (Leakage Check)

**Critical Gate**: Re-run all detectors on redacted output

**Requirement**: **Zero PHI in redacted output** (fail-closed)

**Actions if PHI Detected**:
1. **Block the document**: Do not proceed to compliance checking
2. **Log the failure**: Record which PHI was detected (sanitized log)
3. **Alert operator**: Flag for manual review
4. **Return error**: Inform user that redaction failed

**Rationale**: Safety > convenience. False positives are acceptable.

---

## 3. Expert Determination Method (Extension Point)

### 3.1 Overview

**Legal Basis**: 45 CFR §164.514(b)(1)

**Requirement**: A person with appropriate knowledge and experience determines that the risk of re-identification is very small

**Process**: 
1. Risk assessment methodology
2. Documentation of methodology and results
3. Expert's written statement
4. Periodic re-assessment

### 3.2 Why Not v1.0?

**Complexity**:
- Requires risk assessment methodology
- Needs statistical analysis of re-identification risk
- Requires expert attestation workflow
- Ongoing re-assessment process

**Scope**:
- Beyond the scope of an initial prototype
- Would require additional expertise (statistics, risk assessment)
- More suited for v2.0 after Safe Harbor is proven

### 3.3 Architecture for Future Support

**Extension Points Designed**:

1. **Pluggable De-identification Methods**:
   ```python
   class DeidentificationMethod(ABC):
       def deidentify(self, document: Document) -> RedactedDocument:
           ...
   ```

2. **Method Selection**:
   - User specifies method at document submission
   - System routes to appropriate method
   - Both methods can coexist

3. **Expert Determination Workflow**:
   - Risk assessment module (future)
   - Expert review interface (future)
   - Attestation and documentation (future)

---

## 4. Implementation Priorities

### Phase 1 (v1.0 - Current)
1. ✅ Safe Harbor Method - All 18 identifiers
2. ✅ Multi-layer detection (Rules + NER + targeted LLM)
3. ✅ Typed placeholder redaction
4. ✅ Post-redaction leakage check (fail-closed)

### Phase 2 (v2.0 - Future)
- Expert Determination workflow
- Reversible redaction mapping
- Risk assessment methodology
- Expert attestation interface

---

## 5. Decision Rationale Summary

### Why Safe Harbor First?

**Advantages**:
- ✅ **Deterministic**: Clear pass/fail criteria
- ✅ **Auditable**: Easy to verify compliance
- ✅ **Fast to Implement**: Rules-based approach
- ✅ **Lower Risk**: Well-defined requirements
- ✅ **Testable**: Easy to create test cases

**Tradeoffs**:
- ⚠️ **Less Flexible**: Can't retain some identifiers even with low risk
- ⚠️ **May Over-Redact**: Some dates/identifiers might be safe but must be removed
- ⚠️ **Clinical Impact**: Removing dates can reduce clinical utility

**Mitigation**:
- Use typed placeholders to preserve structure
- Allow Expert Determination for specific use cases (v2.0)
- Document limitations clearly

### Why Not Expert Determination First?

**Challenges**:
- ❌ **Complex**: Requires risk assessment methodology
- ❌ **Subjective**: Depends on expert judgment
- ❌ **Harder to Audit**: Need to validate methodology
- ❌ **Slower**: Requires expert review process

**Future Path**:
- Build Safe Harbor first to establish foundation
- Design architecture to support both methods
- Add Expert Determination when use cases demand it

---

## 6. Success Criteria for Step 3

This PHI handling standard selection is complete when:
- [x] Safe Harbor method is chosen as primary standard
- [x] Implementation details for all 18 identifiers are documented
- [x] Multi-layer detection strategy is defined
- [x] Redaction approach (typed placeholders) is specified
- [x] Post-redaction validation (leakage check) is designed
- [x] Expert Determination extension point is documented
- [x] Rationale for Safe Harbor-first is clear

---

## 7. Next Steps

After PHI handling standard approval, proceed to:
- **Step 4**: Define outputs (contract with users) - expand on the output schemas
- **Step 24-29**: Implement PHI detection and redaction (actual code)

---

## References

- [HHS - Methods for De-identification of PHI](https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html)
- 45 CFR §164.514 - Standards for De-identification of Protected Health Information

---

**Document Version**: 1.0  
**Last Updated**: Jan 20, 2026  
**Status**: Reviewed 
